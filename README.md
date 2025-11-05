# Sample MERN with Microservices



For `helloService`, create `.env` file with the content:
```bash
PORT=3001
```

For `profileService`, create `.env` file with the content:
```bash
PORT=3002
MONGO_URL="specifyYourMongoURLHereWithDatabaseNameInTheEnd"
```

Finally install packages in both the services by running the command `npm install`.

<br/>
For frontend, you have to install and start the frontend server:

```bash
cd frontend
npm install
npm start
```

Note: This will run the frontend in the development server. To run in production, build the application by running the command `npm run build`





04/11/2025:
## Step 1. Set Up AWS CLI and Boto3:
   - **Install AWS CLI and configure it with AWS credentials.**

   - **Install Boto3 for Python and configure it.**
     > pip install boto3

## Step 2: Prepare the MERN Application

### 1. Containerize the MERN Application:

   - **Ensure the MERN application is containerized using Docker**. Create a Dockerfile for each component (frontend and backend).

### 2. Push Docker Images to Amazon ECR:

   - **Build Docker images** for the frontend and backend.


      ECR registry details
      #### registry_id = "975050024946"
      #### repository_id = "sample-mern-repo"
      #### repository_url = "975050024946.dkr.ecr.ca-central-1.amazonaws.com/sample-mern-repo"
      ---------------------------------------------------------------------
  - Get login details:
    > aws ecr get-login-password --region $AWS_REGION | \
     docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com\

example:
   > aws ecr get-login-password --region ca-central-1 |   docker login --username AWS --password-stdin 975050024946.dkr.ecr.ca-central-1.amazonaws.com

   - **Create an Amazon ECR repository** for each image.
     > AWS_REGION=ca-central-1\
     > REPO=frontend\
     > aws ecr describe-repositories --repository-names $REPO --region $AWS_REGION >/dev/null 2>&1 ||   aws ecr create-repository --repository-name $REPO --region $AWS_REGION\

     > REPO=hello-service\
     > aws ecr describe-repositories --repository-names $REPO --region $AWS_REGION >/dev/null 2>&1 ||   aws ecr create-repository --repository-name $REPO --region $AWS_REGION\

     > REPO=profile-service\
     > aws ecr describe-repositories --repository-names $REPO --region $AWS_REGION >/dev/null 2>&1 ||   aws ecr create-repository --repository-name $REPO --region $AWS_REGION


   - **Push the Docker images** to their respective ECR repositories.
   > docker login

   ### Frontend
   REPO=frontend\
   docker build -t $REPO -f /workspaces/SampleMERNwithMicroservices/frontend/Dockerfile /workspaces/SampleMERNwithMicroservices/frontend\
   docker tag $REPO:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO}:latest\
example: docker tag $REPO:latest 975050024946.dkr.ecr.ca-central-1.amazonaws.com/${REPO}:latest
   docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO}:latest\
   example: docker push 975050024946.dkr.ecr.ca-central-1.amazonaws.com/${REPO}:latest

   ### Hello service
   REPO=hello-service\
   docker build -t $REPO -f /workspaces/SampleMERNwithMicroservices/backend/helloService/Dockerfile /workspaces/SampleMERNwithMicroservices/backend/helloService\
   example: docker build -t $REPO -f ./backend/helloService/Dockerfile ./backend/helloService
   docker tag $REPO:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO}:latest\
   example: docker tag $REPO:latest 975050024946.dkr.ecr.ca-central-1.amazonaws.com/${REPO}:latest
   docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO}:latest
   example: docker push 975050024946.dkr.ecr.ca-central-1.amazonaws.com/${REPO}:latest

   ### Profile service
   REPO=profile-service
   docker build -t $REPO -f /workspaces/SampleMERNwithMicroservices/backend/profileService/Dockerfile /workspaces/SampleMERNwithMicroservices/backend/profileService
   example: docker build -t $REPO -f ./backend/profileService/Dockerfile ./backend/profileService
   docker tag $REPO:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO}:latest
   example: docker tag $REPO:latest 975050024946.dkr.ecr.ca-central-1.amazonaws.com/${REPO}:latest
   docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO}:latest
   example: docker push 975050024946.dkr.ecr.ca-central-1.amazonaws.com/${REPO}:latest

Step 3: Version Control

1. Use AWS CodeCommit:

   - Create a CodeCommit repository.

   - Push the MERN application source code to the CodeCommit repository.

Step 4: Continuous Integration with Jenkins

1. Set Up Jenkins:

   - Install Jenkins on an EC2 instance.
            created a IAM policy: ecr-access-policy-prad
            created a IAM role:   ecr-access-role-prad
            Created EC2 instance with the role ecr-access-role-prad
            
            Connecting to the ec2 instance from local PS
            
            > sudo wget -O /usr/share/keyrings/jenkins-keyring.asc https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
            > echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc]" https://pkg.jenkins.io/debian binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
            > sudo apt update -y
            > sudo apt install jenkins -y
            
            Install Docker:
            > sudo apt install docker.io -y
            
            Add the ubuntu and jenkins users to the docker group so they can run Docker commands without sudo:
            > sudo usermod -aG docker ubuntu
            > sudo usermod -aG docker jenkins
            
            Restart Jenkins service to apply group changes and ensure Docker is running:
            > sudo systemctl restart docker
            > sudo systemctl enable docker
            > sudo systemctl restart Jenkins
            Log out and log back in to your SSH session to pick up the new docker group permissions:
            > exit
            > <ssh to instance>
            
            Access the Jenkins Web UI:
            http://<your_instance_public_ip>:8080
            http://3.99.126.89:8080
            Retrieve the initial admin password from the EC2 instance
            > sudo cat /var/lib/jenkins/secrets/initialAdminPassword
            228527d9283d4028b218103f20b32f28
            
            Create your first admin user credentials and click Save and Continue:
            user ID: prad-Jenkins
            Jenkins URL: http://3.99.126.89:8080/

   - Configure Jenkins with necessary plugins.
   - - Added Plugin for Docker Pipeline
   - - Added Plugin for AWS Credential

2. Create Jenkins Jobs:

   - Create Jenkins jobs for building and pushing Docker images to ECR.

   - Trigger the Jenkins jobs whenever there's a new commit in the CodeCommit repository.

Step 5: Infrastructure as Code (IaC) with Boto3

1. Define Infrastructure with Boto3 (Python Script):

   - Use Boto3 to define the infrastructure (VPC, subnets, security groups).

   - Define an Auto Scaling Group (ASG) for the backend.

   - Create AWS Lambda functions if needed.

Step 6: Deploying Backend Services

1. Deploy Backend on EC2 with ASG:

   - Use Boto3 to deploy EC2 instances with the Dockerized backend application in the ASG.

Step 7: Set Up Networking

1. Create Load Balancer:

   - Set up an Elastic Load Balancer (ELB) for the backend ASG.

2. Configure DNS:

   - Set up DNS using Route 53 or any other DNS service.

Step 8: Deploying Frontend Services

1. Deploy Frontend on EC2:

   - Use Boto3 to deploy EC2 instances with the Dockerized frontend application.

Step 9: AWS Lambda Deployment

1. Create Lambda Functions:

- Use Boto3 to create AWS Lambda functions for specific tasks within the application.

- Backup of Db using Lambda Functions and store in S3 bucket - put time stamping on the backup

Step 10: Kubernetes (EKS) Deployment

1. Create EKS Cluster:

   - Use eksctl or other tools to create an Amazon EKS cluster.

2. Deploy Application with Helm:

   - Use Helm to package and deploy the MERN application on EKS.

Step 11: Monitoring and Logging

1. Set Up Monitoring:

   - Use CloudWatch for monitoring and setting up alarms.


2. Configure Logging:

   - Use CloudWatch Logs or another logging solution for collecting logs.

Step 12: Documentation

1. Document the Architecture:

 - Instruct learners to create documentation for the entire architecture and deployment process.

 - Put everything on the GitHub

Step 13: Final Checks

1. Validate the Deployment:

   - Ensure that the MERN application is accessible and functions correctly.

BONUS: ChatOps

Step 14: ChatOps Integration

Create SNS Topics:


Use Boto3 to create SNS topics for different events (e.g., deployment success, failure).

Create Lambda for ChatOps:

Write a Lambda function that sends notifications to the appropriate SNS topics based on deployment events.

Integrate ChatOps with Messaging Platform:

Configure integrations with a messaging platform (e.g., Slack/MS Teams/ Telegram) to receive notifications from SNS.

Configure SES


