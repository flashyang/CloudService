pipeline {
    agent none
    stages {
        stage('Build') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate'
                sh 'pip install -e .'
            }
        }
        stage('Test') {
            environment {
                FLASK_APP='groupnest'
                FLASK_ENV='development'
                DATABASE_URL='mysql://b4fda20e6f61ef:f9356ca7@us-cdbr-iron-east-03.cleardb.net/heroku_46f4b90a3346330'
            }
            steps {
                sh 'pip install pytest coverage'
                sh 'coverage run -m pytest'
            }
            post {
                always {
                    // junit 'test-reports/results.xml'
                }
            }
        }
        stage('Deliver') {
        
            steps {
                // sh 'pyinstaller --onefile sources/add2vals.py'
            }
            post {
                success {
                    // archiveArtifacts 'dist/add2vals'
                }
            }
        }
    }
}