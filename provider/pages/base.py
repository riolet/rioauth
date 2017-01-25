from urllib import quote
import web
import common


class Page(object):
    def __init__(self, title):
        self.data = web.input()
        self.page_title = title
        self.user_id = None
        self.app_id = None
        self.subscription_id = None
        self.http_method, self.body, self.headers = self.extract_params()
        self.uri = self.reconstruct_uri()
        self.errors = []
        self.info = []
        self.request = None

        common.report_init(self.uri, self.page_title, web.ctx.env['REQUEST_METHOD'], self.data)

    @staticmethod
    def reconstruct_uri():
        url = web.ctx.environ['wsgi.url_scheme'] + '://'

        if web.ctx.environ.get('HTTP_HOST'):
            url += web.ctx.environ['HTTP_HOST']
        else:
            url += web.ctx.environ['SERVER_NAME']

            if web.ctx.environ['wsgi.url_scheme'] == 'https':
                if web.ctx.environ['SERVER_PORT'] != '443':
                    url += ':' + web.ctx.environ['SERVER_PORT']
            else:
                if web.ctx.environ['SERVER_PORT'] != '80':
                    url += ':' + web.ctx.environ['SERVER_PORT']

        url += quote(web.ctx.environ.get('SCRIPT_NAME', ''))
        url += quote(web.ctx.environ.get('PATH_INFO', ''))
        if web.ctx.environ.get('QUERY_STRING'):
            url += '?' + web.ctx.environ['QUERY_STRING']

        return url

    @staticmethod
    def extract_params():
        http_method = web.ctx.environ["REQUEST_METHOD"]
        body = web.ctx.get('data', '')
        headers = web.ctx.env.copy()
        headers.pop("wsgi.errors", None)
        headers.pop("wsgi.input", None)
        # headers are not in the usual format. e.g. Content-Type is "CONTENT_TYPE"
        # and Authorization is "HTTP_AUTHORIZATION"
        # See this for renaming details:
        # https://www.python.org/dev/peps/pep-0333/#environ-variables

        return http_method, body, headers

    def is_logged_in(self):
        if 'logged_in' in common.session and 'user_id' in common.session and common.session['logged_in'] is True:
            self.user_id = common.session['user_id']
            return True
        else:
            return False

    def require_login(self, return_uri):
        if not self.is_logged_in():
            common.session['login_redirect'] = return_uri
            raise web.seeother("/login")
        else:
            common.session.pop('login_redirect', None)
        return self.user_id

    def is_subscribed(self, user_id, app_id):
        subscription = common.subscriptions.get(app_id, user_id)
        if subscription:
            self.subscription_id = subscription['subscription_id']
            return subscription['status'] == 'active'
        else:
            return False

    def require_subscribed(self, user_id, app_id, return_uri):
        if not self.is_subscribed(user_id, app_id):
            common.session['subscribe_redirect'] = return_uri
            raise web.seeother('/subscribe?app_id={0}'.format(app_id))
        else:
            common.session.pop('subscribe_redirect', None)
        return self.subscription_id

    def require_oauthentication(self, oauth_server, scopes_required=None):
        scopes_list = scopes_required or []
        valid, self.request = oauth_server.verify_request(
            self.uri, self.http_method, self.body, self.headers, scopes_list)
        if not valid:
            raise web.forbidden()
        else:
            return True

    @staticmethod
    def is_in_group(user, group):
        groups = user['groups'].split(' ')
        return group in groups

    def require_group(self, user, group, fail_uri):
        if not self.is_in_group(user, group):
            raise web.seeother(fail_uri)

    @staticmethod
    def get_user_data(user_id):
        user = dict(common.users.get_by_id(user_id))

        # accessible apps
        subs = common.subscriptions.get_by_user(user_id)
        user['subscriptions'] = map(dict, subs)

        # owned apps
        apps = common.applications.get_all_by_owner(user_id)
        user['apps'] = apps

        return user

    @staticmethod
    def get_user(user_id, what='*'):
        user = dict(common.users.get_by_id(user_id, what))
        return user

    def GET(self):
        raise web.nomethod()

    def POST(self):
        raise web.nomethod()

class LoggedInPage(Page):
    def __init__(self, title):
        Page.__init__(self, title)
        self.require_login(self.uri)

class AdminPage(LoggedInPage):
    def __init__(self, title):
        LoggedInPage.__init__(self, title)
        self.user = self.get_user(self.user_id)
        self.require_group(self.user, 'admin', '/')
