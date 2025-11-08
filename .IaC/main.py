# full_deployment_script.py
import subprocess
import sys
import time
import os

# Import the child modules
import infra_setup
import deploy_backend
import deploy_frontend
import deploy_lambda

# --- Global Configuration/Placeholders (Centralize these if possible) ---
# Ensure these match or are consistent with the child scripts' expectations
S3_BUCKET_NAME = 'your-unique-db-backup-bucket-name'
DOMAIN_NAME = 'assign-prad.com.' 

REGION = 'ca-central-1'
IAM_INSTANCE_PROFILE_ARN = 'arn:aws:iam::975050024946:instance-profile/ecr-access-role-prad'
ECR_REPO_URL = '975050024946.dkr.ecr.ca-central-1.amazonaws.com'
DOCKER_IMAGE_NAME_TAG = 'ecr-prad:latest' # Assuming the repo name is 'ecr-prad' and tag is 'latest'
SUBNET_ID = 'subnet-0c723f27934f0860c'
SECURITY_GROUP_ID = 'sg-066a646544faa4751'
AMI_ID = 'ami-0abac8735a38475db'

# Replace with your actual pre-created IAM Role ARNs
EC2_INSTANCE_PROFILE_ARN = 'arn:aws:iam::123456789012:instance-profile/EC2_Instance_Profile_Role'
LAMBDA_ROLE_ARN = 'arn:aws:iam::123456789012:role/LambdaDBBackupRole'
# -------------------------------------------------------------------------

def run_cli_command(command_list, description="CLI command"):
    """Helper function to run external CLI commands robustly."""
    print(f"--- Running {description} ---")
    try:
        # check=True raises an exception if the command fails (non-zero exit code)
        subprocess.run(command_list, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"Successfully completed {description}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {description} failed.")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        sys.exit(1) # Exit the script on critical CLI failure
    except FileNotFoundError:
        print(f"ERROR: Required CLI tool not found in PATH for command: {command_list[0]}")
        sys.exit(1)


def main():
    print("=====================================================")
    print("      Starting Full Infrastructure Deployment        ")
    print("=====================================================")

    # -----------------------------------------------------
    # Step 5: Infrastructure as Code (IaC) with Boto3
    # -----------------------------------------------------
    print("\n[Step 5.1] Defining Infrastructure (VPC, Subnets, SGs)...")
    try:
        vpc_id, pub_subnet_ids, pvt_subnet_ids = infra_setup.create_vpc_and_subnets()
        alb_sg_id, backend_sg_id, frontend_sg_id = infra_setup.create_security_groups(vpc_id)
        print("Infrastructure base setup complete.")
    except Exception as e:
        print(f"Error during infrastructure setup: {e}")
        sys.exit(1)

    # -----------------------------------------------------
    # Step 6: Deploying Backend Services (ASG & ELB Setup parts)
    # -----------------------------------------------------
    print("\n[Step 6 & 7.1] Creating Backend ASG, ALB, and Target Groups...")
    try:
        asg_name = deploy_backend.create_backend_asg(
            backend_sg_id, pvt_subnet_ids, EC2_INSTANCE_PROFILE_ARN
        )
        # Pass gathered IDs to the networking setup function
        alb_dns = deploy_backend.setup_load_balancer_and_dns(
            vpc_id, pub_subnet_ids, alb_sg_id, asg_name
        )
        print(f"Backend deployment and Load Balancer setup complete. ALB DNS: {alb_dns}")
    except Exception as e:
        print(f"Error during backend/networking setup: {e}")
        sys.exit(1)

    # -----------------------------------------------------
    # Step 8: Deploying Frontend Services
    # -----------------------------------------------------
    print("\n[Step 8.1] Deploying Frontend EC2 Instance...")
    try:
        # We use the first public subnet ID for this single instance
        frontend_instance_id = deploy_frontend.deploy_frontend_ec2(
            frontend_sg_id, pub_subnet_ids[0], EC2_INSTANCE_PROFILE_ARN
        )
        print(f"Frontend instance deployed with ID: {frontend_instance_id}")
    except Exception as e:
        print(f"Error during frontend deployment: {e}")
        sys.exit(1)
        
    # -----------------------------------------------------
    # Step 9: AWS Lambda Deployment
    # -----------------------------------------------------
    print("\n[Step 9.1] Setting up S3 bucket and Lambda function for DB backups...")
    try:
        deploy_lambda.create_s3_bucket(S3_BUCKET_NAME)
        # Assumes lambda_function.zip is in the current directory
        lambda_arn = deploy_lambda.deploy_lambda_function(LAMBDA_ROLE_ARN)
        print(f"Lambda function deployed: {lambda_arn}")
    except Exception as e:
        print(f"Error during Lambda deployment: {e}")
        # This step might not be critical failure, so we might not sys.exit(1) here in prod code

    # -----------------------------------------------------
    # Step 10: Kubernetes (EKS) Deployment (External CLI Tools)
    # -----------------------------------------------------
    print("\n[Step 10] Transitioning to EKS/Kubernetes deployment using CLI tools.")

    EKS_CLUSTER_NAME = 'my-microservice-cluster'
    EKS_REGION = 'ca-central-1'

    # 10.1 Create EKS Cluster
    # NOTE: This step takes 15-20 minutes and requires eksctl to be installed locally.
    run_cli_command(
        ['eksctl', 'create', 'cluster', '--name', EKS_CLUSTER_NAME, '--region', EKS_REGION, '--nodegroup-name', 'standard-workers', '--node-type', 't3.medium', '--nodes', '2'],
        description="EKS Cluster Creation (This will take a while)"
    )

    # 10.2 Deploy Application with Helm
    # NOTE: This requires kubectl and helm installed, and a valid Helm chart path
    run_cli_command(
        ['aws', 'eks', 'update-kubeconfig', '--name', EKS_CLUSTER_NAME, '--region', EKS_REGION],
        description="Updating Kubeconfig"
    )
    
    # Replace './path/to/your/helm-chart' with your actual Helm chart directory
    HELM_CHART_PATH = './path/to/your/helm-chart' 
    if os.path.isdir(HELM_CHART_PATH):
        run_cli_command(
            ['helm', 'install', 'my-app-release', HELM_CHART_PATH, '--namespace', 'default'],
            description="Helm Chart Deployment"
        )
    else:
        print(f"Warning: Helm chart path not found at {HELM_CHART_PATH}. Skipping Helm deployment.")

    print("\n=====================================================")
    print("          Deployment Automation Complete!            ")
    print("=====================================================")
    print(f"Frontend Instance ID: {frontend_instance_id}")
    print(f"Backend ALB DNS: http://{alb_dns}")
    print(f"Backend API DNS CNAME: http://api.{DOMAIN_NAME}")
    print(f"EKS Cluster Name: {EKS_CLUSTER_NAME}")

if __name__ == "__main__":
    # Add robust error handling around main execution if necessary
    main()
