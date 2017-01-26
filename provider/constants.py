import os

DEBUG = False

BASE_PATH = os.path.dirname(__file__)

# Used for database access
DBPATH = ['data']
DBFILENAME = 'dev.db'

# used in setting cookies
REMEMBER_COOKIE_NAME = "rememberme"

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
    '/resetpassword', 'pages.resetpassword.ResetPassword',
    '/changepassword', 'pages.changepassword.ChangePassword',
    '/confirmemail', 'pages.confirmemail.ConfirmEmail',
)
