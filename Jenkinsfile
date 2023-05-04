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
                    withCredentials([usernamePassword(credentialsId: 'acatnamedsummer', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) 
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
                sh 'ssh ${REMOTE_USER}@${REMOTE_HOST} "rm -rf .benchmarks"'

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
                    sh 'sleep 10 && ssh ${REMOTE_USER}@${REMOTE_HOST} "docker exec -t photogallery sh -c \"pytest --benchmark-autosave\""'
                    sh 'ssh ${REMOTE_USER}@${REMOTE_HOST} "docker cp photogallery:/app/.benchmarks ."'
                    //sh 'ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir .benchmarks/jmeter"'
                }
            }
        }
        
         stage ('Run JMeter') {
            steps {
                // copy the deploy.sh script to the remote host
                sh 'scp Photo-Gallery-Test-Plan.jmx ${REMOTE_USER}@${REMOTE_HOST}:~/'
                sh 'scp run_jmeter.sh ${REMOTE_USER}@${REMOTE_HOST}:~/'
                sh 'scp *.jpg ${REMOTE_USER}@${REMOTE_HOST}:~/'
                sh 'ssh ${REMOTE_USER}@${REMOTE_HOST} "chmod +x run_jmeter.sh"' 
                sh 'ssh ${REMOTE_USER}@${REMOTE_HOST} "./run_jmeter.sh"'
                
                
            }
        }

        stage('Uploading Test Results') {
            steps {
                script {
                    //sh 'ssh ${REMOTE_USER}@${REMOTE_HOST} "docker cp photogallery:/app/.benchmarks ."'
                    sh 'scp -r ${REMOTE_USER}@${REMOTE_HOST}:~/.benchmarks .'
                    sh 'scp -r ${REMOTE_USER}@${REMOTE_HOST}:~/data.csv .'
                    sh 'sudo rm -rf /home/ubuntu/benchmarks'
                    sh 'sudo mv /home/ubuntu/.benchmarks /home/ubuntu/benchmarks'
                    sh 'sudo chmod -R 777 /home/ubuntu/benchmarks/'
                    sh 'sudo cp /home/ubuntu/data.csv .'
                    sh 'sudo zip -r jmeter.zip /home/ubuntu/benchmarks/jmeter'
                    sh 'for i in `sudo ls /home/ubuntu/benchmarks/Linux-CPython-3.9-64bit/ | grep json` ; do sudo cp /home/ubuntu/benchmarks/Linux-CPython-3.9-64bit/$i one.json; done'
                }
            }
        }
        
       
    }

    post {
        always {
            archiveArtifacts artifacts: 'one.json', fingerprint: true
            archiveArtifacts artifacts: 'jmeter.zip', fingerprint: true
            archiveArtifacts artifacts: 'data.csv', fingerprint: true
        }
    }
}
