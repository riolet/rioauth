import json
import web
import common
from oauthlib.oauth2 import WebApplicationServer
from request_validator import MyRequestValidator
import base


class Resource(base.Page):
    def __init__(self):
        base.Page.__init__(self, 'Resource')
        self.oauthServer = WebApplicationServer(MyRequestValidator())
        self.token = self.get_bearer_token()

    def get_bearer_token(self):
        if 'token' in self.data:
            access_token = self.data['token']
            return common.bearer_tokens.get(access_token)
        return None

    def GET(self):
        auth = self.headers['HTTP_AUTHORIZATION']
        print("Authorization is {0}".format(auth))

        self.require_oauthentication(self.oauthServer)

        print("Authorized!")
        print(self.request)
        try:
            print(self.request.client)
            print(self.request.user)
            print(self.request.scopes)
        except:
            print("Exception printing request parts")

        web.header("Content-Type", "application/json")
        return json.dumps({'Status': 'Success'})