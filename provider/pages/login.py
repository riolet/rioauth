import web
import constants
import common
import base


class Login(base.Page):
    def __init__(self):
        base.Page.__init__(self, "Riolet Login")
        self.user = None

    def save_cookie(self, account_id):
        print("Saving, for remembering later.")
        cookie_text = common.users.get_login_cookie(account_id)
        duration = 31536000  # 60*60*24*365 # 1 year-ish
        # TODO: does the domain or path need to be set?
        web.setcookie(constants.REMEMBER_COOKIE_NAME, cookie_text, expires=duration, domain=constants.DOMAIN, path="/", secure=True, httponly=True)

    def read_cookie(self):
        # Must be able to read cookie
        cookie = web.cookies().get(constants.REMEMBER_COOKIE_NAME)
        if not cookie:
            return

        # Cookie must have three parts
        cookie_parts = cookie.split(":")
        if len(cookie_parts) != 3:
            return

        # Cookie hash must be calculated the same on both ends.
        uid, token, _hash = cookie_parts
        if not common.users.validate_login_cookie(uid, token, _hash):
            return

        # logged in!
        common.session['logged_in'] = True
        common.session['user_id'] = uid
        return

    def try_login(self):
        email = self.data.get('email')
        password = self.data.get('password')
        if not email or not password:
            self.errors.append("Form data missing. Please fill all the fields and try again.")
            return False

        user = common.users.get(email, password)
        if user is None:
            self.errors.append("Incorrect email or password.")
            return False
        elif user.email_confirmed == '0':
            self.errors.append("Please confirm your email address before logging in.")
            return False

        self.user = user
        return True

    def GET(self):
        # log in by cookie, if appropriate
        self.read_cookie()

        # if already logged in, redirect
        if self.is_logged_in():
            destination = '/'
            if 'login_redirect' in common.session:
                destination = common.session['login_redirect']
            raise web.seeother(destination)

        # show login page
        if 'register' in self.data and self.data['register'] == 'success':
            return common.render.login(new_register=True)
        else:
            return common.render.login()

    def POST(self):
        success = self.try_login()

        if not success:
            common.render.login(self.errors)

        common.session['user_id'] = self.user['id']
        common.session['logged_in'] = True
        if self.data.get('remember', " ") == "True":
            self.save_cookie(self.user['id'])

        # send them back where they came from
        destination = '/'
        if 'login_redirect' in common.session:
            destination = common.session['login_redirect']
        raise web.seeother(destination)

