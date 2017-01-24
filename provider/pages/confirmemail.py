import web
import common


class ConfirmEmail(object):
    def __init__(self):
        self.data = web.input()
        self.loopback = None

    def get_loopback(self):
        print()
        key = self.data.get('key')
        if not key:
            return

        self.loopback = common.email_loopback.get(key)

    def confirm_email(self):
        print("confirming email")
        user_id = self.loopback['user_id']
        common.users.update(user_id, email_confirmed='1')

    def GET(self):
        common.report_init('CONFIRMEMAIL', 'GET', self.data)
        # get the emailed key info
        self.get_loopback()

        # mark as confirmed if key was valid
        if self.loopback:
            self.confirm_email()

        # show message
        # with link to /login
        if self.loopback:
            return common.render.message(info=['Email confirmed--Thank you!'], buttons=[('Login', '/login')])
        else:
            return common.render.message(error=['Error: Invalid key used.'], buttons=[('Register', '/register')])