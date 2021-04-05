import boto3
import click

#Generate Session
session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

##Get instances
def filter_inst(project):
    instances = []
    
    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
    
    return  instances  


@click.group()
def cli():
    """Shotty manage snapshots"""

#Definimos un grupo de commandos llamado volumes
@cli.group('volumes')
def volumes():
    """Commands for Volumes"""
    
#Ahora la accion LIST es necesaria para mostrar por defecto las instances
@volumes.command('list', help="List all volumes")
@click.option('--project', default=None, help="Targets all volumes belonging to a project")    
def list_volumes(project):
    "List EC2 Volumes"
    
    instances = filter_inst(project)
          
    for i in instances:      
        for v in i.volumes.all():
            print(i.id+","+i.state['Name']+"\n\t|")
            print("\t|--"+', '.join((
                v.id,
                v.state,
                str(v.size) + " GiB",
                v.encrypted and "Encrypted" or "Non-Encrypted",
                v.attachments[0]['Device'])))
    return    
    

#Definimos un grupo de commandos llamado Intances
@cli.group('instances')
def instances():
    """Commands for Instances"""

#Ahora la accion LIST es necesaria para mostrar por defecto las instances
@instances.command('list', help="List all instances")
@click.option('--project', default=None, help="Targets all instances belonging to a project")
def list_ec2(project):
    "List EC2 Instances"
    
    instances = filter_inst(project)
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
    instances = filter_inst(project)
    for i in instances:
        if i.state['Name'] == "stopped":
            print("Instances {0} is already stopped".format(i.id))
        else:
            resp=i.stop()
            print("Stopping Instance: {0}...State: {1}".format(i.id,resp['StoppingInstances'][0]['CurrentState']['Name']))
    return

@instances.command('start', help="Start all instances")
@click.option('--project', default=None, help="Targets all instances belonging to a project")        
def ec2_start(project):
    instances = filter_inst(project)
    for i in instances:
        if i.state['Name'] == "started":
            print("Instances {0} is already started".format(i.id))
        else:
            resp=i.start()
            print("Starting Instance: {0}...State: {1}".format(i.id,resp['StartingInstances'][0]['CurrentState']['Name']))
    return

if __name__ == '__main__':
    
    cli()

    
