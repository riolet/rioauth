import os
import sys

BASE_PATH = os.path.dirname(__file__)
DBPATH = ['data']
DBFILENAME = 'dev.db'

sys.path.append(BASE_PATH)

urls = (
    '/', 'pages.account.Account',
    '/login', 'pages.login.Login',
    '/register', 'pages.register.Register',
    '/logout', 'page.logout.Logout',
    '/authorize', 'pages.authorize.Authorize',
    '/token', 'pages.token.Token',
)

REMEMBER_COOKIE_NAME = "rememberme"