pipeline {
    agent any
    environment {
        AWS_ACCOUNT_ID = '975050024946'
        AWS_REGION = 'ca-central-1'
        IMAGE_REPO_NAME = 'ecr-prad'
        IMAGE_TAG = "build-${BUILD_NUMBER}" 
        REPOSITORY_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_REPO_NAME}"
        AWS_CREDENTIALS_ID = 'aws-credential-prad' 
    }
    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }
        stage('ECR Login') {
            steps {
                script {
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding',credentialsId: env.AWS_CREDENTIALS_ID,accessKeyVariable: 'AWS_ACCESS_KEY',secretKeyVariable: 'AWS_SECRET_KEY']]) {
                        sh """
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY_URI}
                        """
                    }
                }
            }

        }
        stage('Build and Push Docker Images - Services') {
            steps {
                script {
                    def services = ['auth-service', 'ecommerce-service', 'product-service']
                    
                    def build_steps = [:]
                    for (int i = 0; i < services.size(); i++) {
                        def service = services[i]
                        build_steps["build-${service}"] = {
                            dir("${service}") {
                                sh "npm install" // Install service-specific dependencies
                                withCredentials([usernamePassword(credentialsId: 'dockerHub', passwordVariable: 'DOCKER_HUB_PASS', usernameVariable: 'DOCKER_HUB_USER')]) {
                                    // Use the Docker Pipeline plugin build method
                                    // This block needs 'script' context to use method calls like .push()
                                    script {
                                        def img = docker.build("${DOCKER_HUB_USER}/${service}:${env.BUILD_ID}") 
                                        img.push()
                                        img.push("latest")
                                        // Use double quotes for Groovy variable interpolation within sh
                                        sh "echo 'Built and pushed ${DOCKER_HUB_USER}/${service}:${env.BUILD_ID} and latest'"
                                    }
                                }
                            }
                        }
                    }
                    // Run all service builds in parallel
                    parallel build_steps
                }
            }
        }

        stage('Build and Push Docker Image - Client') {
            steps {
                dir("client") {
                    withCredentials([usernamePassword(credentialsId: 'dockerHub', passwordVariable: 'DOCKER_HUB_PASS', usernameVariable: 'DOCKER_HUB_USER')]) {
                        // This block needs 'script' context to use method calls like .push()
                        script {
                            // The client service uses a multi-stage Dockerfile
                            def img = docker.build("${DOCKER_HUB_USER}/mern-client:${env.BUILD_ID}")
                            img.push()
                            img.push("latest")
                            sh "echo 'Built and pushed ${DOCKER_HUB_USER}/mern-client:${env.BUILD_ID} and latest'"
                        }
                    }
                }
            }
        }
        
        stage('Deploy Application') {
            // This stage requires Docker and Docker-Compose to be installed on the target server
            steps {
                // Replace 'your_target_server_ip' with the actual IP address or hostname
                // Replace 'ubuntu' with the correct username for your target server
                withCredentials([sshUserPrivateKey(credentialsId: 'target-server-ssh', keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')]) {
                    sh "scp -i \$SSH_KEY docker-compose.yml \$SSH_USER@your_target_server_ip:/home/\$SSH_USER/docker-compose.yml"
                    sh "ssh -i \$SSH_KEY \$SSH_USER@your_target_server_ip 'docker-compose pull && docker-compose up -d'"
                }
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
