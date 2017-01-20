import web
import common
from oauthlib.oauth2 import WebApplicationServer
from request_validator import MyRequestValidator
import oauthlib.oauth2.rfc6749.errors as errors
import web.webapi

class Authorize(object):
    def __init__(self):
        self.data = web.input()
        self._authorization_endpoint = WebApplicationServer(MyRequestValidator())
        self.user_id = None
        self.client_id = None
        self.uri, self.http_method, self.body, self.headers = self.extract_params()

    def is_logged_in(self):
        if 'logged_in' in common.session and 'user_id' in common.session and common.session['logged_in'] is True:
            self.user_id = common.session['user_id']
            return True
        else:
            return False

    def is_subscribed(self):
        subscription = common.subscriptions.get(self.data['client_id'], self.user_id)
        if subscription:
            self.subscription_id = subscription['subscription_id']
            return subscription['status'] == 'active'
        else:
            return False

    def validate_application(self):
        try:
            # begin authorization sequence
            uri, http_method, body, headers = self.extract_params()
            scopes, credentials = self._authorization_endpoint.validate_authorization_request(
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

    def extract_params(self):
        # TODO: host should be web.ctx.env['SERVER_NAME']
        # but that doesn't work for testing here.
        uri = "{scheme}://{host}{port}{path}".format(
            scheme=web.ctx.env.get('wsgi.url_scheme', 'http'),
            host='auth.local',  # web.ctx.env['SERVER_NAME'],
            port=':{0}'.format(web.ctx.env['SERVER_PORT']),
            path=web.ctx.env['REQUEST_URI']
        )
        http_method = web.ctx.environ["REQUEST_METHOD"]
        body = web.ctx.get('data', '')
        headers = web.ctx.env.copy()
        headers.pop("wsgi.errors", None)
        headers.pop("wsgi.input", None)

        return uri, http_method, body, headers

    def save_auth_state(self, credentials, scopes):
        # Store some important information for later.
        # Not necessarily in session but they need to be
        # accessible in the POST view after form submit.
        # NOTE: I need to remove "request" because it contains custom data structures
        # and fails to be properly pickled into the session storage
        common.session['oauth2_credentials'] = credentials
        common.session['oauth2_scopes'] = scopes

    def require_login(self):
        if not self.is_logged_in():
            common.session['login_redirect'] = self.uri
            raise web.seeother("/login")
        else:
            common.session.pop('login_redirect', None)

    def require_subscription(self):
        if not self.is_subscribed():
            common.session['subscribe_redirect'] = self.uri
            raise web.seeother('/subscribe?app_id={0}'.format(self.data['client_id']))
        else:
            common.session.pop('subscribe_redirect', None)

    def create_authorization_token(self):
        try:
            headers, body, status = self._authorization_endpoint.create_authorization_response(
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
        common.report_init("AUTHORIZE", "GET", self.data)

        self.require_login()
        print("\nAUTHORIZE: Logged in\n")

        self.validate_application()
        print("\nAUTHORIZE: Validated\n")

        self.require_subscription()
        print("\nAUTHORIZE: Subscribed\n")

        # if we got this far, the user is logged in, the request is valid,
        # and the user is subscribed to (may access) the app.
        # If any of the above checks failed, the user would be redirected to another page.
        self.create_authorization_token()

    def POST(self):
        common.report_init("AUTHORIZE", "POST", self.data)
        self.GET()
