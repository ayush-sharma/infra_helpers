import argparse
import boto3
from time import sleep


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
    
    print('> Attaching volume %s to instance %s on %s.' % (volume_id, instance_id, device))
    
    try:
        
        data = client.attach_volume(
                Device=device,
                InstanceId=instance_id,
                VolumeId=volume_id
        )
        
        counter = 0
        while True:
            
            check = client.describe_volume_status(VolumeIds=[volume_id])['VolumeStatuses']['VolumeStatus']['Status']
            
            if check == 'ok':
                print('>> Volume %s attached successfully to instance %s on %s.' % (volume_id, instance_id, device))
                break
            
            counter += 1
            
            sleep(counter ** 2)
    
    except Exception as e:
        
        print('>> Coult not attach volume %s to instance %s on %s.' % (volume_id, instance_id, device))
        print('>> Exception: %s' % str(e))
    
    return data


def create_volume(az: str, iops: int, size: int, volume_type: str, SnapshotId: None):
    """ Create EBS volume. """
    
    data = None
    
    client = get_ec2_client()
    
    print('> Creating volume of size %s.' % size)
    
    try:
        
        params = {'AvailabilityZone': az,
                  'Encrypted'       : False,
                  'Iops'            : iops,
                  'Size'            : size,
                  'VolumeType'      : volume_type}
        
        if SnapshotId:
            
            params['SnapshotId'] = SnapshotId
        
        data = client.create_volume(**params)
        
        counter = 0
        while True:
            
            check = data.describe_status()['VolumeStatuses'][0]['VolumeStatus']['Status']
            
            if check == 'ok':
                print('>> Volume of size %s created successfully.' % size)
                break
            
            counter += 1
            
            sleep(counter ** 2)
    
    except Exception as e:
        
        print('>> Could not create volume of size %s.' % size)
        print('>> Exception: %s' % str(e))
    
    return data


def create_snapshot(volume_id: str):
    """ Create snapshot of EBS volume. """
    
    data = None
    
    client = get_ec2_client()
    
    print('> Creating snapshot of volume %s...' % volume_id)
    
    try:
        
        data = client.create_snapshot(VolumeId=[volume_id])
        
        counter = 0
        while True:
            
            check = client.describe_snapshots(SnapshotIds=[volume_id])['VolumeStatuses']['VolumeStatus']['Status']
            
            if check == 'ok':
                print('>> Created snapshot of volume %s.' % volume_id)
                break
            
            counter += 1
            
            sleep(counter ** 2)
    
    except Exception as e:
        
        print('>> Could not create snapshot of volume %s.' % volume_id)
        print('>> Exception: %s' % str(e))
    
    return data


def stop_ec2_instance(instance_id: str):
    """ Stop EC2 instance. """
    
    data = None
    
    client = get_ec2_client()
    
    print('> Stopping instance %s...' % instance_id)
    
    try:
        
        data = client.stop_instances(InstanceIds=[instance_id])
        
        counter = 0
        while True:
            
            check = client.describe_instance_status(InstanceIds=[instance_id])['InstanceStatuses']['InstanceState']
            
            if check == 'stopped':
                print('>> Instance %s stopped successfully.' % instance_id)
                break
            
            counter += 1
            
            sleep(counter ** 2)
    
    except Exception as e:
        
        print('>> Could not stop instance %s.' % instance_id)
        print('>> Exception: %s' % str(e))
    
    return data


def start_ec2_instance(instance_id: str):
    """ Start EC2 instance. """
    
    data = None
    
    client = get_ec2_client()
    
    print('> Starting instance %s...' % instance_id)
    
    try:
        
        data = client.start_instances(InstanceIds=[instance_id])
        
        counter = 0
        while True:
            
            check = client.describe_instance_status(InstanceIds=[instance_id])['InstanceStatuses']['InstanceState']
            
            if check == 'running':
                print('>> Instance %s started successfully.' % instance_id)
                break
            
            counter += 1
            
            sleep(counter ** 2)
    
    except Exception as e:
        
        print('>> Could not start instance %s.' % instance_id)
        print('>> Exception: %s' % str(e))
    
    return data


def get_ec2_info(instance_id: str):
    """ Get AWS EC2 instance information. """
    
    data = None
    
    client = get_ec2_client()
    
    print('> Getting instance info for %s.' % instance_id)
    
    try:
        
        data = client.describe_instances(InstanceIds=[instance_id])
    
    except Exception as e:
        
        print('>> Exception: %s' % str(e))
    
    return data


def get_volume_object(volume_id: str):
    """ Get AWS EBS volume object. """
    
    data = None
    
    client = get_ec2_client()
    
    try:
        
        data = client.describe_volumes(VolumeIds=[volume_id])['Volumes'][0]
    
    except Exception as e:
        
        print('Exception: %s' % str(e))
        pass
    
    return data


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--instance_id', required=True,
                        help='Instance ID of source EC2 instance.')
    parser.add_argument('--region', required=True, help='AWS region that the instance is in.')
    parser.add_argument('--aws_access_key_id', required=True, help='AWS access key ID.')
    parser.add_argument('--aws_secret_access_key', required=True, help='AWS secret access key.')
    parser.add_argument('--target_size', type=int, required=True, help='Target size of volume in GB.')
    
    args = parser.parse_args()
    
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
        print('- Root volume ID invalid: %s. Exiting.' % root_volume_id)
        exit(0)
    
    root_volume = get_volume_object(volume_id=root_volume_id)
    
    if args.target_size < root_volume['Size']:
        
        print('- Shrinking volume from %f to %f.' % (root_volume['Size'], args.target_size))
        
        # Stop Instance
        print('- Stopping instance...')
        stop_ec2_instance(instance_id=args.instance_id)
        
        # Create snapshot of root volume of the original size
        print('- Creating snapshot of instance root volume...')
        root_volume_snapshot = create_snapshot(volume_id=root_volume_id)
        root_volume_snapshot_id = root_volume_snapshot['SnapshotId']
        print('- Root volume snapshot ID is %s.' % root_volume_snapshot_id)
        
        # Create new clone volume of root volume
        print('- Creating new volume from snapshot of instance root volume...')
        clone_volume = create_volume(az=root_volume['AvailabilityZone'], iops=root_volume['Iops'],
                                     size=args.target_size,
                                     volume_type=root_volume['VolumeType'], SnapshotId=root_volume_snapshot_id)
        
        # Create empty volume of new size
        print('- Creating empty volume of size %s...' % str(args.target_size))
        new_volume = create_volume(az=root_volume['AvailabilityZone'], iops=root_volume['Iops'],
                                   size=args.target_size,
                                   volume_type=root_volume['VolumeType'])
        
        # Attach 2 new volumes to instance
        print('- Mounting both new volumes in instance...')
        attach_volume(instance_id=args.instance_id, volume_id=clone_volume['VolumeId'], device='/dev/sdy')
        attach_volume(instance_id=args.instance_id, volume_id=new_volume['VolumeId'], device='/dev/sdz')
        
        # Start Instance
        print('- Starting instance...')
        start_ec2_instance(instance_id=args.instance_id)
    
    elif args.target_size > root_volume['Size']:
        
        print('- Expanding volume from %f to %f.' % (root_volume['Size'], args.target_size))
        pass
    else:
        
        print('- Volume size change is not required.')
