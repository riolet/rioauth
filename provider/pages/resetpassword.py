import time
import web
import common

class ResetPassword(object):
    def __init__(self):
        self.data = web.input()
        self.errors = []
        self.loopback = None
        self.offer_resend = False
        self.user = None

    def validate_key(self):
        secret_key = self.data.get('key')
        if not secret_key:
            self.errors.append('Error: reset code missing. Please make sure to copy the entire url into the address bar.')
            self.offer_resend = True
            return

        self.loopback = common.email_loopback.get(secret_key)
        if not self.loopback:
            self.errors.append('Error: reset code is invalid')
            self.offer_resend = True
            return

        self.expired = common.email_loopback.is_expired(self.loopback)
        if self.expired:
            self.errors.append('Error: reset code has expired')
            self.offer_resend = True

    def GET(self):
        common.report_init('RESETPASSWORD', 'GET', self.data)

        self.validate_key()
        # get the code.
        # is expired?
        # if expired:
        #   show message. Offer resend
        # if not expired:
        #   show pass and confirm pass form

        self.loopback = {
            'user_id': 1,
            'secret_key': 'abc123',
            'redirect_uri': 'https://auth.local:8081/',
            'expiration_time': (time.time()) + 600
        }

        if self.loopback:
            self.user = common.users.get_by_id(self.loopback['user_id'])

        return common.render.resetpass(self.user, self.loopback, self.offer_resend, self.errors)

    def POST(self):
        common.report_init('RESETPASSWORD', 'POST', self.data)
        # validate user and old pass / code
        #