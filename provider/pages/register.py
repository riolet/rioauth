import re
import traceback
import web
import common


class Register(object):
    def GET(self):
        data = web.input()
        common.report_init("LOGIN", "GET", data)
        # show login page
        return common.render.register()

    def validate_pass(self, password):
        return len(password) >= 6

    def validate_email(self, email):
        return bool(re.match(r'^[^@]+@[^\.@]+\.[^@]+$', email))

    def validate_name(self, name):
        return len(name) > 0

    def register_user(self, name, email, password):
        common.users.add(email, password, name=name)

    def POST(self):
        data = web.input()
        common.report_init("LOGIN", "POST", data)

        server_errors = []
        try:
            email = data['email']
            name = data['name']
            password = data['password']
            confirmpassword = data['confirmpassword']
        except KeyError:
            traceback.print_exc()
            server_errors.append('Error processing form.')
            return common.render.register(server_errors)

        if not self.validate_pass(password):
            server_errors.append("Your password must be at least 6 characters")

        if not self.validate_email(email):
            server_errors.append("Please enter a valid e-mail")

        if not self.validate_name(name):
            server_errors.append("Please enter your name")

        if not confirmpassword == password:
            server_errors.append("Passwords don't match")

        if server_errors:
            return common.render.register(server_errors)

        self.register_user(name, email, password)
        # send them back where they came from
        web.seeother('/login?register=success')
