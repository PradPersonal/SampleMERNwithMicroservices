# deploy_frontend.py
import boto3

ec2 = boto3.client('ec2', region_name='ca-central-1')

# --- Configuration Placeholders (Update these values) ---
AMI_ID = 'ami-0abcdef1234567890' # Replace with valid AMI ID (e.g., Amazon Linux 2)
INSTANCE_TYPE = 't2.micro'
KEY_NAME = 'your-key-pair-name'
USER_DATA_SCRIPT_FRONTEND = """#!/bin/bash
yum update -y
amazon-linux-extras install docker -y
service docker start
usermod -a -G docker ec2-user
docker run -d -p 80:80 your-dockerhub-user/frontend-image:latest
"""
# --------------------------------------------------------

def deploy_frontend_ec2(frontend_sg_id, pub_subnet_id, ec2_instance_profile_arn):
    print("Deploying Frontend EC2 instance...")
    
    # Launch instance in a public subnet
    instance = ec2.run_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        MinCount=1, MaxCount=1,
        KeyName=KEY_NAME,
        SecurityGroupIds=[frontend_sg_id],
        SubnetId=pub_subnet_id, # Requires one specific public subnet ID
        UserData=USER_DATA_SCRIPT_FRONTEND,
        IamInstanceProfile={'Arn': ec2_instance_profile_arn},
        TagSpecifications=[
            {'ResourceType': 'instance', 'Tags': [{'Key': 'Name', 'Value': 'FrontendInstance'}]}
        ]
    )
    instance_id = instance['Instances'][0]['InstanceId']
    print(f"Frontend instance launched: {instance_id}")
    return instance_id

if __name__ == "__main__":
    print("Run this script via the main orchestrator script.")
