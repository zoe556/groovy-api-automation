
pipeline {
  agent  any

  options {
    disableConcurrentBuilds()
  }

  parameters {
    string( name: 'TEST_ENVIRONMENT', defaultValue: 'local_host', description: 'Provide test environment name')
  }

  environment {
    AUTOMATION_PATH = "automation/"
    ALLURE_REPORT = "automation/target/allure_reports"
    ALLURE_REPORT_LINK = "${BUILD_URL}/allure/"
  }
  stages {
    stage('Install requirements') {
      steps {
        sh 'pip3 install --no-cache-dir -r ${AUTOMATION_PATH}requirements.txt'
      }
    }
    stage('Run test') {
      steps {
        script {
          TESTBED_CONFIG = "resources/testbeds/${params.TEST_ENVIRONMENT}.yml"
          VALIDATION_CONFIG = "resources/validation/validation_config.yml"
          sh """
            cd ${AUTOMATION_PATH}
            python3 -m pytest -v  --testbed=${TESTBED_CONFIG} --validationConfig=${VALIDATION_CONFIG} --alluredir=target/allure_reports  test/test_groovy_api.py
          """
        }
      }
    }
  }
   post {
    always {
      script{
        allure includeProperties: false, jdk: '', results: [[path: "${ALLURE_REPORT}"]]
      }
    }
  }
}