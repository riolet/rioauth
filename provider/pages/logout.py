import web
import constants
import common


class Logout(object):
    def GET(self):
        data = web.input()
        common.report_init("LOGOUT", "GET", data)
        web.setcookie(constants.REMEMBER_COOKIE_NAME, "", expires=-1, domain="auth.local", path="/")

        destination = '/'
        if 'login_redirect' in common.session:
            destination = common.session['login_redirect']

        common.session.kill()
        print("redirecting to {0}".format(destination))
        web.seeother(destination)

    def POST(self):
        print(" LOGOUT POST ".center(50, '-'))
        self.GET()

