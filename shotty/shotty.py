import boto3
import botocore
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

def has_pending(volume):
    snap = list(volume.snapshots.all())
    
    return snap and snap.state == 'pending'

@click.group()
def cli():
    """Shotty manage snapshots"""

#Definimos un grupo de commandos llamado Snapshots
@cli.group('snapshots')
def snapshots():
    """Commands for Snapshots"""
    
@snapshots.command('list', help="List all snaapshots")    
@click.option('--project', default=None, help="Targets all snapshots belonging to a project")  
@click.option('--all', 'list_all', default=False, is_flag=True, help="List All Snapshots")     
def list_snapshots(project, list_all):
    "List EC2 Volumes"
    
    instances = filter_inst(project)
          
    for i in instances:   
        print(i.id+","+i.state['Name']+"\n\t|")
        for v in i.volumes.all():     
            print("\t|--"+v.id+","+v.state)
            for s in v.snapshots.all():
                print("\t\t|--"+', '.join((
                    s.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c"))))
                    
                if s.state == 'completed' and not list_all: break
    return

@snapshots.command('delete', help="Delete all snapshots")    
@click.option('--project', default=None, help="Targets all snapshots belonging to a project")    
def delete_snapshots(project):
    instances = filter_inst(project)
    for i in instances:   
        print(i.id+","+i.state['Name']+"\n\t|")
        for v in i.volumes.all():     
            print("\t|--"+v.id+","+v.state)
            for s in v.snapshots.all():
                s.delete()
                print("\n\t|-- Deleting: "+s.id)
                
    return            

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
        print(i.id+","+i.state['Name']+"\n\t|")
        for v in i.volumes.all():
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
            try:
                resp=i.stop()
                print("Stopping Instance: {0}...State: {1}".format(i.id,resp['StoppingInstances'][0]['CurrentState']['Name']))
            except botocore.exceptions.ClientError as e:
                print("Instances {0} could not be stopped: {1}".format(i.id,e))
                continue
    return

@instances.command('start', help="Start all instances")
@click.option('--project', default=None, help="Targets all instances belonging to a project")        
def ec2_start(project):
    instances = filter_inst(project)
    for i in instances:
        if i.state['Name'] == "started":
            print("Instances {0} is already started".format(i.id))
        else:
            try:
                resp=i.start()
                print("Starting Instance: {0}...State: {1}".format(i.id,resp['StartingInstances'][0]['CurrentState']['Name']))
            except botocore.exceptions.ClientError as e:
                print("Instances {0} could not be started: {1}".format(i.id,e))
                continue
    return

@instances.command('take_snapshot', help="Take snapshots of selected instances")
@click.option('--project', default=None, help="Targets all instances belonging to a project")        
def ec2_take_snap(project):
    """ Create snapshot of EC2 Instances """
    instances = filter_inst(project)
    
    for i in instances:   
        i.stop()
        print(i.id+","+i.state['Name'])
        i.wait_until_stopped()
        for v in i.volumes.all():
              if has_pending(v):
                print("Skipping Snap {0} ...".format(v.id))
                continue
              print(v.id+": "+"\t| creating snapshot")  
              v.create_snapshot(Description="Created by Shotty!")
              
        i.start()
        print(i.id+","+i.state['Name'])
        i.wait_until_running()
            
    return       

if __name__ == '__main__':
    
    cli()

    
