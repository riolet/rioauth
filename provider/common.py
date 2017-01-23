import os
import dbsetup
import constants
import web
import base64
import math
from models.users import Users
from models.subscriptions import Subscriptions
from models.applications import Applications
from models.authorization_codes import AuthorizationCodes
from models.bearer_tokens import BearerTokens
from models.email_loopback import EmailLoopback


def b64_url_encode(bytes):
    return base64.b64encode(bytes, "-_")


def generate_salt(length):
    """
    Generate a cryptographically secure random base64 code of the desired length
    :param length: The desired output string length
    :return: A base64 encoded salt
    """
    # base64 stores 6 bits per symbol but os.urandom gives 8 bits per symbol
    bytes_needed = int(math.ceil(length * 6.0 / 8.0))
    bytes = os.urandom(bytes_needed)
    encoded = b64_url_encode(bytes)
    return encoded[:length]


def report_init(page, protocol, webinput):
    print(" {page} {protocol} ".format(page=page, protocol=protocol).center(50, '-'))
    print("SESSION ID: {0}".format(web.ctx.environ.get('HTTP_COOKIE', 'unknown')))
    print("SESSION KEYS: {0}".format(session.keys()))
    print("SESSION: {0}".format(dict(session)))
    print("WEB INPUT: {0}".format(webinput))
    print("-"*50)
    print("")


def response_from_return(headers, body, status):
    print("response_from_return(...)")
    print("  headers: {0}".format(str(headers)[:50]))
    print("  body: {0}".format(str(body)[:50]))
    print("  status: {0}".format(status))
    # raise web.HTTPError(status, headers, body)
    raise web.HTTPError('200 OK', headers, body)


def response_from_error(e):
    raise web.BadRequest('<h1>Bad Request</h1><p>Error is: {0}</p>'.format(e.description))


_db = dbsetup.get_db()
users = Users(_db)
subscriptions = Subscriptions(_db)
applications = Applications(_db)
authorization_codes = AuthorizationCodes(_db)
bearer_tokens = BearerTokens(_db)
email_loopback = EmailLoopback(_db)

render = web.template.render(os.path.join(constants.BASE_PATH, 'templates'))

session_store = web.session.DBStore(_db, 'sessions')

session = None