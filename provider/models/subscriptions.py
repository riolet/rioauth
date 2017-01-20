class Subscriptions(object):
    def __init__(self, db):
        self.db = db
        self.table = "Subscriptions"

    def get_by_user(self, user_id):
        qvars = {
            'uid': user_id
        }
        query = """SELECT `S`.app_id, user_id, subscription_id, subscription_type, status, nicename, default_redirect_uri
        FROM Subscriptions `S` JOIN Applications `A`
            ON `S`.app_id = `A`.app_id
        WHERE `S`.user_id = $uid OR `A`.owner_id = $uid"""
        rows = self.db.query(query, vars=qvars)
        return list(rows)

    def set_status(self, sub_id, user_id, status):
        if status not in ['active', 'inactive']:
            return -1

        qvars = {
            'sid': sub_id,
            'uid': user_id
        }

        return self.db.update(self.table, "subscription_id=$sid and user_id=$uid", status=status, vars=qvars)

    def set_status_by_app_user(self, app_id, user_id, status):
        if status not in ['active', 'inactive']:
            return -1

        qvars = {
            'aid': app_id,
            'uid': user_id
        }

        return self.db.update(self.table, "app_id=$aid and user_id=$uid", status=status, vars=qvars)

    def get(self, app_id, user_id):
        qvars = {
            'aid': app_id,
            'uid': user_id
        }
        rows = self.db.select(self.table, where="app_id=$aid and user_id=$uid", vars=qvars)
        return rows.first()

    def get_all(self):
        rows = self.db.select(self.table, what="subscription_id, app_id, user_id, subscription_type")
        return list(rows)

    def delete(self, sub_id):
        qvars = {
            'sid': sub_id
        }
        dels = self.db.delete(self.table, where='subscription_id=$sid', vars=qvars)
        return dels == 1

    def add(self, app_id, user_id, subscription_type):
        exists = self.get(app_id, user_id)
        if exists:
            raise KeyError("User already has a subscription to this application.")

        self.db.insert(self.table,
                       app_id=app_id,
                       user_id=user_id,
                       subscription_type=subscription_type)

