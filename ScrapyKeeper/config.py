# Statement for enabling the development environment
import logging
import os
import boto3
from botocore.exceptions import ClientError

DEBUG = True


def get_param_from_client(client, parameter_name):
    try:
        value = client.get_parameter(Name=parameter_name, WithDecryption=True)['Parameter']['Value']
    except ClientError:
        logging.error(' ClientError: There is no parameter named: {}'.format(parameter_name))
        return

    if value == 'None':
        return None
    elif value == '\'\'':
        return ''

    return value


# Define the application directory


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ssm_client = boto3.client('ssm', region_name='eu-west-1')

SQLALCHEMY_DATABASE_URI = get_param_from_client(ssm_client, '/data/crawlie-keeper/DATABASE_CONNEaCTION_STRING') or None
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

servers_string = get_param_from_client(ssm_client, '/data/crawlie-keeper/SERVERS') or ''
SERVERS = [s.strip() for s in servers_string.split(',') if s]

# basic auth
NO_AUTH = False
BASIC_AUTH_USERNAME = 'admin'
BASIC_AUTH_PASSWORD = 'admin'
BASIC_AUTH_FORCE = True

NO_SENTRY = False
SENTRY_URI = get_param_from_client(ssm_client, '/data/crawlie-keeper/SENTRY_URI') or None

# http settings

DEFAULT_TIMEOUT = 30  # seconds

SPIDERS_SYNC_INTERVAL_IN_SECONDS = int(get_param_from_client(ssm_client, '/data/crawlie-keeper/SPIDERS_SYNC_INTERVAL_IN_SECONDS') or 120)

BACK_IN_TIME_ENABLED = bool(int(get_param_from_client(ssm_client, '/data/crawlie-keeper/BACK_IN_TIME_ENABLED') or 1))

AUTO_SCHEDULE_ENABLED = bool(int(get_param_from_client(ssm_client, '/data/crawlie-keeper/AUTO_SCHEDULE_ENABLED') or 1))
AUTO_SCHEDULE_DEFAULT_VALUE = bool(int(get_param_from_client(ssm_client, '/data/crawlie-keeper/AUTO_SCHEDULE_DEFAULT_VALUE') or 1))

MIN_LOAD_RATIO_MULTIPLIER = float(get_param_from_client(ssm_client, '/data/crawlie-keeper/MIN_LOAD_RATIO_MULTIPLIER') or 0.5)
MAX_LOAD_RATIO_MULTIPLIER = float(get_param_from_client(ssm_client, '/data/crawlie-keeper/MAX_LOAD_RATIO_MULTIPLIER') or 6)
MAX_SPIDERS_START_AT_ONCE = int(get_param_from_client(ssm_client, '/data/crawlie-keeper/MAX_SPIDERS_START_AT_ONCE') or 10)
MAX_LOAD_ALLOWED = int(get_param_from_client(ssm_client, '/data/crawlie-keeper/MAX_LOAD_ALLOWED') or 250)
DEFAULT_AUTOTHROTTLE_MAX_CONCURRENCY = int(get_param_from_client(ssm_client, '/data/crawlie-keeper/AUTOTHROTTLE_MAX_CONCURRENCY') or 10)

USED_MEMORY_PERCENT_THRESHOLD = int(get_param_from_client(ssm_client, '/data/crawlie-keeper/USED_MEMORY_PERCENT_THRESHOLD') or 90)  # the threshold for launching new spiders
RUNS_IN_CLOUD = bool(int(get_param_from_client(ssm_client, '/data/crawlie-keeper/RUNS_IN_CLOUD') or 1))
