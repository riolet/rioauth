import time


class BearerTokens(object):
    def __init__(self, db):
        self.db = db
        self.table = "BearerTokens"

    def delete(self, application_id, user):
        qvars = {
            'aid': application_id,
            'uid': user
        }
        num_deleted = self.db.delete(self.table, where="app_id=$aid AND user_id=$uid", vars=qvars)
        return num_deleted

    @staticmethod
    def is_expired(row):
        return int(row.expiration_time) <= (time.time())

    def delete_token(self, tok_type, token):
        qvars = {
            'tok': token
        }

        if tok_type == 'access_token':
            deleted = self.db.delete(self.table, where='access_token=$tok', vars=qvars)
            return deleted
        elif tok_type == 'refresh_token':
            deleted = self.db.delete(self.table, where='refresh_token=$tok', vars=qvars)
            return deleted
        return 0

    def set(self, application_id, user, scopes, access_token, refresh_token):
        self.delete(application_id, user)
        self.db.insert(self.table,
                       app_id=application_id,
                       user_id=user,
                       scopes=scopes,
                       access_token=access_token,
                       refresh_token=refresh_token)
        return

    def get_access(self, access_token):
        qvars = {
            'act': access_token
        }
        rows = self.db.select(self.table, where='access_token=$act', vars=qvars, limit=1)
        row = rows.first()
        if row:
            if self.is_expired(row):
                return None
            else:
                return row
        return rows.first()

    def get_refresh(self, refresh_token):
        qvars = {
            'token': refresh_token
        }
        rows = self.db.select(self.table, where='refresh_token=$token', vars=qvars, limit=1)
        return rows.first()
