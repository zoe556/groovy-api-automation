
pipeline {
  agent  any
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
        sh """
          cd ${AUTOMATION_PATH}
          python -m pytest -v  --alluredir=target/allure_reports  test/test_groovy_api.py
        """
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