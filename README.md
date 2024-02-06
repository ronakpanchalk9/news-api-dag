# NewsAPI Articles DAG

## Description
Created this pipeline which orchestrates a daily ETL pipeline for news data using Python. Utilizing the News API, it fetches top headlines, cleans, and transforms the data. The processed information is then uploaded to AWS S3 using Boto3. The DAG runs daily, with error retries and email notifications configured.

## Setup
1. **Check Python version**
  - Make sure `Python 3.11.5` is installed
  - To check your python version.
  ```bash
  python -V
  ```
2. **Install dependencies**
   - Use the `requirements.txt` file to install all required dependencies.
     
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Docker Desktop**
   - Pull my docker Images from the `ronakpanchalk9/ronak-news-api` repository on DockerHub. Using:
     
     ```bash
     docker pull ronakpanchalk9/ronak-news-api
     ```
   - Run the `docker-compose.yaml` file,
     
    ```bash
    docker-compose up -d
    ```
4. **Config file**
   - Create a `config.ini` file and store it in the same directory and insert the variables in it
     ```
     ; config.ini
      [api]
      api_key = [Enter the API key here]
      
      [storage]
      region_name = [Enter the region name]
      aws_access_key_id = [Enter your access key]
      aws_secret_access_key = [Enter your Secret access key]
      bucket_name = [Enter your bucket name]
     ```

## Workflow
The DAG is designed to run daily, triggered by Airflow's scheduler. The process begins by fetching news data from the News API, followed by cleaning and transforming the data using pandas. The final step involves uploading the processed data to an AWS S3 bucket, ensuring a secure and scalable storage solution.

## Why this Pipeline:

Automation: The daily scheduling ensures a consistent and automated flow of fresh news data, eliminating the need for manual intervention.

Scalability: Leveraging AWS S3 provides scalable storage, accommodating growing datasets with ease.

Flexibility: Airflow's DAG structure allows easy modification and expansion of the pipeline, adapting to evolving requirements.

Error Handling: Robust error-handling mechanisms are integrated into each step, providing insights into any issues that may arise during data retrieval, transformation, or upload.
