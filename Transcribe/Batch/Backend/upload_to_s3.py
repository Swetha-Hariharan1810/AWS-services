import boto3
from config import region_name, bucket
import os
import pathlib as path

def upload_to_s3(file_name):
    s3_client = boto3.client('s3', region_name=region_name)

    try:
        file_id = os.path.basename(file_name)
        s3_client.upload_file(file_name, bucket, file_id)
        print(f'Successfully uploaded {file_name} to S3 bucket {bucket} with key {file_id}')
        file_uri = f's3://{bucket}/{file_id}'
        return file_uri
    except Exception as e:
        print(f'Error uploading {file_id} to S3 bucket {bucket}: {str(e)}')
        return False
