import json
import web
import common
from oauthlib.oauth2 import WebApplicationServer
from request_validator import MyRequestValidator
import base


class Resource(base.Page):
    def __init__(self):
        base.Page.__init__(self, 'Resource')
        self.scopes = []
        self.oauthServer = WebApplicationServer(MyRequestValidator())
        self.token = self.get_bearer_token()

    def get_bearer_token(self):
        if 'token' in self.data:
            access_token = self.data['token']
            return common.bearer_tokens.get(access_token)
        return None

    def prepare_response(self):
        response = {}
        keys = ['id', 'email', 'name', 'groups', 'last_access']
        self.user = self.get_user(self.user_id, what=keys)
        subscription = common.subscriptions.get(self.app_id, self.user_id)
        if subscription:
            response['status'] = 'success'
            response['subscription'] = dict(subscription)
            response['user'] = dict(self.user)
        else:
            response['status'] = 'failed'
            response['message'] = 'Subscription not found.'
        return response

    def GET(self):
        # WSGI saves headers under different names than standard http.
        # For details, see:
        # https://www.python.org/dev/peps/pep-0333/#environ-variables
        self.headers['Authorization'] = self.headers.pop('HTTP_AUTHORIZATION', '')

        # raises 403 Forbidden if authentication fails.
        self.require_oauthentication(self.oauthServer, scopes_required=['basic'])

        print("Resource is Authorized!")
        self.app_id = self.request.client_id
        self.user_id = self.request.user
        self.scopes = self.request.scopes

        response = self.prepare_response()

        web.header("Content-Type", "application/json")
        return json.dumps(response)
