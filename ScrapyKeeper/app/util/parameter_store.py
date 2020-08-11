import boto3
from botocore.exceptions import ClientError


class ParameterStore:
    def __init__(self, default_region='eu-west-1'):
        self._client = boto3.client('ssm', region_name=default_region)

    def get_param(self, parameter_name, *default_value):
        try:
            value = self._client.get_parameter(Name=parameter_name, WithDecryption=True)['Parameter']['Value']

            if value == 'None':
                return None
            elif value == '\'\'':
                return ''

            return value

        except ClientError:
            if not default_value:
                raise ValueError('Missing parameter: "{}" and default value'.format(parameter_name))

            return default_value[0]
