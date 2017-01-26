import logging
import sys
import os
sys.path.append(os.path.dirname(__file__))
import constants
import web
web.config.debug = constants.DEBUG
from web.wsgiserver import CherryPyWSGIServer
import common

# enable logging, while under development
if constants.DEBUG:
    log = logging.getLogger('oauthlib')
    log.addHandler(logging.StreamHandler(sys.stdout))
    log.setLevel(logging.DEBUG)

# openssl req -x509 -sha256 -nodes -newkey rsa:2048 -days 365 -keyout localhost.key -out localhost.crt
CherryPyWSGIServer.ssl_certificate = "./localhost.crt"
CherryPyWSGIServer.ssl_private_key = "./localhost.key"

app = web.application(constants.urls, globals())


# set the session
if constants.DEBUG:
    if web.config.get('_session') is None:
        common.session = web.session.Session(app, common.session_store)
        web.config._session = common.session
    else:
        common.session = web.config._session
else:  # not debug mode
    common.session = web.session.Session(app, common.session_store)

if __name__ == "__main__":
    app.run()
