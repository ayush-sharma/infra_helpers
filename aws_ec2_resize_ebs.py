import argparse
import boto3
from time import sleep
from subprocess import call


def get_ec2_client():
    """ Get EC2 client. """
    client = boto3.client('ec2',
                          region_name=args.region,
                          aws_access_key_id=args.aws_access_key_id,
                          aws_secret_access_key=args.aws_secret_access_key)
    
    return client


def attach_volume(instance_id: str, volume_id: str, device: str):
    """ Attach volume to instance at mount point. """
    
    data = None
    
    client = get_ec2_client()
    
    print('INFO>> Attaching volume %s to instance %s on %s.' % (volume_id, instance_id, device))
    
    try:
        
        data = client.attach_volume(
                Device=device,
                InstanceId=instance_id,
                VolumeId=volume_id
        )
        
        counter = 0
        while True:
            
            check = client.describe_volume_status(VolumeIds=[volume_id])
            
            if 'VolumeStatuses' in check and len(check['VolumeStatuses']) == 1 and \
                            check['VolumeStatuses'][0]['VolumeStatus']['Status'] == 'ok':
                print('OK>> Volume %s attached successfully to instance %s on %s.' % (volume_id, instance_id, device))
                break
            
            counter += 1
            
            sleep(counter ** 2)
    
    except Exception as e:
        
        print('ERROR>> Coult not attach volume %s to instance %s on %s.' % (volume_id, instance_id, device))
        print('ERROR>> Exception: %s' % str(e))
    
    return data


def create_volume(az: str, size: int, volume_type: str, snapshot_id: None):
    """ Create EBS volume. """
    
    data = None
    
    client = get_ec2_client()
    
    print('INFO>> Creating volume of size %s.' % size)
    
    try:
        
        params = {'AvailabilityZone' : az,
                  'Encrypted'        : False,
                  'Size'             : size,
                  'VolumeType'       : volume_type,
                  'TagSpecifications': [{
                      'ResourceType': 'volume',
                      'Tags'        : [
                          {
                              'Key'  : 'source',
                              'Value': 'aws_ec2_resize_ebs.py'
                          },
                      ]
                  }]}
        
        if snapshot_id:
            
            params['SnapshotId'] = snapshot_id
        
        data = client.create_volume(**params)
        
        volume_id = data['VolumeId']
        
        counter = 0
        while True:
            
            check = client.describe_volumes(VolumeIds=[volume_id])
            
            if 'Volumes' in check and len(check['Volumes']) == 1 and \
                            check['Volumes'][0]['State'] == 'available':
                print('OK>> Volume of size %s created successfully and available.' % size)
                break
            
            counter += 1
            
            sleep(counter ** 2)
    
    except Exception as e:
        
        print('ERROR>> Could not create volume of size %s.' % size)
        print('ERROR>> Exception: %s' % str(e))
    
    return data


def create_snapshot(volume_id: str):
    """ Create snapshot of EBS volume. """
    
    data = None
    
    client = get_ec2_client()
    
    print('INFO>> Creating snapshot of volume %s...' % volume_id)
    
    try:
        
        data = client.create_snapshot(VolumeId=volume_id)
        
        snapshot_id = data['SnapshotId']
        
        counter = 0
        while True:
            
            check = client.describe_snapshots(SnapshotIds=[snapshot_id])
            
            if 'Snapshots' in check and len(check['Snapshots']) == 1 and check['Snapshots'][0]['State'] == 'completed':
                print('OK>> Created snapshot %s of volume %s.' % (snapshot_id, volume_id))
                break
            
            counter += 1
            
            sleep(counter ** 2)
    
    except Exception as e:
        
        print('DEBUG>> Could not create snapshot of volume %s.' % volume_id)
        print('DEBUG>> Exception: %s' % str(e))
    
    return data


def get_instance_status(instance_id: str):
    """ Get EC2 instance status. """
    
    client = get_ec2_client()
    
    print('INFO>> Getting instance status for %s...' % instance_id)
    
    counter = 0
    while True:
        
        check = client.describe_instance_status(InstanceIds=[instance_id], IncludeAllInstances=True)
        
        if 'InstanceStatuses' in check and len(check['InstanceStatuses']) == 1:
            
            print('OK>> Instance status was %s.' % check['InstanceStatuses'][0]['InstanceState']['Name'])
            return check['InstanceStatuses'][0]['InstanceState']['Name']
        
        counter += 1
        
        print('DEBUG>> Sleeping for %s seconds...' % counter ** 2)
        
        sleep(counter ** 2)


def stop_ec2_instance(instance_id: str):
    """ Stop EC2 instance. """
    
    data = None
    
    client = get_ec2_client()
    
    print('INFO>> Stopping instance %s...' % instance_id)
    
    try:
        
        data = client.stop_instances(InstanceIds=[instance_id])
        
        while True:
            state = get_instance_status(instance_id)
            
            if state == 'stopped':
                print('OK>> Instance %s stopped successfully.' % instance_id)
                break
    
    except Exception as e:
        
        print('ERROR>> Could not stop instance %s.' % instance_id)
        print('ERROR>> Exception: %s' % str(e))
    
    return data


def start_ec2_instance(instance_id: str):
    """ Start EC2 instance. """
    
    data = None
    
    client = get_ec2_client()
    
    print('INFO>> Starting instance %s...' % instance_id)
    
    try:
        
        data = client.start_instances(InstanceIds=[instance_id])
        
        while True:
            state = get_instance_status(instance_id)
            
            if state == 'running':
                print('OK>> Instance %s started successfully.' % instance_id)
                break
    
    except Exception as e:
        
        print('ERROR>> Could not start instance %s.' % instance_id)
        print('ERROR>> Exception: %s' % str(e))
    
    return data


def get_ec2_info(instance_id: str):
    """ Get AWS EC2 instance information. """
    
    data = None
    
    client = get_ec2_client()
    
    print('INFO>> Getting instance info for %s.' % instance_id)
    
    try:
        
        data = client.describe_instances(InstanceIds=[instance_id])
    
    except Exception as e:
        
        print('ERROR>> Exception: %s' % str(e))
    
    return data


def get_volume_object(volume_id: str):
    """ Get AWS EBS volume object. """
    
    data = None
    
    client = get_ec2_client()
    
    try:
        
        data = client.describe_volumes(VolumeIds=[volume_id])['Volumes'][0]
    
    except Exception as e:
        
        print('ERROR>> Exception: %s' % str(e))
        pass
    
    return data


def run_ssh_command(user, host, command):
    command = 'ssh %s@%s "%s"' % (user, host, command)
    print('>>INFO Running command: %s.' % command)
    
    output = call([command], shell=True)
    
    return output


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--instance_id', required=True,
                        help='Instance ID of source EC2 instance.')
    parser.add_argument('--region', required=True, help='AWS region that the instance is in.')
    parser.add_argument('--aws_access_key_id', required=True, help='AWS access key ID.')
    parser.add_argument('--aws_secret_access_key', required=True, help='AWS secret access key.')
    parser.add_argument('--target_size', type=int, required=True, help='Target size of volume in GB.')
    
    args = parser.parse_args()
    
    instance_state = get_instance_status(args.instance_id)
    if instance_state == 'stopped':
        start_ec2_instance(args.instance_id)
    
    instance_info = get_ec2_info(instance_id=args.instance_id)
    
    my_instance = {'ami_id'          : instance_info['Reservations'][0]['Instances'][0]['ImageId'],
                   'public_ip'       : instance_info['Reservations'][0]['Instances'][0]['PublicIpAddress'],
                   'block_devices'   : instance_info['Reservations'][0]['Instances'][0]['BlockDeviceMappings'],
                   'root_device_name': instance_info['Reservations'][0]['Instances'][0]['RootDeviceName']}
    
    root_volume_id = None
    for block_device in my_instance['block_devices']:
        
        if block_device['DeviceName'] == my_instance['root_device_name']:
            root_volume_id = block_device['Ebs']['VolumeId']
            break
    
    if not root_volume_id:
        print('- Root volume ID invalid: %s. Exiting.' % str(root_volume_id))
        exit(0)
    
    root_volume = get_volume_object(volume_id=root_volume_id)
    
    if args.target_size < root_volume['Size']:
        
        print('- Shrinking volume from %f to %f.' % (root_volume['Size'], args.target_size))
        
        # Stop Instance
        print('---- Stopping instance...')
        stop_ec2_instance(instance_id=args.instance_id)
        
        # Create snapshot of root volume of the original size
        print('---- Creating snapshot of instance root volume...')
        root_volume_snapshot = create_snapshot(volume_id=root_volume_id)
        root_volume_snapshot_id = root_volume_snapshot['SnapshotId']
        print('- Root volume snapshot ID is %s.' % root_volume_snapshot_id)
        
        # Start Instance
        print('--- Starting instance...')
        start_ec2_instance(args.instance_id)
        
        # Create new clone volume of root volume
        print('---- Creating new volume from snapshot of instance root volume...')
        clone_volume = create_volume(az=root_volume['AvailabilityZone'],
                                     size=root_volume['Size'],
                                     volume_type=root_volume['VolumeType'], snapshot_id=root_volume_snapshot_id)
        
        # Create empty volume of new size
        print('---- Creating empty volume of size %s...' % str(args.target_size))
        new_volume = create_volume(az=root_volume['AvailabilityZone'],
                                   size=args.target_size,
                                   volume_type=root_volume['VolumeType'], snapshot_id=None)
        
        # Attach 2 new volumes to instance
        print('---- Mounting both new volumes in instance...')
        attach_volume(instance_id=args.instance_id, volume_id=clone_volume['VolumeId'], device='/dev/sdy')
        attach_volume(instance_id=args.instance_id, volume_id=new_volume['VolumeId'], device='/dev/sdz')
        
        # Run Command
        print('---- Running copy commands on instance...')
        command = 'sudo mkfs -t ext4 /dev/xvdz; sudo mkdir /mnt/original; sudo mkdir /mnt/new; sudo mount /dev/xvdy1 /mnt/original; sudo mount /dev/xvdz /mnt/new; sudo rsync -aHAXxSP /mnt/original/ /mnt/new; sudo umount /dev/xvdy1; sudo umount /dev/xvdz'
        output = run_ssh_command('ubuntu', '54.80.186.214', command)
        print(output)
    
    elif args.target_size > root_volume['Size']:
        
        print('---- Expanding volume from %f to %f.' % (root_volume['Size'], args.target_size))
        pass
    else:
        
        print('---- Volume size change is not required.')
