import common
import base


class Account(base.LoggedInPage):
    def __init__(self):
        base.LoggedInPage.__init__(self, "Home page")
        self.user_data = None
        self.is_admin = False

    def is_user_admin(self, user):
        return self.is_in_group(user, 'admin')

    def render_page(self):
        self.user_data = self.get_user_data(self.user_id)
        self.is_admin = self.is_user_admin(self.user_data)
        return common.render.account(self.user_data, self.is_admin)

    def GET(self):
        try:
            page = self.render_page()
        except:
            page = common.render.message(error=['Error accessing account. Please try logging in again'], buttons=[('Login page', '/logout')])
        return page

    def POST(self):
        if 'enable_sub' in self.data:
            common.subscriptions.set_status(self.data['enable_sub'], self.user_id, "active")
        if 'disable_sub' in self.data:
            common.subscriptions.set_status(self.data['disable_sub'], self.user_id, "inactive")

        return self.render_page()
