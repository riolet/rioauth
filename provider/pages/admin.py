import common
import base


class Admin(base.AdminPage):
    def __init__(self):
        base.AdminPage.__init__(self, "Admin panel")

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

    @staticmethod
    def get_users():
        return common.users.get_all()

    @staticmethod
    def get_apps():
        return common.applications.get_all()

    @staticmethod
    def get_subs():
        return common.subscriptions.get_all()

    def render_page(self, user):
        users = self.get_users()
        apps = self.get_apps()
        subs = self.get_subs()
        return common.render.admin(user, users, apps, subs, self.errors, self.info)

    def GET(self):
        return self.render_page(self.user)

    def POST(self):
        action = self.data.get('action', None)
        
        if action == "add_user":
            print("Add user")
            self.add_user(self.data)
        elif action == "delete_user":
            print("Delete user")
            self.delete_user(self.data)
        elif action == "add_app":
            print("Add app")
            self.add_app(self.data)
        elif action == "delete_app":
            print("Delete app")
            self.delete_app(self.data)
        elif action == "add_sub":
            print("Add sub")
            self.add_sub(self.data)
        elif action == "delete_sub":
            print("Delete sub")
            self.delete_sub(self.data)

        return self.render_page(self.user)
