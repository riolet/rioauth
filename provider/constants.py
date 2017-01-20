import os
import sys

BASE_PATH = os.path.dirname(__file__)
DBPATH = ['data']
DBFILENAME = 'dev.db'

sys.path.append(BASE_PATH)

urls = (
    '/', 'pages.account.Account',
    '/login', 'pages.login.Login',
    '/admin', 'pages.admin.Admin',
    '/register', 'pages.register.Register',
    '/subscribe', 'pages.subscribe.Subscribe',
    '/logout', 'pages.logout.Logout',
    '/authorize', 'pages.authorize.Authorize',
    '/token', 'pages.token.Token',
    '/resource', 'pages.resource.Resource',
)

REMEMBER_COOKIE_NAME = "rememberme"