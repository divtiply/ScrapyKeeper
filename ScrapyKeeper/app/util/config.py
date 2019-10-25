import boto3


def get_cluster_servers(app):
    """
    Dynamically get the instance ips from a given cluster
    :return: list
    """
    ecs_conn = boto3.client('ecs', region_name=app.config.get('AWS_DEFAULT_REGION'))
    
    cluster_name = app.config.get('DEFAULT_CLUSTER_NAME')
    
    container_arns = ecs_conn.list_container_instances(cluster=cluster_name).get('containerInstanceArns', [])
    if not container_arns:
        return []
    
    detailed_containers = ecs_conn.describe_container_instances(cluster=cluster_name, containerInstances=container_arns)
    instance_ids = [c.get('ec2InstanceId') for c in detailed_containers.get('containerInstances', [])]
    if not instance_ids:
        return []
    
    ec2_conn = boto3.client('ec2', region_name=app.config.get('AWS_DEFAULT_REGION'))
    detailed_instances = ec2_conn.describe_instances(InstanceIds=instance_ids)
    
    ips = []
    for reservation in detailed_instances.get('Reservations', []):
        for instance in reservation.get('Instances', []):
            ips.append(instance.get('PrivateIpAddress'))
    
    if not ips:
        return []
    
    servers = ['http://{}:6800'.format(ip) for ip in ips]
    
    return servers
