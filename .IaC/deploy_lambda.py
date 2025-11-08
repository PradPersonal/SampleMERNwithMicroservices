# deploy_lambda.py
import boto3
import time

s3 = boto3.client('s3', region_name='ca-central-1')
lambda_client = boto3.client('lambda', region_name='ca-central-1')

# --- Configuration Placeholders (Update these values) ---
S3_BUCKET_NAME = 'your-unique-db-backup-bucket-name' # Must be globally unique
LAMBDA_ROLE_ARN = 'arn:aws:iam::123456789012:role/LambdaDBBackupRole' # Role with S3 & RDS permissions
# --------------------------------------------------------

def create_s3_bucket(bucket_name):
    print(f"Creating S3 bucket {bucket_name}...")
    try:
        s3.create_bucket(Bucket=bucket_name)
        print("S3 bucket created.")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print("S3 bucket already exists.")

def deploy_lambda_function(role_arn):
    print("Deploying Lambda function for DB backup...")
    try:
        with open('lambda_function.zip', 'rb') as f:
            zip_file_bytes = f.read()

        response = lambda_client.create_function(
            FunctionName='DBBackupFunction',
            Runtime='python3.8',
            Role=role_arn,
            Handler='lambda_function.lambda_handler', # Assumes the entry point is lambda_function.py, handler function 'lambda_handler'
            Code={'ZipFile': zip_file_bytes},
            Description='Backs up RDS database to S3 with timestamp',
            Timeout=120
        )
        print(f"Lambda function 'DBBackupFunction' created/updated.")
        return response['FunctionArn']

    except FileNotFoundError:
        print("Error: lambda_function.zip not found. Please create the deployment package first.")
        return None
    except Exception as e:
        # Handle update_function for subsequent runs if needed
        print(f"An error occurred during Lambda deployment: {e}")

if __name__ == "__main__":
    print("Run this script via the main orchestrator script.")
