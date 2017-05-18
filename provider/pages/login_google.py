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
        self.redirect_uri = unicode(constants.config.get('google', 'redirect_uri'))
        self.scope = unicode(constants.config.get('google', 'request_scope'))
        self.oauth = oauth_consumer.Authorization(
            session=common.session,
            authorization_url=constants.config.get('google', 'authorization_url'),
            token_url=constants.config.get('google', 'token_url'),
            client_id=constants.config.get('google', 'client_id'),
            client_secret=constants.config.get('google', 'client_secret'),
            default_redirect_uri=constants.config.get('google', 'redirect_uri'),
            default_scope_requested=constants.config.get('google', 'request_scope'))

    def get_token(self):
        authorization_response = self.uri

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
        user_info = self.oauth.request(constants.config.get('google', 'resource_url'))

        # user_info should be a dict like the following:
        # {
        #  "family_name": "Doe",
        #  "name": "J Doe",
        #  "picture": "https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg",
        #  "email": "jdoe@example.com",
        #  "given_name": "J",
        #  "id": "112792919567704030902",
        #  "hd": "example.com",
        #  "verified_email": true
        # }

        email = user_info['email']
        name = user_info['name']

        user = common.users.get_by_email(email)
        if user is None:
            # create user for that email!
            # random password. Nobody should know it, ever. Login is done through Google.
            # If user wants to choose password, they will reset it anyway.
            user_id = common.users.add(email, common.generate_salt(32), name)
            user = common.users.get_by_id(user_id)
        self.user = user
        return True

    def GET(self):
        if 'state' in self.data and 'code' in self.data:
            print("state and code found. Assuming to be at fetch_token step.")
            if self.get_token():
                print("get_token returned True. setting logged_in to True")
                success = self.login()
                if not success:
                    print("should render page with errors: {}".format(self.errors))
                    self.redirect('/login')
                common.session['logged_in'] = True
                common.session['user_id'] = self.user['id']
                destination = '/'
                if 'login_redirect' in common.session:
                    destination = common.session['login_redirect']
                self.redirect(destination, absolute=True)
            else:
                print("get_token returned False. setting logged_in to False")
                common.session['logged_in'] = False
                self.redirect('/login')

        elif 'error' in self.data:
            print("Error response.\n\t{0}".format(self.data['error']))
            print("Data: ")
            print(dict(self.data))

            return common.render.message(
                error=['Error logging in via GitHub.', 'Error: {}'.format(self.data['error_description'])],
                buttons=[('Login page', '/logout')])

        else:
            print("begin authentication process.")
            self.get_auth_code()

        # this code should be unreachable.
        self.redirect('/login')
