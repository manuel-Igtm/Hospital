// Hospital Backend - Jenkins CI/CD Pipeline
// Copyright (c) 2025, Immanuel Njogu. All rights reserved.

pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_IMAGE = 'hospital-backend'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        KUBECONFIG = credentials('kubeconfig')
        DOCKER_CREDENTIALS = credentials('docker-hub-credentials')
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        // ============================================
        // Stage 1: Checkout
        // ============================================
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --pretty=%B'
            }
        }

        // ============================================
        // Stage 2: Install Dependencies
        // ============================================
        stage('Install Dependencies') {
            steps {
                dir('backend') {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements/test.txt
                    '''
                }
            }
        }

        // ============================================
        // Stage 3: Lint & Format Check
        // ============================================
        stage('Lint') {
            steps {
                dir('backend') {
                    sh '''
                        . venv/bin/activate
                        pip install black isort flake8 bandit
                        
                        echo "=== Checking Black formatting ==="
                        black --check --diff .
                        
                        echo "=== Checking isort imports ==="
                        isort --check-only --diff .
                        
                        echo "=== Running flake8 ==="
                        flake8 apps/ --count --select=E9,F63,F7,F82 --show-source --statistics
                        
                        echo "=== Security scan with Bandit ==="
                        bandit -r apps/ -ll --skip B101 || true
                    '''
                }
            }
        }

        // ============================================
        // Stage 4: Run Tests
        // ============================================
        stage('Test') {
            environment {
                DJANGO_SETTINGS_MODULE = 'config.settings.test'
                DJANGO_SECRET_KEY = 'jenkins-test-secret-key'
            }
            steps {
                dir('backend') {
                    sh '''
                        . venv/bin/activate
                        python manage.py migrate --noinput
                        pytest --cov=apps --cov-report=xml --cov-report=term-missing -v
                    '''
                }
            }
            post {
                always {
                    dir('backend') {
                        junit allowEmptyResults: true, testResults: '**/junit.xml'
                        cobertura coberturaReportFile: '**/coverage.xml', conditionalCoverageTargets: '70, 0, 0', lineCoverageTargets: '80, 0, 0'
                    }
                }
            }
        }

        // ============================================
        // Stage 5: Build C Modules (Optional)
        // ============================================
        stage('Build C Modules') {
            when {
                changeset "native/**"
            }
            steps {
                dir('native') {
                    sh '''
                        mkdir -p build && cd build
                        cmake -DCMAKE_BUILD_TYPE=Release ..
                        make -j$(nproc)
                        ctest --output-on-failure
                    '''
                }
            }
        }

        // ============================================
        // Stage 6: Build Docker Image
        // ============================================
        stage('Build Docker') {
            steps {
                sh '''
                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} -f docker/Dockerfile .
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                '''
            }
        }

        // ============================================
        // Stage 7: Push to Registry
        // ============================================
        stage('Push to Registry') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    echo ${DOCKER_CREDENTIALS_PSW} | docker login -u ${DOCKER_CREDENTIALS_USR} --password-stdin ${DOCKER_REGISTRY}
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_REGISTRY}/${DOCKER_CREDENTIALS_USR}/${DOCKER_IMAGE}:${DOCKER_TAG}
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_REGISTRY}/${DOCKER_CREDENTIALS_USR}/${DOCKER_IMAGE}:latest
                    docker push ${DOCKER_REGISTRY}/${DOCKER_CREDENTIALS_USR}/${DOCKER_IMAGE}:${DOCKER_TAG}
                    docker push ${DOCKER_REGISTRY}/${DOCKER_CREDENTIALS_USR}/${DOCKER_IMAGE}:latest
                '''
            }
        }

        // ============================================
        // Stage 8: Deploy to Kubernetes
        // ============================================
        stage('Deploy to Kubernetes') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    # Update image tag in deployment
                    sed -i "s|image:.*hospital-backend.*|image: ${DOCKER_REGISTRY}/${DOCKER_CREDENTIALS_USR}/${DOCKER_IMAGE}:${DOCKER_TAG}|g" k8s/deployment.yaml
                    
                    # Apply Kubernetes manifests
                    kubectl apply -f k8s/namespace.yaml
                    kubectl apply -f k8s/configmap.yaml
                    kubectl apply -f k8s/secret.yaml
                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml
                    kubectl apply -f k8s/ingress.yaml
                    
                    # Wait for rollout
                    kubectl rollout status deployment/hospital-backend -n hospital --timeout=300s
                '''
            }
        }
    }

    post {
        always {
            cleanWs()
            sh 'docker system prune -f || true'
        }
        success {
            echo 'Pipeline succeeded!'
            // Uncomment to enable Slack notifications
            // slackSend(color: 'good', message: "Build ${env.BUILD_NUMBER} succeeded for ${env.JOB_NAME}")
        }
        failure {
            echo 'Pipeline failed!'
            // slackSend(color: 'danger', message: "Build ${env.BUILD_NUMBER} failed for ${env.JOB_NAME}")
        }
    }
}
