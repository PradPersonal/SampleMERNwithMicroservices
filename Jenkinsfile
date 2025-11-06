pipeline {
    agent any
    tools {
        // Replace 'node18' with the name of your NodeJS tool configuration in Jenkins
        nodejs 'node18' 
    }
    
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
                                withCredentials([usernamePassword(credentialsId: 'dockerHub', passwordVariable: 'DOCKER_HUB_PASS', usernameVariable: 'DOCKER_HUB_USER')]) {
                                    script {
                                        // Build the image using the DOCKERFILE in the directory, tagging with the serviceName
                                        def img = docker.build("${DOCKER_HUB_USER}/${serviceName}:${env.BUILD_ID}") 
                                        img.push()
                                        img.push("latest")
                                        sh "echo 'Built and pushed ${DOCKER_HUB_USER}/${serviceName}:${env.BUILD_ID} and latest'"
                                    }
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
                    withCredentials([usernamePassword(credentialsId: 'dockerHub', passwordVariable: 'DOCKER_HUB_PASS', usernameVariable: 'DOCKER_HUB_USER')]) {
                        script {
                            // Build the frontend image
                            def img = docker.build("${DOCKER_HUB_USER}/mern-frontend:${env.BUILD_ID}")
                            img.push()
                            img.push("latest")
                            sh "echo 'Built and pushed ${DOCKER_HUB_USER}/mern-frontend:${env.BUILD_ID} and latest'"
                        }
                    }
                }
            }
        }
        
        stage('Deploy Application (Optional)') {
            // This stage is commented out by default. Uncomment it to enable deployment.
            // Requires a docker-compose.yml file that references the built images 
            // (${DOCKER_HUB_USER}/helloService-1, ${DOCKER_HUB_USER}/helloService-2, ${DOCKER_HUB_USER}/mern-frontend)
            // and SSH credentials configured in Jenkins ('target-server-ssh').

            /*
            steps {
                // Replace 'your_target_server_ip' with the actual IP address or hostname
                // Replace 'ubuntu' with the correct username for your target server
                withCredentials([sshUserPrivateKey(credentialsId: 'target-server-ssh', keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')]) {
                    sh "scp -i \$SSH_KEY docker-compose.yml \$SSH_USER@your_target_server_ip:/home/\$SSH_USER/docker-compose.yml"
                    sh "ssh -i \$SSH_KEY \$SSH_USER@your_target_server_ip 'docker-compose pull && docker-compose up -d'"
                }
            }
            */
        }
    }
    post {
        always {
            // Clean up local Docker images after pipeline execution to save space
            sh 'docker image prune -af'
        }
    }
}