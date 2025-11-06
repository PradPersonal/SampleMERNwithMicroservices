pipeline {
    agent any
    environment {
        AWS_ACCOUNT_ID = '975050024946'
        AWS_REGION = 'ca-central-1'
        IMAGE_REPO_NAME = 'ecr-prad'
        IMAGE_TAG = "build-${BUILD_NUMBER}" 
        ECR_REGISTRY_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_REPO_NAME}"
        AWS_CREDENTIALS_ID = 'aws-credential-prad'
        DOCKER_HUB_USER = "your_dockerhub_username" 
    }

    stages {
        stage('Clone Repository') {
            steps {
                // Jenkins SCM checkout happens automatically before the pipeline starts
                echo 'Repository cloned.'
            }
        }
        stage('Build and Push Docker Images - Backend Services') {
            steps {
                script {
                    def backendServices = ['helloservice', 'profileservice']
                    
                    def build_steps = [:]
                    for (int i = 0; i < backendServices.size(); i++) {
                        def serviceName = backendServices[i]
                        
                        if(serviceName == 'helloservice'){
                            def serviceDir = "helloService"
                        }
                        if(serviceName == 'profileservice'){
                            def serviceDir = "profileService"
                        }
                        build_steps["build-${serviceName}"] = {
                            dir("backend/${serviceDir}") {
                                sh "npm install"
                                echo "Building image started..."
                                def img = docker.build("${ECR_REGISTRY_URI}:${IMAGE_TAG}", ".")
                                echo "Building image completed..."
                                docker.withRegistry("https://${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com", "ecr:${AWS_REGION}:${AWS_CREDENTIALS_ID}") {
                                    echo "Pushing image to ECR..."
                                    img.push()
                                    img.push("latest")
                                    sh "echo 'Built and pushed ${ECR_REGISTRY_URI}:${IMAGE_TAG} and latest'"
                                }
                            }
                        }
                    }
                    // Run both service builds in parallel
                    parallel build_steps
                }
            }
        }
        stage('Build and Push Docker Image - Frontend') {
            steps {
                dir("frontend") {
                    script {
                        echo "Building image started..."
                        def img = docker.build("${ECR_REGISTRY_URI}:${IMAGE_TAG}", ".")
                        echo "Building image completed..."
                        docker.withRegistry("https://${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com", "ecr:${AWS_REGION}:${AWS_CREDENTIALS_ID}") {
                            img.push()
                            img.push("latest")
                            sh "echo 'Built and pushed ${ECR_REGISTRY_URI}:${IMAGE_TAG} and latest'"
                        }
                    }
                }
            }
        }
    }
    post {
        always {
            // Clean up local Docker images after pipeline execution to save space
            sh 'docker image prune -af'
        }
    }
}