import traceback
import web
import constants
import common
from oauthlib.oauth2 import WebApplicationServer
from request_validator import MyRequestValidator
import oauthlib.oauth2.rfc6749.errors as errors


class Authorize(object):
    def __init__(self):
        print("assigning server")
        self._authorization_endpoint = WebApplicationServer(MyRequestValidator())
        print("finished init")

    def get_user_id(self):
        if "logged_in" in common.session and common.session['logged_in'] is True and "user_id" in common.session:
            return common.session['user_id']

        cookie = web.cookies().get(constants.REMEMBER_COOKIE_NAME)
        if cookie:
            cookie_parts = cookie.split(":")
            if len(cookie_parts) == 3:
                uid, token, hash = cookie_parts
                if common.users.validate_login_cookie(uid, token, hash):
                    common.session['logged_in'] = True
                    common.session['user_id'] = uid
                    return uid
        return None

    def GET(self):
        data = web.input()
        common.report_init("AUTHORIZE", "GET", data)
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

        try:
            scopes, credentials = self._authorization_endpoint.validate_authorization_request(
                uri, http_method, body, headers)

            # Store some important information for later.
            # Not necessarily in session but they need to be
            # accessible in the POST view after form submit.
            # NOTE: I need to remove "request" because it contains custom data structures
            # and fails to be properly pickled into the session storage
            credentials.pop("request", None)
            common.session['oauth2_credentials'] = credentials
            common.session['oauth2_scopes'] = scopes
            common.session['login_redirect'] = uri

            # Display authorization page
            user_id = self.get_user_id()
            if user_id:
                user = common.users.get_by_id(user_id)
                app = common.applications.get(credentials['client_id'])
                # if logged in, display authorization page
                credentials['user'] = user_id
                return common.render.authorize(user.name, app.nicename)
            else:
                # otherwise, display login page
                print("redirecting to /login")
                raise web.seeother("/login")

        # Errors that should be shown to the user on the provider website
        except errors.FatalClientError as e:
            return common.response_from_error(e)
        # Errors embedded in the redirect URI back to the client
        except errors.OAuth2Error as e:
            raise web.seeother(e.in_uri(e.redirect_uri))

        # Something else went wrong.
        except Exception:
            print(" Something went wrong. ".center(70, '='))
            traceback.print_exc()
        return "Error. Reached end of authorization code"

    def POST(self):
        data = web.input()
        common.report_init("AUTHORIZE", "POST", data)
        uri = "{scheme}://{host}{port}{path}".format(
            scheme=web.ctx.env.get('wsgi.url_scheme', 'http'),
            host=web.ctx.env['SERVER_NAME'],
            port=':{0}'.format(web.ctx.env['SERVER_PORT']),
            path=web.ctx.env['REQUEST_URI']
        )
        http_method = web.ctx.environ["REQUEST_METHOD"]
        body = web.ctx.get('data', '')
        headers = web.ctx.env.copy()
        headers.pop("wsgi.errors", None)
        headers.pop("wsgi.input", None)

        # Did the user approve access?
        approved = data.get('approved') == "yes"

        # TODO: What if approved is not True?
        # Extra credentials we need in the validator
        credentials = {'user': self.get_user_id()}

        # The previously stored (in authorization GET view) credentials
        # probably contains: 'state', 'redirect_uri', 'response_type', 'client_id'
        credentials.update(common.session.get('oauth2_credentials', {}))
        scopes = common.session.get('oauth2_scopes', [])

        try:
            print("creating authorization response\n")
            headers, body, status = self._authorization_endpoint.create_authorization_response(
                uri, http_method, body, headers, scopes, credentials)
            print("\nauthorization response created")
            if headers.keys() == ['Location'] and status in (302, 303):
                print("Redirecting to {0}".format(headers['Location']))
                raise web.seeother(headers['Location'], absolute=True)
            else:
                return common.response_from_return(headers, body, status)

        except errors.FatalClientError as e:
            return common.response_from_error(e)
