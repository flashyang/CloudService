// // pipeline {
// //     agent none
// //     stages {
// //         stage('Build') {
// //             steps {
// //                 sh 'python3 -m venv venv'
// //                 sh '. venv/bin/activate'
// //                 sh 'pip install -e .'
// //             }
// //         }
// //         stage('Test') {
// //             environment {
// //                 FLASK_APP='groupnest'
// //                 FLASK_ENV='development'
// //                 DATABASE_URL='mysql://b4fda20e6f61ef:f9356ca7@us-cdbr-iron-east-03.cleardb.net/heroku_46f4b90a3346330'
// //             }
// //             steps {
// //                 sh 'pip install pytest coverage'
// //                 sh 'coverage run -m pytest'
// //             }
// //             // post {
// //             //     always {
// //             //         // junit 'test-reports/results.xml'
// //             //     }
// //             // }
// //         }
// //         // stage('Deliver') {
        
// //         //     steps {
// //         //         // sh 'pyinstaller --onefile sources/add2vals.py'
// //         //     }
// //         //     post {
// //         //         success {
// //         //             // archiveArtifacts 'dist/add2vals'
// //         //         }
// //         //     }
// //         // }
// //     }
// // }


// node {
//     stage 'Checkout and Build' 
    
//     // createVirtualEnv 'env'
//     // executeIn 'env', 'pip install -r requirements.txt'
//     // executeIn 'env', './manage.py test'
//     // executeIn 'env', './manage.py integration-test'
    
//     virtualEnv('true')
//     runCmd('pip install -r requirements.txt')

//     stage 'Test'

//     runCmd('export FLASK_APP=groupnest')
//     runCmd('export FLASK_ENV=development')
//     runCmd('export DATABASE_URL=mysql://b4fda20e6f61ef:f9356ca7@us-cdbr-iron-east-03.cleardb.net/heroku_46f4b90a3346330')
//     runCmd('coverage run -m pytest')
//     runCmd('python -m coverage xml -o reports/coverage.xml')

//     // runCmd(junit allowEmptyResults: true, testResults: 'test-reports/results.xml', fingerprint: true)

//     runCmd('step([$class: 'CoberturaPublisher',
//         autoUpdateHealth: false,
//         autoUpdateStability: false,
//         coberturaReportFile: 'reports/coverage.xml',
//         failNoReports: false,
//         failUnhealthy: false,
//         failUnstable: false,
//         maxNumberOfBuilds: 10,
//         onlyStable: false,
//         sourceEncoding: 'ASCII',
//         zoomCoverageChart: false])')

//     stage 'Build package'
//     runCmd('python setup.py bdist_wheel')
//     runCmd('archiveArtifacts allowEmptyArchive: true, artifacts: "dist/*whl", fingerprint: true')




// }

// // one of the workaround
// def createVirtualEnv(String name) {
//     sh "virtualenv ${name}"
// }
 
// def executeIn(String environment, String script) {
//     sh "source ${environment}/bin/activate && " + script
// }
 
// // alternative workaround
// env.VENV_PATH = "${JENKINS_HOME}/.virtualenv/${JOB_NAME}/venv"

// def virtualEnv(String rebuild){
//     withEnv(["PATH+VEX=~/.local/bin"]){
//         if(rebuild == "true") {
//             sh "rm -rf ${env.VENV_PATH}"
//             sh "echo 'rebuild is true'"
//         }
//         sh returnStatus: true, script: "virtualenv ${env.VENV_PATH}"
//     }
// }

// def runCmd(String pyCmd){
//     withEnv(["PATH+VEX=~/.local/bin"]){
//         sh returnStatus: true, script: "vex --path=${env.VENV_PATH} ${pyCmd}"
//     }
// }


pipeline {
    agent any
    environment{
        workspace_path = "$WORKSPACE/${BUILD_NUMBER}"
        PYTHONPATH = "$WORKSPACE/${BUILD_NUMBER}"
    }
    stages {
        stage('Checkout'){
             steps {
                sh """ pwd """
                checkout([$class: 'GitSCM',
                branches: [[name: '*/yangsun']],
                doGenerateSubmoduleConfigurations: false,
                extensions: [[$class: 'RelativeTargetDirectory',
                relativeTargetDir: './${BUILD_NUMBER}']],
                submoduleCfg: [], userRemoteConfigs:
                [[credentialsId: 'git', url: 'https://github.com/flashyang/CloudService.git']]])
                }
        }
        stage('Tests') {
            environment {
                FLASK_APP=groupnest
                FLASK_ENV=development
                DATABASE_URL=mysql://b4fda20e6f61ef:f9356ca7@us-cdbr-iron-east-03.cleardb.net/heroku_46f4b90a3346330
            }
            steps {

		        dir("${WORKSPACE}/${BUILD_NUMBER}"){
		            sh """
		                echo $PYTHONPATH
		                pip3 install -r "./requirements.txt"
                        python3 -m pytest --cov=main ${workspace_path}/tests/
		            """
		        }
            }
        }
    }
}