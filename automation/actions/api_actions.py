import logging
import requests



class ApiActions:
    """
    Api actions class that contains methods corresponding to APIs testing
    """

    def __init__(self, env_config, validation_config):
        self.logger = logging.getLogger(__name__)
        self.validation_config = validation_config
        self.endpoint = env_config["endpoint"]
        self.username = env_config["username"]
        self.password= env_config["password"]
        self.default_code = "2 + 2"
        self.headers = {"Content-Type": "application/json"}

    def get_submit_code_response(self, auth=None, code=None):
        """
        Get the response for submit execution code
        :param auth: the auth username and password
        :type auth: tuple
        :param code: the code submit for execution
        :type code: str
        :return: dictionary of response of the request
        """
        if auth is None:
            auth = (self.username, self.password)
        if code is None:
            code = self.default_code
        url = self.endpoint + "/groovy/submit"
        payload = {"code": code}
        response = requests.post(
            url=url, auth=auth, headers=self.headers, json=payload
        )
        return response

    def get_query_result_response(self, request_id, auth=None):
        """
        Get response for get result of the submitted request query
        :param request_id: ID of the submitted request query
        :type request_id: str
        :param auth: the auth username and password
        :type auth: tuple
        :return: dictionary of response of the query result
        """
        if auth is None:
            auth = (self.username, self.password)
        url = self.endpoint + "/groovy/status?id=" + request_id
        response = requests.get(url, auth=auth, headers=self.headers)
        return response

    def submit_code_and_require_result(self, auth=None, code=None):
        """
        Submit code and get result of the query
        :param auth: the auth username and password
        :type auth: tuple
        :param code: the code submit for execution
        :type code: str
        :return: dictionary of response of the query result
        """
        if auth is None:
            auth = ('user_1', "pass_1")
        if code is None:
            code = self.default_code
        submit_response = self.get_submit_code_response(auth=auth, code=code)
        assert submit_response.status_code == 200, "%s: %s" % (submit_response.reason, submit_response.content)
        # Ensure the ID returned successful
        assert "id" in submit_response.json()
        # Get the ID of the request
        request_id = submit_response.json()["id"]
        # Get the request result
        result_response  = self.get_query_result_response(auth=auth, request_id=request_id)
        assert result_response.status_code == 200, "%s: %s" % (result_response.reason, result_response.content)
        # Ensure that the response has the correct ID
        assert result_response.json()["id"] == request_id
        return result_response
