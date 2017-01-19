import common

# create admin account
try:
    admin_id = common.users.add('hat@headquarters.com', 'adminpass', name='Admin', groups="admin")
except KeyError:
    boss = common.users.get('owner@company.com', 'bosspass')
    boss_id = boss.id

# create app owner account
try:
    boss_id = common.users.add('owner@company.com', 'bosspass', name='Pointy Haired Boss')
except KeyError:
    boss = common.users.get('owner@company.com', 'bosspass')
    boss_id = boss.id

# create user account
try:
    user_id = common.users.add('user@customer.com', 'secretpass', name='Bob the Customer')
except KeyError:
    user = common.users.get('user@customer.com', 'secretpass')
    user_id = user.id




app_id = common.applications.add(
    name='WidgetBuilder',
    owner_id=boss_id,
    scopes=['basic', 'admin'],
    redirect_uris=['https://app.local:8080/private', 'https://app.local:8080/login'],
    default_redirect_uri='https://app.local:8080/private')

common.subscriptions.add(app_id=app_id,
         user_id=user_id,
         subscription_type='Basic Package')

