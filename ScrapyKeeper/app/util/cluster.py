import boto3
import datetime as dt
from datetime import datetime


def get_instance_memory_usage(app, instance_id):
    cw_conn = boto3.client('cloudwatch', region_name=app.config.get('AWS_DEFAULT_REGION'))

    response = cw_conn.get_metric_data(
        MetricDataQueries=[
            {
                "Id": "myRequestToFindOutUsedMemory",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "CWAgent",
                        "MetricName": "mem_used_percent",
                        "Dimensions": [
                            {
                                "Name": "InstanceId",
                                "Value": instance_id
                            }
                        ]
                    },
                    "Period": 300,
                    "Stat": "Average"
                },
                "Label": "findOutUsedMemory",
                "ReturnData": True
            }
        ],
        StartTime=(datetime.utcnow() - dt.timedelta(minutes=5)),
        EndTime=(datetime.utcnow() - dt.timedelta(minutes=0))
    )

    metric_data_results = response.get('MetricDataResults')
    if 1 > len(metric_data_results):
        return None

    return metric_data_results.pop(0).get('Values').pop(0)
