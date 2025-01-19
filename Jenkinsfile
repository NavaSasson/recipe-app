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
        GITOPS_REPO = 'git@github.com:NavaSasson/gitops-config.git'
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
                branch 'main'
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'Nava-github-AT', passwordVariable: 'GITHUB_TOKEN', usernameVariable: 'GITHUB_USER')]) {
                        env.NEW_VERSION = getNextVersion()
                        sh """
                            git tag v${env.NEW_VERSION}"
                            git push https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/your-repo.git v${env.NEW_VERSION}
                        """
                    }
                }
            }
        }


        stage('Publish to ECR') {
            when {
                branch 'main'
            }
            steps {
                script {
                    withAWS(credentials: 'aws-credentials', region: env.AWS_REGION) {
                        sh """
                            aws ecr get-login-password --region ${env.AWS_REGION} | docker login --username AWS --password-stdin ${env.ECR_REGISTRY}
                            
                            docker tag ${DOCKER_IMAGE}:${IMAGE_TAG} ${env.ECR_REGISTRY}:${env.NEW_VERSION}
                            docker tag ${DOCKER_IMAGE}:${IMAGE_TAG} ${env.ECR_REGISTRY}:latest
                            
                            docker push ${env.ECR_REGISTRY}:${env.NEW_VERSION}
                            docker push ${env.ECR_REGISTRY}:latest
                        """
                    }
                }
            }
        }
        
        // stage('Deploy') {
        //     when {
        //         branch 'main'
        //     }
        //     steps {
        //         script {
        //             withCredentials([sshUserPrivateKey(credentialsId: 'gitops-ssh-key', keyFileVariable: 'SSH_KEY')]) {
        //                 sh """
        //                     git clone ${GITOPS_REPO} gitops-config
        //                     cd gitops-config
                            
        //                     # Update version in Chart.yaml
        //                     yq e '.version = "${env.NEW_VERSION}"' -i helm/recipe-app/Chart.yaml
        //                     yq e '.appVersion = "${env.NEW_VERSION}"' -i helm/recipe-app/Chart.yaml
                            
        //                     git config --global user.email "jenkins@example.com"
        //                     git config --global user.name "Jenkins"
        //                     git add helm/recipe-app/Chart.yaml
        //                     git commit -m "Update recipe-app version to ${env.NEW_VERSION}"
        //                     GIT_SSH_COMMAND="ssh -i ${SSH_KEY}" git push origin main
        //                 """
        //             }
        //         }
        //     }
        // }
    }
    
    post {
        always {
            cleanWs()
            sh 'docker compose -f docker-compose.unit-tests.yaml down'
            sh 'docker compose -f docker-compose.e2e.yaml down'
        }
        failure {
            echo "Pipeline failed at stage: ${currentBuild.displayName}"
            // emailext (
            //     subject: "Pipeline Failed: ${currentBuild.fullDisplayName}",
            //     body: "Pipeline failed at stage: ${currentBuild.displayName}",
            //     recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            // )
        }
    }
}

def runTests(composeFile) {
    try {
        sh """
            docker compose -f ${composeFile} up --build -d
            sleep 30
            docker logs -f test-container || true
            EXIT_CODE=\$(docker inspect test-container --format='{{.State.ExitCode}}')
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