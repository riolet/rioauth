import web
import constants
import common


class Admin():
    def get_user_id(self):
        if "logged_in" in common.session and common.session['logged_in'] is True and "user_id" in common.session:
            return common.session['user_id']

        cookie = web.cookies().get(constants.REMEMBER_COOKIE_NAME)
        if cookie:
            cookie_parts = cookie.split(":")
            if len(cookie_parts) == 3:
                uid, token, hash = cookie_parts
                if common.users.validate_login_cookie(uid, token, hash):
                    common.session['logged_in'] = True
                    common.session['user_id'] = uid
                    return uid
        return None

    def get_user_data(self, user_id):
        user = dict(common.users.get_by_id(user_id))

        # accessible apps
        subs = common.subscriptions.get_by_user(user_id)
        user['subscriptions'] = map(dict, subs)

        # owned apps
        apps = common.applications.get_by_owner(user_id)
        user['apps'] = apps

        return user

    def is_admin(self, user):
        groups = user['groups'].split(' ')
        return 'admin' in groups

    def get_users(self):
        return common.users.get_all()

    def get_apps(self):
        return common.applications.get_all()

    def get_subs(self):
        return common.subscriptions.get_all()

    def GET(self):
        data = web.input()
        common.report_init("LOGIN", "GET", data)

        user_id = self.get_user_id()
        user = self.get_user_data(user_id)
        is_admin = self.is_admin(user)
        if is_admin:
            users = self.get_users()
            apps = self.get_apps()
            subs = self.get_subs()
            return common.render.admin(user, users, apps, subs)
        else:
            raise web.seeother("/")

    def POST(self):
        data = web.input()
        common.report_init("LOGIN", "GET", data)
        return "Error."