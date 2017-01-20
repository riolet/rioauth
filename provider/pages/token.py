import web
import common
from oauthlib.oauth2 import WebApplicationServer
from request_validator import MyRequestValidator


class Token(object):
    def __init__(self):
        self._token_endpoint = WebApplicationServer(MyRequestValidator())

    def GET(self):
        data = web.input()
        common.report_init("TOKEN", "GET", data)
        print("Error. POST method expected.")
        return common.render.dummy()

    def POST(self):
        data = web.input()
        common.report_init("TOKEN", "POST", data)

        uri = "{scheme}://{host}{port}{path}".format(
            scheme=web.ctx.env.get('wsgi.url_scheme', 'http'),
            host=web.ctx.env['SERVER_NAME'],
            port=':{0}'.format(web.ctx.env['SERVER_PORT']),
            path=web.ctx.env['REQUEST_URI']
        )
        http_method = web.ctx.environ["REQUEST_METHOD"]
        body = web.ctx.get('data', '')
        headers = web.ctx.env.copy()
        headers.pop("wsgi.errors", None)
        headers.pop("wsgi.input", None)
        headers = {
            'CONTENT_TYPE': 'application/x-www-form-urlencoded;charset=UTF-8'
        }

        # If you wish to include request specific extra credentials for
        # use in the validator, do so here.
        credentials = {
            #'foo': 'bar'
        }

        headers, body, status = self._token_endpoint.create_token_response(
            uri, http_method, body, headers, credentials)

        # All requests to /token will return a json response, no redirection.
        return common.response_from_return(headers, body, status)

