import os
import urllib
import urlparse

from ConfigEnvy import ConfigEnvy


config = ConfigEnvy('RIOAUTH_PROVIDER')

DEBUG = config.get('debug', 'debug', default='False').lower() == 'true'

BASE_PATH = os.path.dirname(__file__)

# Used for database access
if not config.has_option('db','db_url') or config.get('db', 'db_url').startswith('sqlite'):
    DB_TYPE = 'sqlite'
    DB_URL = config.get('db', 'db_url', default="sqlite:///tmp/rioauth/provider.db")
    parts = urlparse.urlparse(urllib.unquote(DB_URL))
    DB_PATH = '/'.join(parts.path.split('/')[:-1])
    if not DB_PATH.startswith('/'):
        DB_PATH = os.path.join(BASE_PATH, DB_PATH)
    DB_FILENAME = parts.path[1:].split('/')[-1]
else:
    DB_TYPE = 'not_sqlite'
    DB_URL = config.get('db', 'db_url')

# used in setting cookies
REMEMBER_COOKIE_NAME = "rememberme"

USE_TLS = config.get('ssl', 'use_ssl', default='False').lower() == 'true'

urls = [
    '/', 'pages.account.Account',
    '/login', 'pages.login.Login',
    '/admin', 'pages.admin.Admin',
    '/register', 'pages.register.Register',
    '/subscribe', 'pages.subscribe.Subscribe',
    '/logout', 'pages.logout.Logout',
    '/authorize', 'pages.authorize.Authorize',
    '/token', 'pages.token.Token',
    '/resource', 'pages.resource.Resource',
    '/resetpassword', 'pages.resetpassword.ResetPassword',
    '/changepassword', 'pages.changepassword.ChangePassword',
    '/confirmemail', 'pages.confirmemail.ConfirmEmail'
]
if DEBUG:
    urls.extend(['/_debug_', 'pages.test.Env'])

FROM_ADDRESS = config.get('email', 'from_address', default='noreply@example.com')

