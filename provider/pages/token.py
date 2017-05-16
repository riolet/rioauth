import common
from oauthlib.oauth2 import WebApplicationServer
from request_validator import MyRequestValidator
import base


class Token(base.Page):
    def __init__(self):
        base.Page.__init__(self, "Token")
        self.oauthServer = WebApplicationServer(MyRequestValidator())

    def POST(self):
        # If you wish to include request specific extra credentials for
        # use in the validator, do so here.
        credentials = {
            # 'foo': 'bar'
        }

        headers, body, status = self.oauthServer.create_token_response(
            self.uri, self.http_method, self.body, self.headers, credentials)

        # All requests to /token will return a json response, no redirection.
        return common.response_from_return(headers, body, status)
