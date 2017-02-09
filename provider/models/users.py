import time
import bcrypt
import hashlib
import binascii
import hmac
from datetime import datetime
import common
import re


class Users:
    def __init__(self, db):
        self.db = db
        self.table = "Users"

    def update_access_time(self, email):
        """
        Updates the "last_access" time to the current server time, for the user with the given email address
        :param email:  The email to identify a user
        :return: None
        """
        qvars = {
            "email": email
        }
        now = int(time.time())
        self.db.update(self.table, "email=$email", vars=qvars, last_access=now)

    def update(self, user_id, **kwargs):
        qvars = {
            'uid': user_id
        }
        affected = self.db.update(self.table, 'id=$uid', vars=qvars, **kwargs)
        return affected == 1

    def get_login_cookie(self, user_id):
        token = common.generate_salt(32)
        secret_key = common.generate_salt(32)
        self.store_remember_token(user_id, token, secret_key)
        cookie_text = "{0}:{1}".format(user_id, token)
        dk = hashlib.pbkdf2_hmac('sha256', cookie_text, secret_key, 100000)
        ascii_hash = binascii.hexlify(dk)
        cookie_text = "{0}:{1}".format(cookie_text, ascii_hash)
        return cookie_text

    def delete(self, user_id):
        qvars = {
            'uid': user_id
        }
        deleted_rows = self.db.delete(self.table, where='id=$uid', vars=qvars)
        return deleted_rows == 1

    def validate_login_cookie(self, user_id, token, cookie_hash):
        """
        Validate a "remember me" cookie meant to keep a user logged in.
        :param user_id: The user to match against
        :param token: One of two secret codes (stored with the user db row)
        :param cookie_hash: Everything hashed together
        :return: True or False if the cookie matches a login credential
        """
        valid = False
        user = self.get_by_id(user_id)
        if user:
            print("memory of user found")
            saved_token = user.remember_token
            saved_key = user.secret_key
            dk = hashlib.pbkdf2_hmac('sha256', "{0}:{1}".format(user_id, saved_token), saved_key, 100000)
            ascii_hash = binascii.hexlify(dk)
            matches = hmac.compare_digest("{0}:{1}:{2}".format(user_id, token, cookie_hash),
                                          "{0}:{1}:{2}".format(user_id, saved_token, ascii_hash))
            if matches:
                print("user codes match! User is remembered")
                valid = True
        return valid

    @staticmethod
    def validate_pass(password):
        return len(password) >= 6

    @staticmethod
    def validate_email(email):
        return bool(re.match(r'^[\w.]+@[\w]+\.[\w.]+$', email))

    @staticmethod
    def validate_name(name):
        return len(name) > 0

    def get_by_email(self, email):
        qvars = {
            'em': email
        }
        rows = self.db.select(self.table, where='email=$em', vars=qvars, limit=1)
        user = rows.first()
        return user

    def get_by_id(self, account, what='*'):
        qvars = {
            "aid": account
        }
        if type(what) is list or type(what) is tuple:
            what = ', '.join(what)
        rows = self.db.select(self.table, where='id=$aid', what=what, vars=qvars, limit=1)
        user = rows.first()
        return user

    def get_all(self):
        date_format = '%Y-%m-%d %H:%M:%S'
        rows = list(self.db.select(self.table, what="id, email, groups, name, last_access"))
        for row in rows:
            row['last_access'] = datetime.fromtimestamp(row['last_access']).strftime(date_format)
        return rows

    def get(self, email, password):
        """
        :param email: The user email to search for
        :param password: The use password that corresponds to the email above
        :return: All user details if a match is found, else None.
        """
        qvars = {
            "email": email
        }
        rows = self.db.select(self.table, where="email=$email", vars=qvars, limit=1)
        user = rows.first()
        if user:
            hashed_password = user.password.encode(encoding='utf-8')
            ascii_password = password.encode(encoding='utf-8')
            password_matches = bcrypt.hashpw(ascii_password, hashed_password) == hashed_password
            if password_matches:
                self.update_access_time(email)
                return user
            else:
                return None
        else:
            return None

    def add(self, email, password, name, **kwargs):
        # Password needs be string not unicode
        password = password.encode(encoding='utf-8')

        # Validate details
        if not self.validate_email(email):
            raise common.ValidationError("Email isn't valid")
        if not self.validate_name(name):
            raise common.ValidationError("Name must not be empty")
        if not self.validate_pass(password):
            raise common.ValidationError("Password must be at least 6 characters")

        qvars = {
            "email": email
        }
        rows = self.db.select(self.table, where="email=$email", vars=qvars, limit=1)
        user = rows.first()
        if user:
            print("checking user: ")
            print("confirmed = {0} ({0.__class__})".format(user.email_confirmed))
            if user.email_confirmed == '1':
                raise KeyError("Email already exists")
            else:
                self.delete(user.id)

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        user_id = self.db.insert(self.table, email=email, password=hashed_password, name=name, **kwargs)

        return user_id

    def set_password(self, user_id, new_password):
        qvars = {
            'uid': user_id
        }

        if not self.validate_pass(new_password):
            raise common.ValidationError("Password must be at least 6 characters")

        hashed_password = bcrypt.hashpw(new_password.encode(encoding='utf-8'), bcrypt.gensalt())

        changes = self.db.update(self.table, 'id=$uid', vars=qvars, password=hashed_password)
        return changes == 1

    def store_remember_token(self, account_id, token, secret):
        qvars = {
            'aid': account_id
        }
        self.db.update(self.table, "id=$aid", vars=qvars, remember_token=token, secret_key=secret)
