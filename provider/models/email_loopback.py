import time
import common


class EmailLoopback(object):

    def __init__(self, db):
        self.db = db
        self.table = "EmailLoopback"

    def delete(self, user_id):
        qvars = {
            'uid': user_id
        }
        num_deleted = self.db.delete(self.table, where='user_id=$uid', vars=qvars)
        return num_deleted

    def add(self, user_id, redirect_uri, duration=600):
        key = common.generate_salt(64)
        expiration = int(time.time())+duration

        self.delete(user_id)
        self.db.insert(
            self.table,
            user_id=user_id,
            secret_key=key,
            redirect_uri=redirect_uri,
            expiration_time=expiration)

        return key

    @staticmethod
    def is_expired(row):
        """
        :return: True if row exists and is expired. Otherwise False.
        """
        return row and row.expiration_time <= int(time.time())

    def get(self, key):
        print("getting key {0}".format(key))
        qvars = {'key': key}
        rows = self.db.select(self.table, where='secret_key=$key', vars=qvars)
        row = rows.first()
        return row
