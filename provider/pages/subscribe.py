import web
import constants
import common


class Subscribe:
    def __init__(self):
        self.user = None
        self.app = None
        self.errors = []
        self.data = web.input()

        allowed = self.authenticate(self.data)
        if not allowed:
            raise web.seeother('/')

    def get_user_id(self):
        if "logged_in" in common.session and common.session['logged_in'] is True and "user_id" in common.session:
            return common.session['user_id']

        cookie = web.cookies().get(constants.REMEMBER_COOKIE_NAME)
        if cookie:
            cookie_parts = cookie.split(":")
            if len(cookie_parts) == 3:
                uid, token, _hash = cookie_parts
                if common.users.validate_login_cookie(uid, token, _hash):
                    common.session['logged_in'] = True
                    common.session['user_id'] = uid
                    return uid
        return None

    def get_user(self, user_id):
        user = dict(common.users.get_by_id(user_id))
        return user

    def validate_sub(self):
        valid = (unicode(self.user['id']) == unicode(self.data['user_id'])
                 and unicode(self.app['app_id']) == unicode(self.data['app_id']))
        return valid

    def add_sub(self, app_id, user_id, sub_type='Basic'):
        try:
            common.subscriptions.add(app_id, user_id, sub_type)
        except:
            self.errors.append("Error adding new subscription")

    def enable_sub(self, app_id, user_id):
        try:
            rowsAffected = common.subscriptions.set_status_by_app_user(app_id, user_id, 'active')
            if rowsAffected == 0:
                self.errors.append("Error: no subscriptions affected")
        except:
            self.errors.append("Error enabling subscription")

    def authenticate(self, data):
        user_id = self.get_user_id()
        if not user_id:
            return False

        user = self.get_user(user_id)
        if not user:
            return False
        self.user = user

        app_id = data.get('app_id', None) or common.session.get('subscribe_app', None)
        if not app_id:
            return False

        app = common.applications.get(app_id)
        if not app:
            return False
        self.app = app

        return True

    def get_sub(self, user_id, app_id):
        return common.subscriptions.get(app_id, user_id)

    def GET(self):
        common.report_init("SUBSCRIBE", "GET", self.data)
        common.session['subscribe_app'] = self.app.app_id

        # if subscription doesn't exist: off subscription
        # if subscription exists and is not active: off enable
        # if subscription exists and is active: redirect to destination
        subscription = common.subscriptions.get(self.app['app_id'], self.user['id'])
        if not subscription:
            return common.render.subscribe(self.user, self.app, "create", self.errors)
        elif subscription['status'] != 'active':
            return common.render.subscribe(self.user, self.app, "enable", self.errors)
        else:
            destination = '/'
            if 'subscribe_redirect' in common.session:
                destination = common.session['subscribe_redirect']
            raise web.seeother(destination)

    def POST(self):
        common.report_init("SUBSCRIBE", "POST", self.data)

        action = self.data.get('action', None)
        print("subscribe action: {0}".format(action))
        if action == 'subscribe':
            print("checking subscribe...")
            if self.validate_sub():
                self.add_sub(self.app['app_id'], self.user['id'])
            else:
                self.errors.append("User and application were mismatched; unable to subscribe. Please try again.")
        if action == 'enable':
            print("checking enable...")
            if self.validate_sub():
                self.enable_sub(self.app['app_id'], self.user['id'])
            else:
                self.errors.append("User and application were mismatched; unable to subscribe. Please try again.")

        if self.errors:
            return common.render.subscribe(self.user, self.app, self.errors)

        destination = '/'
        if 'subscribe_redirect' in common.session:
            destination = common.session['subscribe_redirect']
        raise web.seeother(destination)
        