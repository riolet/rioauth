import common
import base


class ChangePassword(base.LoggedInPage):
    def __init__(self):
        base.LoggedInPage.__init__(self, 'Change Password')
        self.user = None
        self.new_password = None

    def validate_passwords(self):
        old_pass = self.data.get('old_password')
        new_pass = self.data.get('password')
        confirm_pass = self.data.get('confirmpassword')
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
        try:
            common.users.set_password(self.user['id'], self.new_password)
        except common.ValidationError as e:
            self.errors.append("Error: {0}".format(e.message))
            return False
        return True

    def GET(self):
        # get user info
        self.user = self.get_user(self.user_id)

        return common.render.changepassword(self.user, self.errors)

    def POST(self):
        # get user info
        self.user = self.get_user(self.user_id)

        # change password
        if self.validate_passwords():
            if self.change_password():
                return common.render.message(success=['Password changed successfully'])

        return common.render.changepassword(self.user, self.errors)
