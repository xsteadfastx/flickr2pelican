pipeline {
        agent {
                dockerfile {
                        filename 'Dockerfile.tests'
                }
        }
        environment {
                TOX_WORK_DIR = '/tmp'
        }
        stages {
                stage('Test') {
                        steps {
                                sh 'tox -e py37'
                                sh 'tox -e flake8'
                                sh 'tox -e pylint'
                                sh 'tox -e mypy'
                                sh 'tox -e black-only-check'
                        }
                }
                stage('Coverage') {
                        steps {
                                sh 'tox -e coverage'
                                publishHTML(
                                        [
                                                allowMissing: false,
                                                alwaysLinkToLastBuild: false,
                                                keepAll: false,
                                                reportDir: 'htmlcov',
                                                reportFiles: 'index.html',
                                                reportName: 'HTML Report',
                                                reportTitles: ''
                                        ]
                                )
                        }
                }
        }
}
