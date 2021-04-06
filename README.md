# shotty
AWS EC2 Managing Tool

## About
Test project to manage EC2 Instances

##Setup
Shotty uses the config file created by aws cli command
	`aws configre --profile=shotty`

##Running

	`pipenv run python shotty.py`
	
## List EC2 Instances
	`shotty.py instances list`

### Start EC2 Instances
	`shotty.py instances start`
	
### Stop EC2 Instances
	`shotty.py instances stop`	
	
### Take Snapshot EC2 Instances
	`shotty.py instances take_snapshot`	
	
## List EC2 Volumes
	`shotty.py volumes list`	
	
## List EC2 Snapshots
	`shotty.py snapshots list`		
	
### Delete EC2 Snapshots
	`shotty.py snapshots delete`		