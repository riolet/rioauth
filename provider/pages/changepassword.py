import web
import common


class ResetPassword(object):
    def __init__(self):
        self.data = web.input()
        self.errors = []
        self.user = None

    def GET(self):
        common.report_init('CHANGEPASSWORD', 'GET', self.data)

        # require user to be defined.

        return common.render.changepass()

    def POST(self):
        common.report_init('CHANGEPASSWORD', 'POST', self.data)

        return common.render.changepass()
