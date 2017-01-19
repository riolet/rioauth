import web
import constants
import common


class Account(object):
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

    def GET(self):
        data = web.input()
        common.report_init("HOME", "GET", data)

        user_id = self.get_user_id()
        print("get_user_id returned {0} ({0.__class__})".format(user_id))
        is_logged_in = bool(user_id)
        if is_logged_in:
            user = self.get_user_data(user_id)
            return common.render.account(user)
        else:
            raise web.seeother("/login")