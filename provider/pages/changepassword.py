import web
import common


class ChangePassword(object):
    def __init__(self):
        self.data = web.input()
        self.errors = []
        self.user_id = None
        self.user = None
        self.new_password = None
        self.errors = []

    def is_logged_in(self):
        if 'logged_in' in common.session and 'user_id' in common.session and common.session['logged_in'] is True:
            self.user_id = common.session['user_id']
            return True
        else:
            return False

    def require_login(self):
        if not self.is_logged_in():
            common.session['login_redirect'] = self.uri
            raise web.seeother("/login")
        else:
            common.session.pop('login_redirect', None)

    def validate_passwords(self):
        old_pass = self.data.get('password')
        new_pass = self.data.get('new_password')
        confirm_pass = self.data.get('confirm_new_password')
        old_user = common.users.get(self.user['email'], old_pass)
        if not old_user or old_user['id'] != self.user['id']:
            self.errors.append('Error: Current password incorrect')
            return False

        if new_pass != confirm_pass:
            self.errors.append('Error: Passwords do not match')
            return False

        self.new_password = new_pass
        return True

    def change_password(self):
        common.users.set_password(self.user['id'], self.new_password)

    def get_user(self, user_id):
        user = dict(common.users.get_by_id(user_id))
        return user

    def GET(self):
        common.report_init('CHANGEPASSWORD', 'GET', self.data)

        # require user_id to be defined.
        self.require_login()

        # get user info
        self.user = self.get_user(self.user_id)

        return common.render.changepassword(self.user, self.errors)

    def POST(self):
        common.report_init('CHANGEPASSWORD', 'POST', self.data)

        # require user_id to be defined.
        self.require_login()

        # get user info
        self.user = self.get_user(self.user_id)

        # change password
        if self.validate_passwords():
            self.change_password()
            return common.render.message(success=['Password changed successfully'])

        return common.render.changepassword(self.user, self.errors)
