import web
import constants
import common


class Admin:
    def __init__(self):
        self.errors = []
        self.info = []

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

    def add_user(self, data):
        try:
            password = data['password']
            name = data['name']
            groups = data['groups']
            email = data['email']
        except KeyError:
            self.errors.append("Could not read all fields when adding user")
            return
        try:
            common.users.add(email, password, name=name, groups=groups)
        except:
            self.errors.append("Error adding new user")
        else:
            self.info.append("Successfully added new user")

    def delete_user(self, data):
        try:
            user_id = data['user_id']
        except KeyError:
            self.errors.append("Could not read all fields when deleting user")
            return
        try:
            success = common.users.delete(user_id)
            if success:
                self.info.append("Successfully deleted user")
            else:
                self.errors.append("No user matches that id")
        except:
            self.errors.append("Error deleting user")

    def add_app(self, data):
        try:
            nicename = data['nicename']
            owner_id = data['owner_id']
            scopes = data['scopes'].split(' ')
            uris = data['uris'].split(' ')
            def_scopes = data['def_scopes'].split(' ')
            def_uri = data['def_uri']
        except KeyError:
            self.errors.append("Could not read all fields when adding application")
            return
        try:
            common.applications.add(nicename, owner_id, scopes, uris, def_scopes, def_uri)
        except:
            self.errors.append("Error adding new application")
        else:
            self.info.append("Successfully added new application")

    def delete_app(self, data):
        try:
            app_id = data['app_id']
        except KeyError:
            self.errors.append("Could not read all fields when deleting application")
            return
        try:
            success = common.applications.delete(app_id)
            if success:
                self.info.append("Successfully deleted application")
            else:
                self.errors.append("No application matches that id")
        except:
            self.errors.append("Error deleting application")

    def add_sub(self, data):
        try:
            sub_type = data['type']
            user_id = data['user_id']
            app_id = data['app_id']
        except KeyError:
            self.errors.append("Could not read all fields when adding subscription")
            return
        try:
            common.subscriptions.add(app_id, user_id, sub_type)
        except:
            self.errors.append("Error adding new subscription")
        else:
            self.info.append("Successfully added new subscription")

    def delete_sub(self, data):
        try:
            sub_id = data['sub_id']
        except KeyError:
            self.errors.append("Could not read all fields when deleting subscription")
            return
        try:
            success = common.subscriptions.delete(sub_id)
            if success:
                self.info.append("Successfully deleted subscription")
            else:
                self.errors.append("No subscription matches that id")
        except:
            self.errors.append("Error deleting subscription")

    def is_admin(self, user):
        groups = user['groups'].split(' ')
        return 'admin' in groups

    def get_users(self):
        return common.users.get_all()

    def get_apps(self):
        return common.applications.get_all()

    def get_subs(self):
        return common.subscriptions.get_all()

    def render_page(self, user):
        users = self.get_users()
        apps = self.get_apps()
        subs = self.get_subs()
        return common.render.admin(user, users, apps, subs, self.errors, self.info)

    def GET(self):
        data = web.input()
        common.report_init("ADMIN", "GET", data)

        user_id = self.get_user_id()
        user = self.get_user(user_id)
        is_admin = self.is_admin(user)
        if not is_admin:
            raise web.seeother("/")

        return self.render_page(user)

    def POST(self):
        data = web.input()
        common.report_init("ADMIN", "GET", data)

        user_id = self.get_user_id()
        user = self.get_user(user_id)
        is_admin = self.is_admin(user)
        if not is_admin:
            raise web.seeother("/")

        action = data.get('action', None)
        
        if action == "add_user":
            print("Add user")
            self.add_user(data)
        elif action == "delete_user":
            print("Delete user")
            self.delete_user(data)
        elif action == "add_app":
            print("Add app")
            self.add_app(data)
        elif action == "delete_app":
            print("Delete app")
            self.delete_app(data)
        elif action == "add_sub":
            print("Add sub")
            self.add_sub(data)
        elif action == "delete_sub":
            print("Delete sub")
            self.delete_sub(data)

        return self.render_page(user)
        