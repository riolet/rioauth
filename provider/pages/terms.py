import common
import base


class Terms(base.Page):
    def __init__(self):
        base.Page.__init__(self, "Riolet Terms of Service and Privacy Policy")

    def GET(self):
        return common.render.terms()