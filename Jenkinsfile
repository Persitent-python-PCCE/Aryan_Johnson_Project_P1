pipeline {

    agent any

    triggers {
        githubPush()
    }

    environment {
        DOCKER_IMAGE = 'aryanjohnson/ticket-booking-app'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                sh 'python3 -m pip install --break-system-packages -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                sh 'python3 -m pytest'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'

                sh 'docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .'

                sh 'docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing Docker image to Docker Hub...'

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-cred',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                        echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

                        docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}

                        docker push ${DOCKER_IMAGE}:latest

                        docker logout
                    '''
                }
            }
        }
    }

    post {

        success {
            emailext(
                subject: "SUCCESS ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                    <h2>Jenkins build Successful!!</h2>
                    <p>
                        <b>URL</b>: ${env.BUILD_URL}
                    </p>
                """,
                to: "aryanjohnson1307@gmail.com"
            )
        }

        failure {
            emailext(
                subject: "FAILED ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                    <h2>Jenkins build Failed</h2>
                    <p>
                        <b>URL</b>: ${env.BUILD_URL}
                    </p>
                """,
                to: "aryanjohnson1307@gmail.com"
            )
        }
    }
}