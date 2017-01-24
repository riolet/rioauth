import web
import constants
import common
import base


class Logout(base.Page):
    def __init__(self):
        base.Page.__init__(self, 'Logout')

    def GET(self):
        # remove any login cookies
        web.setcookie(constants.REMEMBER_COOKIE_NAME, "", expires=-1, domain=constants.DOMAIN, path="/")

        destination = '/'
        if 'logout_redirect' in common.session:
            destination = common.session['logout_redirect']

        common.session.kill()
        web.seeother(destination)
