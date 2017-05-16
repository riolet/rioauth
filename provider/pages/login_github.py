import web
import oauthlib.oauth2.rfc6749
import constants
import common
import base
import logging
import pprint
from models import oauth_consumer


class Login(base.Page):
    def __init__(self):
        base.Page.__init__(self, "Riolet Login")
        self.redirect_uri = unicode(constants.config.get('github', 'redirect_uri'))
        self.scope = unicode(constants.config.get('github', 'request_scope'))
        self.oauth = oauth_consumer.Authorization(
            session=common.session,
            authorization_url=constants.config.get('github', 'authorization_url'),
            token_url=constants.config.get('github', 'token_url'),
            client_id=constants.config.get('github', 'client_id'),
            client_secret=constants.config.get('github', 'client_secret'),
            default_redirect_uri=constants.config.get('github', 'redirect_uri'),
            default_scope_requested=constants.config.get('github', 'request_scope'))

    def get_token(self):
        authorization_response = "{scheme}://{host}{port}{path}".format(
            scheme=web.ctx.env.get('wsgi.url_scheme', 'https'),
            host=web.ctx.env['SERVER_NAME'],
            port=':{0}'.format(web.ctx.env['SERVER_PORT']),
            path=web.ctx.env['REQUEST_URI'])
        try:
            # redirect_uri must match between get_auth_code and get_token.
            # scope must match between get_auth_code and get_token
            token = self.oauth.fetch_token(authorization_response, redirect_uri=self.redirect_uri, scope=self.scope)
        except oauthlib.oauth2.rfc6749.errors.AccessDeniedError:
            print("Access was denied. Reason unknown.")
            return False
        except oauthlib.oauth2.rfc6749.errors.InvalidGrantError:
            print("Access was denied. Error: Invalid Grant.")
            return False

        print("\n\nToken acquired!")
        pprint.pprint(token)
        print("")
        return True

    def get_auth_code(self):
        print("redirect_uri is {0}".format(self.redirect_uri))
        # redirect_uri must match between get_auth_code and get_token.
        # scope must match between get_auth_code and get_token
        authorization_url = self.oauth.get_auth_url(redirect_uri=self.redirect_uri, scope=self.scope)
        print("redirecting to {0}".format(authorization_url))
        self.redirect(authorization_url)

    def login(self):
        resource = self.oauth.request(constants.config.get('github', 'resource_url'))
        pprint.pprint(resource)

        user = common.users.get_by_email()
        if user is None:
            # create user for that email!
            self.errors.append("User didn't exist.")
            return False
        self.user = user
        return True

    def errorpage(self):
        head = """<!DOCTYPE html><html lang="en-CA"><head><meta charset="utf-8"/><title>Errors</title></head><body>\n<table>\n"""
        foot = """</table>\n</body></html>"""
        body = ""
        for k, v in self.data.items:
            body += "<tr><td>{key}</td><td>{value}</td></tr>\n".format(key=k, value=v)
        return head+body+foot

    def GET(self):
        if 'state' in self.data and 'code' in self.data:
            print("state and code found. Assuming to be at fetch_token step.")
            if self.get_token():
                print("get_token returned True. setting logged_in to True")
                success = self.login()
                if success:
                    common.session['logged_in'] = True
                    common.session['user_id'] = self.user['id']
                    self.redirect('/account')
                else:
                    print("should render page with errors: {}".format(self.errors))
                    self.redirect('/login')
            else:
                print("get_token returned False. setting logged_in to False")
                common.session['logged_in'] = False
                self.redirect('/login')
        elif 'error' in self.data:
            print("Error response.\n\t{0}".format(self.data['error']))
            if 'error_description' in self.data:
                print("\t{0}".format(self.data['error_description']))
            # TODO: have destination page indicate to user that an error has occurred.
            # self.redirect('/login')
            return self.errorpage()
        else:
            print("begin authentication process.")
            self.get_auth_code()

        # this code should be unreachable.
        self.redirect('/login')
