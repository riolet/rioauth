import json
import web
import common
from oauthlib.oauth2 import WebApplicationServer
from request_validator import MyRequestValidator
import base


class Resource(base.Page):
    def __init__(self):
        base.Page.__init__(self, 'Resource')
        self._token_endpoint = WebApplicationServer(MyRequestValidator())
        self.token = None
        self.get_bearer_token()

    def get_bearer_token(self):
        if 'token' in self.data:
            access_token = self.data['token']
            return common.bearer_tokens.get(access_token)
        return None

    def GET(self):
        web.header("Content-Type", "application/json")
        return json.dumps({'Status': 'Success'})

    def POST(self):
        web.header("Content-Type", "application/json")
        print(self.token)
        print('')
        return json.dumps({'Status': 'Success'})