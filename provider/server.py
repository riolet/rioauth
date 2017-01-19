import traceback
import logging
import sys
import web
web.config.debug = False
from web.wsgiserver import CherryPyWSGIServer
import constants
import common

# enable logging, while under development
log = logging.getLogger('oauthlib')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

# openssl req -x509 -sha256 -nodes -newkey rsa:2048 -days 365 -keyout localhost.key -out localhost.crt
CherryPyWSGIServer.ssl_certificate = "./localhost.crt"
CherryPyWSGIServer.ssl_private_key = "./localhost.key"

app = web.application(constants.urls, globals())
common.session = web.session.Session(app, common.session_store)

if __name__ == "__main__":
    app.run()
