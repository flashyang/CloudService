// pipeline {
//     agent none
//     stages {
//         stage('Build') {
//             steps {
//                 sh 'python3 -m venv venv'
//                 sh '. venv/bin/activate'
//                 sh 'pip install -e .'
//             }
//         }
//         stage('Test') {
//             environment {
//                 FLASK_APP='groupnest'
//                 FLASK_ENV='development'
//                 DATABASE_URL='mysql://b4fda20e6f61ef:f9356ca7@us-cdbr-iron-east-03.cleardb.net/heroku_46f4b90a3346330'
//             }
//             steps {
//                 sh 'pip install pytest coverage'
//                 sh 'coverage run -m pytest'
//             }
//             // post {
//             //     always {
//             //         // junit 'test-reports/results.xml'
//             //     }
//             // }
//         }
//         // stage('Deliver') {
        
//         //     steps {
//         //         // sh 'pyinstaller --onefile sources/add2vals.py'
//         //     }
//         //     post {
//         //         success {
//         //             // archiveArtifacts 'dist/add2vals'
//         //         }
//         //     }
//         // }
//     }
// }




node {
    stage 'Checkout and Build' 
    sh 'pip install virtualenv'
    createVirtualEnv 'env'
    executeIn 'env', 'pip install -r requirements.txt'

    stage 'Test'
    executeIn 'env', 'export FLASK_APP=groupnest'
    executeIn 'env', 'export FLASK_ENV=development'
    executeIn 'env', 'export DATABASE_URL=mysql://b4fda20e6f61ef:f9356ca7@us-cdbr-iron-east-03.cleardb.net/heroku_46f4b90a3346330'

    executeIn 'env', 'coverage run -m pytest'
    executeIn 'env', 'python -m coverage xml -o reports/coverage.xml'
    // executeIn 'env', 'step([$class: 'CoberturaPublisher', autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'reports/coverage.xml', failNoReports: false, failUnhealthy: false, failUnstable: false, maxNumberOfBuilds: 10, onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false])'

    stage 'Build package'
    executeIn 'env', 'python setup.py bdist_wheel'
    executeIn 'env', 'archiveArtifacts allowEmptyArchive: true, artifacts: "dist/*whl", fingerprint: true'




    
    // virtualEnv('true')
    // runCmd('pip install -r requirements.txt')

    // stage 'Test'

    // runCmd('export FLASK_APP=groupnest')
    // runCmd('export FLASK_ENV=development')
    // runCmd('export DATABASE_URL=mysql://b4fda20e6f61ef:f9356ca7@us-cdbr-iron-east-03.cleardb.net/heroku_46f4b90a3346330')
    // runCmd('coverage run -m pytest')
    // runCmd('python -m coverage xml -o reports/coverage.xml')

    // step([$class: 'CoberturaPublisher', autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'reports/coverage.xml', failNoReports: false, failUnhealthy: false, failUnstable: false, maxNumberOfBuilds: 10, onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false])
     

    // stage 'Build package'
    // runCmd('python setup.py bdist_wheel')
    // runCmd('archiveArtifacts allowEmptyArchive: true, artifacts: "dist/*whl", fingerprint: true')




}

// one of the workaround
def createVirtualEnv(String name) {
    sh "virtualenv ${name}"
}
 
def executeIn(String environment, String script) {
    sh "source ${environment}/bin/activate && " + script
}
 
// alternative workaround
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


