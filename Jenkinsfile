pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'dockerhub-credentials' // Docker Hub credentials ID
        DOCKERHUB_REPO = 'ahmedamamou'      
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Starting Checkout Code stage...'
                // Clone the GitHub repository
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']], // Replace 'main' with the branch name you want to build
                    userRemoteConfigs: [[
                        url: 'https://github.com/Ahmed-Amamou/Pipeline-Music-Classification.git' // Replace with your repo URL
                    ]]
                ])
                echo 'Checkout Code stage completed.'
            }
        }

        stage('Build Docker Images') {
            parallel {
                stage('Build Frontend Image') {
                    steps {
                        script {
                            sh 'docker build -t ${DOCKERHUB_REPO}/frontend ./frontend'
                        }
                    }
                }
                stage('Build VGG19 Model Image') {
                    steps {
                        script {
                            sh 'docker build -t ${DOCKERHUB_REPO}/vgg_model ./vgg_model'
                        }
                    }
                }
                stage('Build SVM Model Image') {
                    steps {
                        script {
                            sh 'docker build -t ${DOCKERHUB_REPO}/svm_model ./svm_model'
                        }
                    }
                }
            }
        }

        stage('Push Docker Images to Docker Hub') {
            steps {
                // Log in to Docker Hub and push images
                withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                    sh 'echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin'
                    sh 'docker push ${DOCKERHUB_REPO}/frontend'
                    sh 'docker push ${DOCKERHUB_REPO}/vgg_model'
                    sh 'docker push ${DOCKERHUB_REPO}/svm_model'
                    sh 'docker logout'
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}
