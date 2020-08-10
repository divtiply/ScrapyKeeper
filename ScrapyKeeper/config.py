# Statement for enabling the development environment
import os

from ScrapyKeeper.app.util.parameter_store import ParameterStore

DEBUG = True

# Define the application directory


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
param_store = ParameterStore()

SQLALCHEMY_DATABASE_URI = param_store.get_param('/data/crawlie-keeper/DATABASE_CONNECTION_STRING')
SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"

# log
LOG_LEVEL = 'INFO'

AWS_DEFAULT_REGION = 'eu-west-1'
DEFAULT_CLUSTER_NAME = 'crawler'

# spider services
SERVER_TYPE = 'scrapyd'

servers_string = param_store.get_param('/data/crawlie-keeper/SERVERS', '')
SERVERS = [s.strip() for s in servers_string.split(',') if s]

# basic auth
NO_AUTH = False
BASIC_AUTH_USERNAME = 'admin'
BASIC_AUTH_PASSWORD = 'admin'
BASIC_AUTH_FORCE = True

NO_SENTRY = False
SENTRY_URI = param_store.get_param('/data/crawlie-keeper/SENTRY_URI')

# http settings

DEFAULT_TIMEOUT = 30  # seconds

SPIDERS_SYNC_INTERVAL_IN_SECONDS = int(param_store.get_param('/data/crawlie-keeper/SPIDERS_SYNC_INTERVAL_IN_SECONDS', 120))

BACK_IN_TIME_ENABLED = bool(int(param_store.get_param('/data/crawlie-keeper/BACK_IN_TIME_ENABLED', 1)))

AUTO_SCHEDULE_ENABLED = bool(int(param_store.get_param('/data/crawlie-keeper/AUTO_SCHEDULE_ENABLED', 1)))
AUTO_SCHEDULE_DEFAULT_VALUE = bool(int(param_store.get_param('/data/crawlie-keeper/AUTO_SCHEDULE_DEFAULT_VALUE', 1)))

MIN_LOAD_RATIO_MULTIPLIER = float(param_store.get_param('/data/crawlie-keeper/MIN_LOAD_RATIO_MULTIPLIER', 0.5))
MAX_LOAD_RATIO_MULTIPLIER = float(param_store.get_param('/data/crawlie-keeper/MAX_LOAD_RATIO_MULTIPLIER', 6))
MAX_SPIDERS_START_AT_ONCE = int(param_store.get_param('/data/crawlie-keeper/MAX_SPIDERS_START_AT_ONCE', 10))
MAX_LOAD_ALLOWED = int(param_store.get_param('/data/crawlie-keeper/MAX_LOAD_ALLOWED', 250))
DEFAULT_AUTOTHROTTLE_MAX_CONCURRENCY = int(param_store.get_param('/data/crawlie-keeper/AUTOTHROTTLE_MAX_CONCURRENCY', 10))

USED_MEMORY_PERCENT_THRESHOLD = int(param_store.get_param('/data/crawlie-keeper/USED_MEMORY_PERCENT_THRESHOLD', 90))  # the threshold for launching new spiders
RUNS_IN_CLOUD = bool(int(param_store.get_param('/data/crawlie-keeper/RUNS_IN_CLOUD', 1)))
