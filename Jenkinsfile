pipeline {
    options {
        timeout(time: 1, unit: 'HOURS')
    }
    agent {
        label 'ubuntu-1804 && amd64 && docker'
    }
    stages {
        stage('build and push') {
            when {
                branch 'master'
            }
            sh "docker build -t semerhi/dockerized_dash_app ."

            steps {
                withDockerRegistry([url: "", credentialsId: "dockerbuildbot-index.docker.io"]) {
                    sh("docker push semerhi/dockerized_dash_app")
                }
            }
        }
    }
}
