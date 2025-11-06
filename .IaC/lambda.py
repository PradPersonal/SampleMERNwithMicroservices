import boto3
import json
import zipfile
import os

lambda_client = boto3.client('lambda', region_name='ca-central-1')
iam_client = boto3.client('iam', region_name='ca-central-1')

# --- IAM Role for Lambda ---
def create_lambda_iam_role():
    role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    try:
        role = iam_client.create_role(
            RoleName='LambdaBasicExecutionRole',
            AssumeRolePolicyDocument=json.dumps(role_policy),
            Description='Basic execution role for Lambda'
        )
        # Attach the basic execution policy
        iam_client.attach_role_policy(
            RoleName='LambdaBasicExecutionRole',
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        print("IAM Role created for Lambda.")
        return role['Role']['Arn']
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("IAM Role already exists. Reusing existing role.")
            return iam_client.get_role(RoleName='LambdaBasicExecutionRole')['Role']['Arn']
        else:
            raise e

# --- Lambda Function Code (lambda_function.py) ---
LAMBDA_CODE = """
import json

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from a Boto3 provisioned Lambda!')
    }
"""

# --- Create Zip File for Lambda Deployment ---
def create_lambda_zip(filename='lambda_function.zip'):
    with open('lambda_function.py', 'w') as f:
        f.write(LAMBDA_CODE)
    with zipfile.ZipFile(filename, 'w') as zipf:
        zipf.write('lambda_function.py')
    os.remove('lambda_function.py')
    with open(filename, 'rb') as f:
        return f.read()

# --- Lambda Function Creation ---
def create_lambda_function(role_arn, zip_file_bytes):
    try:
        response = lambda_client.create_function(
            FunctionName='MyMicroserviceLambda',
            Runtime='python3.8',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_file_bytes},
            Description='A microservice Lambda function created with Boto3'
        )
        print(f"Lambda function created: {response['FunctionName']}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceConflictException':
            print("Lambda function already exists. Skipping creation.")
        else:
            raise e

# Combine the calls in a main function
if __name__ == "__main__":
    role_arn = create_lambda_iam_role()
    zip_bytes = create_lambda_zip()
    create_lambda_function(role_arn, zip_bytes)
