import os
import constants
import web
import bcrypt


def parse_sql_file(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    # remove comment lines
    lines = [i for i in lines if not i.startswith("--")]
    # join into one long string
    script = " ".join(lines)
    # split string into a list of commands
    commands = script.split(";")
    # ignore empty statements (like trailing newlines)
    commands = filter(lambda x: bool(x.strip()), commands)
    return commands


def exec_sql(connection, path):
    commands = parse_sql_file(path)
    for command in commands:
        connection.query(command)


def create_db(db_path, filename):

    # make sure folder exists
    if not os.path.exists(db_path):
        os.makedirs(db_path)

    # make sure db exists
    full_path = os.path.join(db_path, filename)
    if not os.path.exists(full_path):
        f = open(full_path, 'a')
        f.close()


def create_tables(db, base_path):
    exec_sql(db, os.path.join(base_path, "sql", "create_tables.sql"))


def create_session_tables(db, base_path):
    exec_sql(db, os.path.join(base_path, "sql", "session_table.sql"))


def create_admin_account(db):
    # intended credentials:
    email = constants.config.get('profiles', 'adminmail')
    password = constants.config.get('profiles', 'adminpass')
    password = password.encode(encoding='utf-8')
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    # get any admin accounts that exist.
    rows = list(db.select('Users', where="groups='admin'"))
    if len(rows) == 0:
        # create admin account
        db.insert('Users', email=email, password=hashed_password, name='Admin', groups='admin', email_confirmed='1')
    elif len(rows) == 1:
        # check if email/password match. if not, update to use new email
        row = rows[0]
        if row['email'] != email or row['password'] != hashed_password:
            qvars = {
                'uid': row['id']
            }
            # TODO: will break if a user already exists with this email address.
            db.update('Users', where='id=$uid', vars=qvars, email=email, password=hashed_password, email_confirmed='1')
        else:
            # we're good, admin account exists as described
            pass
    elif len(rows) > 1:
        # Remove extra admin users. There can be only one.
        to_save = None
        to_toss = []
        for row in rows:
            if to_save and to_save['email'] == email:
                to_toss.append(row)
            else:
                to_toss.append(to_save)
                to_save = row
        qvars = {
            'uid': to_save['id']
        }
        # TODO: will break if a user already exists with this email address.
        db.update('Users', where='id=$uid', vars=qvars, email=email, password=hashed_password, email_confirmed='1')
        for row in to_toss:
            qvars['uid'] = row['id']
            db.delete('Users', where='id=$uid', vars=qvars)


def db_setup(db, base_path):
    if constants.DB_TYPE == 'sqlite':
        create_db(constants.DB_PATH, constants.DB_FILENAME)
        db.query("PRAGMA foreign_keys = ON;")
    create_tables(db, base_path)
    create_session_tables(db, base_path)
    create_admin_account(db)


def get_db():
        if constants.DB_TYPE == 'sqlite':
            db = web.database(dbn='sqlite',db=os.path.join(constants.DB_PATH, constants.DB_FILENAME))
        else:
            db = web.database(dburl=constants.DB_URL)
        db_setup(db, constants.BASE_PATH)
        return db
