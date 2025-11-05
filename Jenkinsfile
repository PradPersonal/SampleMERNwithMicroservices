pipeline {
    agent any
    environment {
        AWS_ACCOUNT_ID = '975050024946'
        AWS_REGION = 'ca-central-1'
        IMAGE_REPO_NAME = 'ecr-prad'
        // Tag the image with the Jenkins build number
        IMAGE_TAG = "build-${BUILD_NUMBER}" 
        REPOSITORY_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_REPO_NAME}"
        // Reference the Jenkins credential ID for AWS
        AWS_CREDENTIALS_ID = 'prad-aws-credential' 
    }
    stages {
        stage('Checkout Code') {
            steps {
                // The SCM configuration in the Jenkins job settings handles the branch filtering
                checkout scm
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    // Build the image using the Dockerfile in the current directory
                    docker.build("${IMAGE_REPO_NAME}:${IMAGE_TAG}") 
                }
            }
        }
        stage('Login to AWS ECR') {
            steps {
                script {
                    // Use the withAWS step to handle authentication using the configured credentials
                    awsCredentials(credentialsId: AWS_CREDENTIALS_ID) {
                        sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${REPOSITORY_URI}"
                    }
                }
            }
        }
        stage('Tag and Push to ECR') {
            steps {
                script {
                    sh "docker tag ${IMAGE_REPO_NAME}:${IMAGE_TAG} ${REPOSITORY_URI}:${IMAGE_TAG}"
                    sh "docker push ${REPOSITORY_URI}:${IMAGE_TAG}"
                    sh "docker tag ${IMAGE_REPO_NAME}:${IMAGE_TAG} ${REPOSITORY_URI}:latest"
                    sh "docker push ${REPOSITORY_URI}:latest"
                }
            }
        }
        stage('Clean up') {
            steps {
                // Optional: remove the local image to save space on the Jenkins agent
                sh "docker rmi ${REPOSITORY_URI}:${IMAGE_TAG} ${REPOSITORY_URI}:latest"
            }
        }
    }
}
