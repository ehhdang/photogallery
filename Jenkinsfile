pipeline {
    agent any
    environment {
        IMAGE_REPO_NAME = "photogalleryflaskapp"
        IMAGE_TAG = "latest"
        REPOSITORY_URI = "DOCKERHUB_USERNAME/${IMAGE_REPO_NAME}"
        REMOTE_USER = "ubuntu"
        REMOTE_HOST = "PHOTOGALLERY_IP"  // IP address of photogallery EC2 instance

        // environement variables for the remote host/photogallery EC2 instance
        AWS_ACCESS_KEY_ID="AWS_ACCESS_KEY_ID"
        AWS_SECRET_ACCESS_KEY="AWS_SECRET_ACCESS_KEY"
        BUCKET_NAME="galleryphotobucket"
        DB_HOSTNAME="PHOTOGALLERY_IP" // IP address of photogallery EC2 instance
        DB_PASSWORD="DB_PASSWORD"
        DB_NAME='DB_NAME'
        REGION="us-east-2"
    }

    stages {
        stage('Cloning Git') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '*/master']], extensions: [], userRemoteConfigs: [[url: 'https://github.com/ehhdang/photogallery.git']]])
            }
        }

        // Building Docker images
        stage('Building image') {
            steps {
                script {
                    sh "sudo docker build -f Dockerfile -t ${IMAGE_REPO_NAME}:${IMAGE_TAG} ."
                }
            }
        }

        // Uploading Docker images into AWS ECR
        stage('Pushing to DockerHub') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'DOCKERHUB_USERNAME', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) 
                    {
                        sh 'sudo docker login -u=$DOCKER_USERNAME -p=$DOCKER_PASSWORD'
                        sh 'sudo docker tag ${IMAGE_REPO_NAME}:${IMAGE_TAG} ${REPOSITORY_URI}:$IMAGE_TAG'
                        sh 'sudo docker push ${REPOSITORY_URI}:${IMAGE_TAG}'
                    }
                }
            }
        }

        stage ('Deploy') {
            steps {
                // copy the deploy.sh script to the remote host
                sh 'scp deploy.sh ${REMOTE_USER}@${REMOTE_HOST}:~/'

                // ssh into the remote host and create a .env file
                sh 'ssh ${REMOTE_USER}@${REMOTE_HOST} "rm -f .env"'
                sh 'ssh ${REMOTE_USER}@${REMOTE_HOST} "touch .env"'
                // add photogallery environment variables to the .env file
                sh 'ssh ${REMOTE_USER}@${REMOTE_HOST} "echo "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}" >> .env"'
                sh 'ssh ${REMOTE_USER}@${REMOTE_HOST} "echo "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}" >> .env"'
                sh 'ssh ${REMOTE_USER}@${REMOTE_HOST} "echo "BUCKET_NAME=${BUCKET_NAME}" >> .env"'
                sh 'ssh ${REMOTE_USER}@${REMOTE_HOST} "echo "DB_HOSTNAME=${DB_HOSTNAME}" >> .env"'
                sh 'ssh ${REMOTE_USER}@${REMOTE_HOST} "echo "DB_PASSWORD=${DB_PASSWORD}" >> .env"'
                sh 'ssh ${REMOTE_USER}@${REMOTE_HOST} "echo "REGION=${REGION}" >> .env"'

                // ssh into the remote host and run the deploy.sh script
                sh 'ssh ${REMOTE_USER}@${REMOTE_HOST} "chmod +x deploy.sh"'
                sh 'ssh ${REMOTE_USER}@${REMOTE_HOST} "MYSQL_ROOT_PASSWORD=\'${DB_PASSWORD}\' MYSQL_DATABASE=\'${DB_NAME}\' sh ./deploy.sh"'
            }
        }
        stage('Benchmark Test') {
            // run the unit tests
            steps {
                script{
                    sh "python -m pytest test_sample.py"
                }
            }
        }
    }
}
