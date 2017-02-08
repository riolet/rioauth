import web
import common
import base


class Env(base.Page):
    def __init__(self):
        base.Page.__init__(self, "Debug Info")

    def GET(self):
        env = web.ctx.env
        self_vars = self.__dict__
        session = common.session
        config = dict(web.config)

        context = web.ctx

        return common.render.debug(sorted, env, self_vars, session, config, context)