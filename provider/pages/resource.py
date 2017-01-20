import json
import web
import common
from oauthlib.oauth2 import WebApplicationServer
from request_validator import MyRequestValidator


class Resource:
    def __init__(self):
        self.data = web.input()
        self._token_endpoint = WebApplicationServer(MyRequestValidator())
        self.token = None
        self.get_bearer_token()

    def get_bearer_token(self):
        if 'token' in self.data:
            access_token = self.data['token']
            return common.bearer_tokens.get(access_token)
        return None

    def GET(self):
        common.report_init('RESOURCE', 'GET', self.data)
        web.header("Content-Type", "application/json")
        return json.dumps({'Status': 'Success'})

    def POST(self):
        common.report_init('RESOURCE', 'POST', self.data)
        web.header("Content-Type", "application/json")
        print(self.token)
        print('')
        return json.dumps({'Status': 'Success'})