import web
import constants
import common
import base


class Logout(base.Page):
    def __init__(self):
        base.Page.__init__(self, 'Logout')

    def GET(self):
        # remove any login cookies
        domain = web.ctx.environ.get('HTTP_HOST')
        if domain:
            colon = domain.find(":")
            if colon != -1:
                domain = domain[:colon]
        else:
            domain = web.ctx.environ['SERVER_NAME']
        web.setcookie(constants.REMEMBER_COOKIE_NAME, "", expires=-1, domain=domain, path="/")

        destination = '/'
        if 'logout_redirect' in common.session:
            destination = common.session['logout_redirect']

        common.session.kill()
        web.seeother(destination)
