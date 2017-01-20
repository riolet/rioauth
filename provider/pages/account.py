import web
import constants
import common


class Account(object):
    def __init__(self):
        self.data = web.input()
        self.user_id = None
        self.user_data = None
        self.is_admin = False

    def is_logged_in(self):
        if 'logged_in' in common.session and 'user_id' in common.session and common.session['logged_in'] is True:
            self.user_id = common.session['user_id']
            return True
        else:
            return False

    def require_login(self, return_uri):
        if not self.is_logged_in():
            common.session['login_redirect'] = return_uri
            raise web.seeother("/login")
        else:
            common.session.pop('login_redirect', None)

    def is_user_admin(self, user):
        groups = user['groups'].split(' ')
        return 'admin' in groups

    def get_user_data(self, user_id):
        user = dict(common.users.get_by_id(user_id))

        # accessible apps
        subs = common.subscriptions.get_by_user(user_id)
        user['subscriptions'] = map(dict, subs)

        # owned apps
        apps = common.applications.get_all_by_owner(user_id)
        user['apps'] = apps

        return user

    def GET(self):
        common.report_init("HOME", "GET", self.data)
        self.require_login("/")

        self.user_data = self.get_user_data(self.user_id)
        self.is_admin = self.is_user_admin(self.user_data)

        return common.render.account(self.user_data, self.is_admin)

    def POST(self):
        common.report_init("HOME", "POST", self.data)
        self.require_login("/")

        if 'enable_sub' in self.data:
            common.subscriptions.set_status(self.data['enable_sub'], self.user_id, "active")
        if 'disable_sub' in self.data:
            common.subscriptions.set_status(self.data['disable_sub'], self.user_id, "inactive")

        self.user_data = self.get_user_data(self.user_id)
        self.is_admin = self.is_user_admin(self.user_data)

        return common.render.account(self.user_data, self.is_admin)
