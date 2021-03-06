import web
import common
import base


class Subscribe(base.LoggedInPage):
    def __init__(self):
        base.LoggedInPage.__init__(self, "Subscribe")
        self.user = self.get_user(self.user_id)
        self.app = self.get_app()

        if not self.user or not self.app:
            self.redirect('/')

    def get_app(self):
        app_id = self.data.get('app_id', None) or common.session.get('subscribe_app', None)
        if not app_id:
            return None

        app = common.applications.get(app_id)
        return app

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
            rows_affected = common.subscriptions.set_status_by_app_user(app_id, user_id, 'active')
            if rows_affected == 0:
                self.errors.append("Error: no subscriptions affected")
        except:
            self.errors.append("Error enabling subscription")

    @staticmethod
    def get_sub(user_id, app_id):
        return common.subscriptions.get(app_id, user_id)

    def redirect_back(self):
        destination = '/'
        if 'subscribe_redirect' in common.session:
            destination = common.session['subscribe_redirect']
        self.redirect(destination)


    def GET(self):
        common.session['subscribe_app'] = self.app.app_id

        # if subscription doesn't exist: offer subscription
        # if subscription exists and is not active: offer enable
        # if subscription exists and is active: redirect to destination
        subscription = common.subscriptions.get(self.app['app_id'], self.user['id'])
        if not subscription:
            if self.app['preapprove'] == '1':
                self.add_sub(self.app['app_id'], self.user['id'])
                self.redirect_back()
            else:
                return common.render.subscribe(self.user, self.app, "create", self.errors)
        elif subscription['status'] != 'active':
            return common.render.subscribe(self.user, self.app, "enable", self.errors)
        else:
            self.redirect_back()

    def POST(self):
        action = self.data.get('action', None)

        if action == 'subscribe':
            if self.validate_sub():
                self.add_sub(self.app['app_id'], self.user['id'])
            else:
                self.errors.append("User and application were mismatched; unable to subscribe. Please try again.")
        if action == 'enable':
            if self.validate_sub():
                self.enable_sub(self.app['app_id'], self.user['id'])
            else:
                self.errors.append("User and application were mismatched; unable to subscribe. Please try again.")

        if self.errors:
            return common.render.subscribe(self.user, self.app, self.errors)

        self.redirect_back()
