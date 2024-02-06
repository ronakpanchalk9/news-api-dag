# Import necessary libraries and modules
from airflow.decorators import dag, task
from datetime import datetime, timedelta
import boto3
import pandas as pd
import numpy as np
import os
import requests
from configparser import ConfigParser
import logging

# Load configuration from the config.ini file
config = ConfigParser()
config.read('dags/config.ini')

# Retrieve configuration values
api_key = config.get('api', 'api_key')
region_name = config.get('storage', 'region_name')
aws_access_key_id = config.get('storage', 'aws_access_key_id')
aws_secret_access_key = config.get('storage', 'aws_secret_access_key')
bucket_name = config.get('storage', 'bucket_name')

# Get the current date and time in the specified format
curr_time = datetime.now()
curr_time = curr_time.strftime('%Y-%m-%d')

# Get the directory of the DAG file
dag_folder = os.path.dirname(os.path.abspath(__file__))

# Create a file path using the current date for the news data CSV file, to make it easier to distinguish daily outputs
file_path = os.path.join(dag_folder,f'{str(curr_time)}_news_data.csv')

# Define default arguments for the Airflow DAG
default_args = {
    'owner':'ronakpanchalk9',
    'retries':2,
    'retry_delay':timedelta(minutes=1),
    'email':['ronakbadmash12@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
}

#  Define the Airflow DAG using the @dag decorator
@dag(
    dag_id= 'news_api_dag',
    default_args= default_args,
    start_date= datetime(2024,2,6),
    schedule_interval= '@daily'
)

# Define the main function for the DAG
def api_etl():
    # Define a task to retrieve data from the News API
    @task
    def data_from_API(api_key):
        try:
            url = ('https://newsapi.org/v2/top-headlines?'
            f'country=us&'
            f'apiKey={api_key}')
            response = requests.get(url)
            news_data = response.json()
            return news_data
        except Exception as e:
            raise Exception(f"Found Error in data_from_API: {str(e)}")

    
    # Define a task to clean and transform the retrieved news data
    @task
    def cleaning_and_transforming(news_data, curr_time, file_path):
        logging.info(f"Total Results: {news_data['totalResults']}")
        if (news_data['totalResults']==0):
            logging.warning("No news articles found based on the specified criteria.")
        else:
            try:
                df = pd.DataFrame(news_data['articles'])
                df['source_id'] = df['source'].map(lambda x: x['id'])
                df['source'] = df['source'].map(lambda x: x['name'])
                df = df[~(df['source']=='[Removed]')&~(df['publishedAt']=='1970-01-01T00:00:00Z')].reset_index(drop=True)
                df['inserted_in_db_date'] = curr_time
                df['published_Date']=df['publishedAt'].map(lambda x: x.split('T')[0])
                df.drop('publishedAt',axis=1,inplace=True)
                df.to_csv(file_path, index=False)
            except Exception as e:
                raise Exception(f"Found Error in cleaning_and_transforming: {str(e)}")

    # Define a task to upload the cleaned and transformed data to AWS S3
    @task
    def uploading_aws(curr_time, file_path, region_name, aws_access_key_id, aws_secret_access_key):
        s3 = boto3.resource(
            service_name='s3',
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
            )
        s3.Bucket('wizikey1').upload_file(Filename= file_path, Key= str(curr_time)+'_headlines.csv')

    # Call the data_from_API task to get news data
    df = data_from_API(api_key)

     # Call the cleaning_and_transforming task to clean and transform the data
    cnt = cleaning_and_transforming(df, curr_time, file_path) 

    # Call the uploading_aws task to upload the data to AWS S3
    uas = uploading_aws(curr_time, file_path, region_name, aws_access_key_id, aws_secret_access_key)

    # Set the task dependencies
    cnt >> uas

# Create an instance of the DAG
complete_ETL = api_etl()
