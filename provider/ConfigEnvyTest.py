import os
import urllib
import urlparse

from ConfigEnvy import ConfigEnvy

BASE_PATH = os.path.dirname(__file__)

config = ConfigEnvy('PROVIDER')

DB_FILENAME = config.get('debug', 'debug')
NONEX_DEFAULT = config.get('nonex', 'default', default='default_value_here')
print  DB_FILENAME, NONEX_DEFAULT
db_url = "sqlite:///path/to/file.db"
parts = urlparse.urlparse(urllib.unquote(db_url))
print '/'.join(parts.path.split('/')[:-1])
