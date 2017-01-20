import sys
import os
sys.path.append(os.path.dirname(__file__))
import web
import constants
import common

app = web.application(constants.urls, globals())
common.session = web.session.Session(app, common.session_store)
application = app.wsgifunc()
