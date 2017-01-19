import traceback
import web
import constants
import common


class AuthenticationError(Exception):
    pass


class Login(object):
    def save_cookie(self, account_id):
        print("Saving, for remembering later.")
        cookie_text = common.users.get_login_cookie(account_id)
        duration = 31536000  # 60*60*24*365 # 1 year-ish
        # TODO: does the domain or path need to be set?
        web.setcookie(constants.REMEMBER_COOKIE_NAME, cookie_text, expires=duration, domain="auth.local", path="/", secure=True, httponly=True)

    def get_user(self, data):
        email = data['email']
        password = data['password']

        user = common.users.get(email, password)
        if user is None:
            raise AuthenticationError("Incorrect email or password.")
        return user

    def GET(self):
        data = web.input()
        common.report_init("LOGIN", "GET", data)
        # show login page
        if 'register' in data and data['register'] == 'success':
            return common.render.login(new_register=True)
        else:
            return common.render.login()

    def POST(self):
        data = web.input()
        common.report_init("LOGIN", "POST", data)

        try:
            user = self.get_user(data)
        except KeyError:
            traceback.print_exc()
            server_errors = ['Error processing form.']
            return common.render.login(server_errors)
        except AuthenticationError:
            traceback.print_exc()
            server_errors = ['Incorrect username or password.']
            return common.render.login(server_errors)

        if user:
            print("Logged in successfully")
            common.session['user_id'] = user['id']
            common.session['logged_in'] = True
            if data.get('remember', " ") == "True":
                self.save_cookie(user['id'])

        # send them back where they came from
        destination = '/'
        if 'login_redirect' in common.session:
            destination = common.session['login_redirect']
        print("redirecting to {0}".format(destination))
        web.seeother(destination)

