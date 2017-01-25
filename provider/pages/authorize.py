import web
import common
from oauthlib.oauth2 import WebApplicationServer
from request_validator import MyRequestValidator
import oauthlib.oauth2.rfc6749.errors as errors
import web.webapi
import base

class Authorize(base.LoggedInPage):

    def __init__(self):
        base.LoggedInPage.__init__(self, 'Authorize')
        self.oauthServer = WebApplicationServer(MyRequestValidator())

    def validate_application(self):
        try:
            # begin authorization sequence
            scopes, credentials = self.oauthServer.validate_authorization_request(
                self.uri, self.http_method, self.body, self.headers)

            self.scopes = scopes
            self.credentials = credentials
            self.credentials['user'] = self.user_id

        # Errors that should be shown to the user on the provider website
        except errors.FatalClientError as e:
            # raises a "bad request" exception page.
            return common.response_from_error(e)
        # Errors embedded in the redirect URI back to the client
        except errors.OAuth2Error as e:
            raise web.seeother(e.in_uri(e.redirect_uri))

        self.client_id = self.credentials['client_id']

    def save_auth_state(self, credentials, scopes):
        # Store some important information for later.
        # Not necessarily in session but they need to be
        # accessible in the POST view after form submit.
        # NOTE: I need to remove "request" because it contains custom data structures
        # and fails to be properly pickled into the session storage
        common.session['oauth2_credentials'] = credentials
        common.session['oauth2_scopes'] = scopes

    def require_subscription(self):
        if not self.is_subscribed():
            common.session['subscribe_redirect'] = self.uri
            raise web.seeother('/subscribe?app_id={0}'.format(self.data['client_id']))
        else:
            common.session.pop('subscribe_redirect', None)

    def create_authorization_token(self):
        try:
            headers, body, status = self.oauthServer.create_authorization_response(
                self.uri, self.http_method, self.body, self.headers, self.scopes, self.credentials)

            print("\nauthorization response created")

            # check for redirection response.
            if headers.keys() == ['Location'] and status in (302, 303):
                print("Redirecting to {0}".format(headers['Location']))
                raise web.seeother(headers['Location'], absolute=True)
            else:
                print("\nAUTHORIZE: Token created\n")
                return common.response_from_return(headers, body, status)

        except errors.FatalClientError as e:
            return common.response_from_error(e)

    def GET(self):
        self.validate_application()

        self.require_subscribed(self.user_id, self.client_id, self.uri)

        # if we got this far, the user is logged in, the request is valid,
        # and the user is subscribed to (may access) the app.
        # If any of the above checks failed, the user would be redirected to another page.
        self.create_authorization_token()
        # all paths in create_authorization_token should raise an exception to redirect the browser.
        return common.render.message(error=['Error. Authorize failed.'])
