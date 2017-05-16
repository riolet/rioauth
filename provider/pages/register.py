import web
import common
import base


class Register(base.Page):
    def __init__(self):
        base.Page.__init__(self, "Register")

    def GET(self):
        # show login page
        return common.render.register()

    @staticmethod
    def send_conf_email(user_id, name, email):

        duration = 1800  # 30 minutes
        key = common.email_loopback.add(user_id, '/login', duration=duration)
        subject = "Riolet Registration"
        link = "{uri_prefix}/confirmemail?key={key}".format(
            uri_prefix=web.ctx.home,
            key=key)
        body = """
Hello, {name}

Thank you for registering with Riolet. To complete your registration, please follow the link below:

{link}

This link will be valid for the next {duration} minutes. If it expires, you will need to register again.

Thanks,
Riolet
""".format(name=name, link=link, duration=duration/60)
        common.sendmail(email, subject, body)

    def POST(self):
        email = self.data.get('email')
        name = self.data.get('name')
        password = self.data.get('password')
        confirmpassword = self.data.get('confirmpassword')

        if not email or not name or not password or not confirmpassword:
            self.errors.append('Error processing form.')
            return common.render.register(self.errors)

        if password != confirmpassword:
            self.errors.append("Passwords don't match")
            return common.render.register(self.errors)

        try:
            self.user_id = common.users.add(email, password, name)
        except (common.ValidationError, KeyError) as e:
            self.errors.append('Error: {0}'.format(e.message))
            return common.render.register(self.errors)

        # send the user an email to have the use confirm their email address
        self.send_conf_email(self.user_id, name, email)

        # send them back to the login page
        self.redirect('/login?register=success')
