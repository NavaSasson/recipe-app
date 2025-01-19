def isPushable() {
    return env.BRANCH_NAME == 'main'
}

pipeline {
    options {
        timeout(time: 15, unit: "MINUTES")
        timestamps()
    }

    triggers {
        github(triggerOnPush: true, branchFilterType: 'NameBasedFilter', includeBranchesSpec: 'main, feature/*')
    }

    tools {
        EMAIL = 'nava7386@gmail.com'
        terraform 'terraform-amd64'
    }

    agent any
    
    environment {
        DOCKER_IMAGE = 'recipe-app'
        AWS_REGION = 'ap-south-1'
        ECR_REGISTRY = '600627353694.dkr.ecr.ap-south-1.amazonaws.com/nava-recipe-app'
        IMAGE_TAG = "${env.GIT_COMMIT[0..7]}"
        GITOPS_REPO = 'git@github.com:NavaSasson/gitops-config.git'
    }
    
    stages {
        stage('Clone/Pull') {
            steps {
                checkout scm
            }
        }
        
        stage('Unit Tests') {
            steps {
                script {
                    runTests('docker-compose.unit-tests.yaml')
                }
            }
        }
        
        stage('Build + Package') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${IMAGE_TAG}")
                }
            }
        }
        
        stage('E2E Tests') {
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
                    env.NEW_VERSION = getNextVersion()
                    sh """
                        git tag -a v${env.NEW_VERSION} -m "Version ${env.NEW_VERSION}"
                        git push origin v${env.NEW_VERSION}
                    """
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
                            
                            docker tag ${DOCKER_IMAGE}:${env.GIT_COMMIT[0..7]} ${env.ECR_REGISTRY}:${env.NEW_VERSION}
                            docker tag ${DOCKER_IMAGE}:${env.GIT_COMMIT[0..7]} ${env.ECR_REGISTRY}:latest
                            
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
            sh 'docker-compose -f docker-compose.unit-tests.yaml down'
            sh 'docker-compose -f docker-compose.e2e.yaml down'
        }
        failure {
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
            docker-compose -f ${composeFile} up --build -d
            sleep 30
            docker logs -f test-container || true
            EXIT_CODE=\$(docker inspect test-container --format='{{.State.ExitCode}}')
            if [ \$EXIT_CODE -ne 0 ]; then
                exit 1
            fi
        """
    } finally {
        sh "docker-compose -f ${composeFile} down"
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