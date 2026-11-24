pipeline {
    agent any

    stages {
        stage('Test Backend') {
            steps {
                dir('backend') {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install -r requirements.txt -r requirements-dev.txt
                        pytest -v
                    '''
                }
            }
        }

        stage('Build Backend Image') {
            steps {
                sh 'docker build -t orderpulse-api:${BUILD_NUMBER} ./backend'
            }
        }
    }

    post {
        success { echo 'Pipeline success' }
        failure { echo 'Pipeline failed' }
    }
}
