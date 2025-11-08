
#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

EKS_CLUSTER_NAME="my-microservice-cluster-ca"
EKS_REGION="ca-central-1" # Set your target region for EKS

echo "====================================================="
echo "      Starting Full Infrastructure Deployment        "
echo "====================================================="

# Check for required tools
if ! command -v python3 &> /dev/null; then echo "python3 is required."; exit 1; fi
if ! command -v aws &> /dev/null; then echo "AWS CLI is required."; exit 1; fi
if ! command -v eksctl &> /dev/null; then echo "eksctl is required."; exit 1; fi
if ! command -v helm &> /dev/null; then echo "helm is required."; exit 1; fi


# --- Step 5: Infrastructure as Code (IaC) with Boto3 ---
echo "\n[Step 5] Running infrastructure_setup.py..."
python3 infra_setup.py

# Note: The subsequent scripts (6-9) rely on the configuration variables set within their own files
# and assume the resources created by infra_setup.py (like VPC IDs) are correctly found
# via boto3 calls within them or passed via command line arguments (which these scripts don't currently support).
# This is a limitation of this shell-based approach compared to the Python module approach.

# --- Step 6-7: Deploying Backend Services & Networking ---
echo "\n[Step 6-7] Running deploy_backend.py (ASG, ALB, Route53)..."
python3 deploy_backend.py

# --- Step 8: Deploying Frontend Services ---
echo "\n[Step 8] Running deploy_frontend.py..."
python3 deploy_frontend.py

# --- Step 9: AWS Lambda Deployment ---
echo "\n[Step 9] Running deploy_lambda.py..."
# Ensure lambda_function.zip exists for this step to succeed
python3 deploy_lambda.py

# --- Step 10: Kubernetes (EKS) Deployment (External CLI Tools) ---
echo "\n[Step 10.1] Creating EKS Cluster using eksctl in $EKS_REGION (This will take 15-20 mins)..."
eksctl create cluster --name $EKS_CLUSTER_NAME --region $EKS_REGION --nodegroup-name standard-workers --node-type t3.medium --nodes 2 --nodes-min 1 --nodes-max 4

echo "\n[Step 10.2] Deploying Application with Helm..."

# Update Kubeconfig
echo "Updating Kubeconfig for kubectl..."
aws eks update-kubeconfig --name $EKS_CLUSTER_NAME --region $EKS_REGION

# Deploy Helm Chart (Update the path below to your actual Helm chart directory)
HELM_CHART_PATH="./path/to/your/helm-chart" 
if [ -d "$HELM_CHART_PATH" ]; then
    echo "Installing Helm chart from $HELM_CHART_PATH..."
    helm install my-app-release $HELM_CHART_PATH --namespace default
else
    echo "Warning: Helm chart path not found at $HELM_CHART_PATH. Skipping Helm deployment."
fi


echo "====================================================="
echo "          Deployment Automation Complete!            "
echo "====================================================="
