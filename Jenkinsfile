pipeline {
    options {
        timeout(time: 15, unit: "MINUTES")
        timestamps()
    }

    triggers {
        githubPush()
    }

    agent any
    
    environment {
        EMAIL='nava7386@gmail.com'
        DOCKER_IMAGE = 'recipe-app'
        AWS_REGION = 'ap-south-1'
        ECR_REGISTRY = '600627353694.dkr.ecr.ap-south-1.amazonaws.com/nava-recipe-app'
        IMAGE_TAG = "latest"
        GITOPS_REPO = 'github.com/NavaSasson/gitops-config.git'
    }
    
    stages {
        stage('Clone/Pull') {
            when {
                anyOf {
                    branch 'main'
                    branch 'feature/*'
                }
            }
            steps {
                checkout scm
            }
        }
        
        stage('Unit Tests') {
            when {
                anyOf {
                    branch 'main'
                    branch 'feature/*'
                }
            }
            steps {
                script {
                    runTests('docker-compose.unit-tests.yaml')
                }
            }
        }
        
        stage('Build + Package') {
            when {
                anyOf {
                    branch 'main'
                    branch 'feature/*'
                }
            }
            steps {
                script {
                    sh "docker build -t ${DOCKER_IMAGE}:${IMAGE_TAG} ."
                }
            }
        }
        
        stage('E2E Tests') {
            when {
                anyOf {
                    branch 'main'
                    branch 'feature/*'
                }
            }
            steps {
                script {
                    runTests('docker-compose.e2e.yaml')
                }
            }
        }

        stage('Tag Version') {
            when {
                anyOf {
                    branch 'main'
                }
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'Nava-github-AT', passwordVariable: 'GITHUB_TOKEN', usernameVariable: 'GITHUB_USER')]) {
                        env.NEW_VERSION = getNextVersion()
                        sh """
                            git tag v${env.NEW_VERSION}
                            git push https://${env.GITHUB_USER}:${env.GITHUB_TOKEN}@github.com/NavaSasson/recipe-app.git v${env.NEW_VERSION}
                        """
                    }
                }
            }
        }

        stage('Publish to ECR') {
            when {
                anyOf {
                    branch 'main'
                }
            }
            steps {
                echo 'Publishing docker image to ECR...'
                script {
                    sh """
                        # Login to AWS ECR
                        echo "Logging into AWS ECR..."
                        aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin $ECR_REGISTRY

                        
                        # Tag the image for ECR
                        echo "Tagging the Docker image $DOCKER_IMAGE:$IMAGE_TAG for ECR..."
                        docker tag $DOCKER_IMAGE:$IMAGE_TAG $ECR_REGISTRY:${env.NEW_VERSION}
                        docker tag $DOCKER_IMAGE:$IMAGE_TAG $ECR_REGISTRY:latest

                        # Push the Docker image to ECR
                        docker push $ECR_REGISTRY:${env.NEW_VERSION}
                        docker push $ECR_REGISTRY:latest
                    """
                }
            }
        }

        stage('Deploy') {
            when {
                anyOf {
                    branch 'main'
                }
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'Nava-github-AT', passwordVariable: 'GITHUB_TOKEN', usernameVariable: 'GITHUB_USER')]) {
                        sh """
                            git clone https://${env.GITHUB_USER}:${env.GITHUB_TOKEN}@${GITOPS_REPO} gitops-config
                            cd gitops-config
                            
                            # Update version in Chart.yaml
                            # yq e '.appVersion = "${env.NEW_VERSION}"' -i Chart.yaml
                            sed -i 's/^appVersion:.*/appVersion: ${env.NEW_VERSION}/' Chart.yaml
                            
                            git add Chart.yaml
                            git commit -m "Update recipe-app version to ${env.NEW_VERSION}"
                            git push origin main
                        """
                    }
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        failure {
            echo "Pipeline failed at stage: ${currentBuild.displayName}"
            emailext (
                subject: "Pipeline Failed: ${currentBuild.fullDisplayName}",
                body: "Pipeline failed at stage: ${currentBuild.displayName}",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }
    }
}

def runTests(composeFile) {
    try {
        sh """
            docker compose -f ${composeFile} up --build -d
            sleep 30
            docker logs -f test-container-main || true
            EXIT_CODE=\$(docker inspect test-container-main --format='{{.State.ExitCode}}')
            if [ \$EXIT_CODE -ne 0 ]; then
                exit 1
            fi
        """
    } finally {
        sh "docker compose -f ${composeFile} down"
    }
}

def getNextVersion() {
    def currentVersion = '1.0.0'
    try {
        withCredentials([usernamePassword(credentialsId: 'Nava-github-AT', passwordVariable: 'GITHUB_TOKEN', usernameVariable: 'GITHUB_USER')]) {
            sh "git fetch --tags https://${env.GITHUB_USER}:${env.GITHUB_TOKEN}@github.com/NavaSasson/recipe-app.git"
        }
        // Get all git tags
        def tags = sh(script: 'git tag -l "v*"', returnStdout: true).trim()
        if (tags) {
            // Find latest version tag
            currentVersion = sh(
                script: 'git tag -l "v*" | sort -V | tail -n1 | sed "s/v//"',
                returnStdout: true
            ).trim()
        }
    } catch (Exception e) {
        echo "No existing version tags found, starting with ${currentVersion}"
        return currentVersion
    }
    
    // Split version into major, minor, patch
    def (major, minor, patch) = currentVersion.tokenize('.')
    // Increment patch version
    def nextPatch = (patch as int) + 1
    return "${major}.${minor}.${nextPatch}"
}