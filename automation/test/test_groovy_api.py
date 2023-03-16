import random
import time
import pytest
from concurrent.futures import ThreadPoolExecutor
from actions.api_actions import ApiActions


class TestGroovyApi:
    """
    Test cases for testing API
    """
    @pytest.fixture(scope="session")
    def api_actions(self, env_config, validation_config):
        """
         Get API actions
        :return: API object
        """
        return ApiActions(env_config, validation_config)

    def test_submit_code_execution_with_valid_auth(self, api_actions):
        """ Test submit a code execution request with valid auth user"""
        code = "1 + 513"
        auth = tuple(random.choice(api_actions.validation_config['auth_users']))
        submit_response = api_actions.get_submit_code_response(code=code, auth=auth)
        # Check that the response is successful and contains an ID
        assert submit_response.status_code == 200, "%s: %s" % (submit_response.reason, submit_response.content)
        assert "id" in submit_response.json()

    def test_submit_code_execution_with_invalid_auth(self, api_actions):
        """Test submit a code execution request with invalid auth username and password"""
        auth = ('invalid_user', 'invalid_pass')
        code = '1 + 26666'
        response = api_actions.get_submit_code_response(code=code, auth=auth)
        # Check that the request returns a 401 error
        assert response.status_code == 401

    def test_submit_code_execution_with_invalid_user(self, api_actions):
        """Test submitting a code execution request with invalid username"""
        auth = ('invalid_user', 'pass_1')
        code = '1 + 297670376'
        response = api_actions.get_submit_code_response(code=code, auth=auth)
        # Check that the request returns a 401 error
        assert response.status_code == 401

    def test_submit_code_execution_with_invalid_password(self, api_actions):
        """Test submitting a code execution request with invalid password"""
        auth = ('user_4', 'pass_1')
        code = '1 + 45757'
        response = api_actions.get_submit_code_response(code=code, auth=auth)
        # Check that the request returns a 401 error
        assert response.status_code == 401

    def test_submit_code_execution_with_invalid_code(self, api_actions):
        """Test submitting execution request with invalid code"""
        code = api_actions.validation_config['invalid_code'][1]
        request_result = api_actions.submit_code_and_require_result(code=code)
        time.sleep(1)
        # Check that the response status and a result
        assert request_result.status_code == 200, "%s: %s" % (request_result.reason,request_result.content)
        assert "status" in request_result.json()
        assert request_result.json()["status"] in ("FAILED", "PENDING", 'IN_PROGRESS')

    def test_submit_code_with_special_characters(self, api_actions):
        """Test submitting execution request with special characters"""
        code = api_actions.validation_config['special_characters_codes'][1]
        request_result = api_actions.submit_code_and_require_result(code=code)
        time.sleep(1)
        # Check if server correctly handle it (respond with 200 or 4xx status code)
        assert request_result.status_code in (200, range(400, 500)), \
            "%s: %s" % (request_result.reason,request_result.content)

    def test_query_result_with_same_user(self, api_actions):
        """Test query execution result available for the user who submitted the query """
        code = "6 + 8"
        execution_status = api_actions.validation_config['execution_status']
        request_result = api_actions.submit_code_and_require_result(code=code)
        # Ensure that the response has a status and a result
        assert "status" in request_result.json()
        assert request_result.json()["status"] in execution_status
        if request_result.json()['status'] == 'COMPLETED':
            assert 'result' in request_result.json()
            assert request_result.json()['result'] == '14'

    def test_query_result_with_different_user(self, api_actions):
        """ Test execution request should not be available to the user different with who submitted the request """
        code = "1 + 57658"
        auth_1 = ('user_1', 'pass_1')
        auth_2 = ('user_2', 'pass_2')
        submit_response = api_actions.get_submit_code_response(code=code, auth=auth_1)
        assert submit_response.status_code == 200, \
            "%s: %s" % (submit_response.reason, submit_response.content)
        request_id = submit_response.json()['id']
        # Try to check the status of the request using user 2's credentials
        request_status_response = api_actions.get_query_result_response(request_id, auth_2)
        assert request_status_response.status_code == 401

    def test_query_result_with_not_exist_id(self, api_actions):
        """Test querying request status with not exist ID"""
        request_id = 'ef81a976-4dee-4a91-b5ac-7ff0da3c2913'
        response = api_actions.get_query_result_response(request_id=request_id)
        # Check that the request returns a 404 error
        assert response.status_code == 404

    def test_query_result_with_invalid_id(self, api_actions):
        """Test querying request status with invalid ID"""
        request_id = 'invalid_id'
        response = api_actions.get_query_result_response(request_id=request_id)
        # Check that the request returns a 400 error
        assert response.status_code == 400

    def test_two_requests_execute_parallel(self, api_actions):
        """Test two requests sending at same time, executing parallel"""
        # create 2 test codes to
        codes = ["5 * 5", "7 * 7"]
        # send the requests at same time to the service using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(api_actions.submit_code_and_require_result,(f"user_{i+1}", f"pass_{i+1}"), code)
                for i, code in enumerate(codes)]
        # check the two tasks status
        status_1 = futures[0].result().json()["status"]
        assert status_1 in ("COMPLETED", 'IN_PROGRESS')
        status_2 = futures[1].result().json()["status"]
        assert status_2 in ("COMPLETED", 'IN_PROGRESS' )

    def test_five_requests_submit_simultaneously(self, api_actions):
        """Test send five requests sending parallel"""
        execution_status =  api_actions.validation_config['execution_status']
        # Get test codes from validation file
        codes = list(api_actions.validation_config['sample_codes'][:5])
        # submit the requests to the service using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(api_actions.submit_code_and_require_result, (f"user_{i + 1}", f"pass_{i + 1}"), code)
                for i, code in enumerate(codes)]
        for i in range(5):
            # Check the execution results
            result_response = futures[i].result()
            assert result_response.status_code == 200, "%s: %s" % (result_response.reason, result_response.content)
            assert result_response.json()["status"] in execution_status

    def test_submit_long_execution_code(self, api_actions):
        """ Test user submits long execution code """
        # Read code from test_data file
        file_name = api_actions.validation_config['test_file_name']
        with open('resources/test_data/%s' % file_name) as code_file:
            code = code_file.read()
        submit_response = api_actions.get_submit_code_response(code=code)
        # Check if server correctly handle it (respond with 200 or 4xx status code)
        assert submit_response .status_code in (200, range(400, 500)), \
            "%s: %s" % (submit_response .reason, submit_response .content)

    def test_submit_repeated_code(self, api_actions):
        """ Test users submit repeated code """
        code = "5 * 513"
        for i in range(3):
            # Random pick up a user for test
            auth = tuple(random.choice(api_actions.validation_config['auth_users']))
            submit_response = api_actions.get_submit_code_response(code=code, auth=auth)
            # Check that the response is successful and contains an ID
            assert submit_response.status_code == 200, "%s: %s" % (submit_response.reason, submit_response.content)
            assert "id" in submit_response.json()
