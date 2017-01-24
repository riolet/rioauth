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

    def resend(self):
        redirect_uri = '/'
        user_id = 0
        email = None
        name = ""
        if 'user_id' in self.data and 'redirect_uri' in self.data:
            user_id = self.data['user_id']
            redirect_uri = self.data['redirect_uri']
            user = common.users.get_by_id(user_id)
            if not user:
                self.errors.append("Error: user not found")
                return False
            email = user.email
            name = user.name.title()
        elif 'email' in self.data:
            user = common.users.get_by_email(self.data['email'])
            if not user:
                self.errors.append("Error: email not found")
                return False
            name = user.name.title()
            user_id = user.id
        else:
            self.errors.append("Error: did not understand request.")
            return False

        duration = 1800  # 30 minutes
        key = common.email_loopback.add(user_id, redirect_uri, duration=60*30)

        subject = "Riolet Password Reset"
        link = "https://{domain}{port}/resetpassword?key={key}".format(
            domain=web.ctx.env['SSL_SERVER_S_DN_CN'],
            port= '' if web.ctx.env['SERVER_PORT'] == 443 else ':{0}'.format(web.ctx.env['SERVER_PORT']),
            key=key)
        body = \
"""Hello {name},

You recently request that your password be reset. To reset your password simply follow the link below:

{link}

If you did not request your password be reset, just ignore this email. The reset code will be valid for the next {duration} minutes.

Thanks,
Riolet Corporation
""".format(name=name, link=link, duration=(duration // 60))
        print("password reset link is {0}".format(link))
        common.sendmail(email, subject, body)
        return True

    def updatepassword(self):
        self.validate_key()
        if not self.offer_resend and not self.errors:

            new_pass = self.data.get('password', '')
            confirm_new_pass = self.data.get('confirmpassword', '-1')
            if new_pass != confirm_new_pass:
                self.errors.append("Error: passwords don't match.")
                return False
            success = common.users.set_password(self.loopback['user_id'], new_pass)
            if success:
                common.email_loopback.delete(self.loopback['user_id'])
                return True
            else:
                self.errors.append("Unknown error while updating password")
        return False


    def GET(self):
        common.report_init('RESETPASSWORD', 'GET', self.data)

        self.validate_key()
        # get the code.
        # is expired?
        # if expired:
        #   show message. Offer resend
        # if not expired:
        #   show pass and confirm pass form

        if self.loopback:
            self.user = common.users.get_by_id(self.loopback['user_id'])

        return common.render.resetpassword(self.user, self.loopback, self.offer_resend, self.errors)

    def POST(self):
        common.report_init('RESETPASSWORD', 'POST', self.data)
        intention = self.data.get("intention")

        if intention not in ['resend', 'update']:
            raise web.seeother('/')

        if intention == 'resend':
            success = self.resend()
            if success:
                msg = "Please check your email for your password reset link."
                return common.render.message(success=[msg], buttons=[('Login', '/login')])
            else:
                return common.render.resetpassword(self.user, self.loopback, self.offer_resend, self.errors)

        elif intention == 'update':
            success = self.updatepassword()
            if success:
                msg = "Your password has been successfully changed."
                return common.render.message(success=[msg], buttons=[('Login', '/login')])
            else:
                return common.render.resetpassword(self.user, self.loopback, self.offer_resend, self.errors)

        else:
            web.seeother('/')
