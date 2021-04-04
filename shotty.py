import boto3
import click

#Generate Session
session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

#Definimos un grupo de commandos llamado Intances
@click.group()
def instances():
    """Commands for Instances"""

#Ahora la accion LIST es necesaria para mostrar por defecto las instances
@instances.command('list', help="List all instances")
@click.option('--project', default=None, help="Targets all instances belonging to a project")
def list_ec2(project):
    "List EC2 Instances"
    
    instances = []
    
    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
        
    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or [] }
        dns = {i.public_dns_name or "N/A"}
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            dns.pop(),
            tags.get('Project','No Project'))))
    return

@instances.command('stop', help="Stop all instances")
@click.option('--project', default=None, help="Targets all instances belonging to a project")        
def ec2_stop(project):
    instances = []
    
    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
        
    for i in instances:
        if i.state['Name'] == "stopped":
            print("Instances {0} is already stopped".format(i.id))
        else:
            resp=i.stop()
            print("Stopping Instance: {0}...State: {1}".format(i.id,resp['StoppingInstances'][0]['CurrentState']['Name']))
    return

@instances.command('start', help="Start all instances")
@click.option('--project', default=None, help="Targets all instances belonging to a project")        
def ec2_stop(project):
    instances = []
    
    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
        
    for i in instances:
        if i.state['Name'] == "started":
            print("Instances {0} is already started".format(i.id))
        else:
            resp=i.start()
            print("Starting Instance: {0}...State: {1}".format(i.id,resp['StartingInstances'][0]['CurrentState']['Name']))
    return

if __name__ == '__main__':
    
    instances()

    
