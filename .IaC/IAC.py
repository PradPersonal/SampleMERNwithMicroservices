import boto3
import base64
import time

# --- Configuration Data ---
REGION = 'ca-central-1'
IAM_INSTANCE_PROFILE_ARN = 'arn:aws:iam::975050024946:role/ecr-access-role-prad'
ECR_REPO_URL = '975050024946.dkr.ecr.ca-central-1.amazonaws.com'
DOCKER_IMAGE_NAME_TAG = 'ecr-prad:latest' # Assuming the repo name is 'ecr-prad' and tag is 'latest'
SUBNET_ID = 'subnet-0c723f27934f0860c'
SECURITY_GROUP_ID = 'sg-066a646544faa4751'
AMI_ID = 'ami-0abac8735a38475db' # Amazon Linux AMI in ca-central-1

LAUNCH_TEMPLATE_NAME = 'BackendDockerLaunchTemplatePrad'
ASG_NAME = 'BackendASGDockerPrad'

# --- Boto3 Clients ---
ec2_client = boto3.client('ec2', region_name=REGION)
autoscaling_client = boto3.client('autoscaling', region_name=REGION)

def get_user_data_script():
    """
    Generates the base64 encoded user data script for EC2 instances.
    This script installs Docker, logs into ECR, pulls the image, and runs the container.
    """
    # The EC2 instance must have the 'ecr-access-role-prad' IAM role attached to successfully run the 'aws ecr get-login-password' command.
    user_data = f"""#!/bin/bash
    sudo yum update -y
    sudo yum install -y docker aws-cli
    sudo service docker start
    sudo usermod -a -G docker ec2-user
    sudo systemctl enable docker
    
    # ECR Login using instance profile credentials
    aws ecr get-login-password --region {REGION} | docker login --username AWS --password-stdin {ECR_REPO_URL}

    # Pull and run the Docker image
    docker pull {ECR_REPO_URL}/{DOCKER_IMAGE_NAME_TAG}
    docker run -d -p 80:80 {ECR_REPO_URL}/{DOCKER_IMAGE_NAME_TAG}
    """
    # Boto3 requires user data to be base64 encoded
    return base64.b64encode(user_data.encode("utf-8")).decode("utf-8")

def create_launch_template(user_data):
    """
    1. Creates a Launch Template with the Docker configuration.
    """
    print(f"Creating Launch Template: {LAUNCH_TEMPLATE_NAME}...")
    try:
        response = ec2_client.create_launch_template(
            LaunchTemplateName=LAUNCH_TEMPLATE_NAME,
            LaunchTemplateData={
                'ImageId': AMI_ID,
                'InstanceType': 't2.micro', # Adjusted to a common type, modify as needed
                'SecurityGroupIds': [SECURITY_GROUP_ID],
                'UserData': user_data,
                'IamInstanceProfile': {
                    'Arn': IAM_INSTANCE_PROFILE_ARN 
                }
            }
        )
        lt_id = response['LaunchTemplate']['LaunchTemplateId']
        print(f"Launch Template created successfully. ID: {lt_id}")
        return lt_id
    except Exception as e:
        print(f"Error creating Launch Template: {e}")
        # If template exists, try to get its ID (simplified error handling)
        if "already exists" in str(e):
             templates = ec2_client.describe_launch_templates(LaunchTemplateNames=[LAUNCH_TEMPLATE_NAME])
             return templates['LaunchTemplates'][0]['LaunchTemplateId']
        return None

def create_auto_scaling_group(launch_template_id):
    """
    2. Creates an Auto Scaling Group using the defined Launch Template.
    3. Launches instances that automatically run the Docker application.
    """
    print(f"Creating Auto Scaling Group: {ASG_NAME}...")
    try:
        autoscaling_client.create_auto_scaling_group(
            AutoScalingGroupName=ASG_NAME,
            LaunchTemplate={
                'LaunchTemplateId': launch_template_id,
                'Version': '$Latest'
            },
            MinSize=1,
            MaxSize=3,
            DesiredCapacity=1,
            VPCZoneIdentifier=SUBNET_ID, # Boto3 accepts a comma-separated list or single string
            Tags=[
                {'Key': 'Name', 'Value': 'BackendDockerInstancePrad', 'PropagateAtLaunch': True}
            ]
        )
        print(f"Auto Scaling Group '{ASG_NAME}' created successfully.")
        print("Instances are now launching and running the Dockerized application via User Data.")
    except Exception as e:
        print(f"Error creating Auto Scaling Group: {e}")

if __name__ == "__main__":
    # Ensure Docker Image Tag is correct before running
    # print(f"Ensuring IAM Role {IAM_INSTANCE_PROFILE_ARN} has ECR access policies attached...")
    
    user_data = get_user_data_script()
    launch_template_id = create_launch_template(user_data)
    
    if launch_template_id:
        # Give AWS a moment to ensure the template is fully available for ASG creation
        time.sleep(5) 
        create_auto_scaling_group(launch_template_id)
    else:
        print("Could not proceed with ASG creation without a valid Launch Template ID.")
