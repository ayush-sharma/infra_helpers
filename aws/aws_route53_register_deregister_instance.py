import boto3
import requests
import argparse
import socket
import struct
import sys
from time import sleep


def add_entry(this_ip: str, hosted_zone_id: str, record_bucket: int, record_set_name: str, record_type: str,
              record_ttl: str, ip_list: list):
    """ Add entry for this machine in record set. """
    
    response = ''
    
    route53_client = boto3.client('route53')
    
    counter = 1
    while counter <= 25:
        
        try:
            response = route53_client.change_resource_record_sets(
                    HostedZoneId=hosted_zone_id,
                    ChangeBatch={
                        'Comment': 'string',
                        'Changes': [
                            {
                                'Action'           : 'UPSERT',
                                'ResourceRecordSet': {
                                    'Name'           : record_set_name,
                                    'Type'           : record_type,
                                    'TTL'            : record_ttl,
                                    'ResourceRecords': ip_list,
                                    'Weight'         : 1,
                                    'SetIdentifier'  : record_set_name + '_' + str(record_bucket)
                                    # 'HealthCheckId': 'string',
                                }
                            },
                        ]
                    }
            )
            
            print(this_ip + ' >>> IP insert complete.')
            
            break
        
        except Exception as e:
            
            sleepy_time = counter ** 2
            print(this_ip + ' XXX Exception: %s' % str(e.args))
            print(this_ip + ' XXX Iteration %s, sleeping for %s seconds.' % (str(counter), str(sleepy_time)))
            sleep(sleepy_time)
        
        counter += 1
    
    return response


def remove_entry(this_ip: str, hosted_zone_id: str, record_bucket: int, record_set_name: str, record_type: str,
                 record_ttl: str, ip_list: list):
    """ Remove entry for this machine in record set. """
    
    response = ''
    
    route53_client = boto3.client('route53')
    
    counter = 1
    while counter <= 25:
        
        try:
            response = route53_client.change_resource_record_sets(
                    HostedZoneId=hosted_zone_id,
                    ChangeBatch={
                        'Comment': 'string',
                        'Changes': [
                            {
                                'Action'           : 'DELETE',
                                'ResourceRecordSet': {
                                    'Name'           : record_set_name,
                                    'Type'           : record_type,
                                    'TTL'            : record_ttl,
                                    'ResourceRecords': ip_list,
                                    'Weight'         : 1,
                                    'SetIdentifier'  : record_set_name + '_' + str(record_bucket)
                                    # 'HealthCheckId': 'string',
                                }
                            },
                        ]
                    }
            )
            
            print(this_ip + ' >>> IP delete complete.')
            
            break
        
        except Exception as e:
            
            sleepy_time = counter ** 2
            print(this_ip + ' XXX Exception: %s' % str(e.args))
            print(this_ip + ' XXX Iteration %s, sleeping for %s seconds.' % (str(counter), str(sleepy_time)))
            sleep(sleepy_time)
        
        counter += 1
    
    return response


def get_ip_bucket(ip):
    """ Convert an IP string to long. """
    
    packed_ip = socket.inet_aton(ip)
    return struct.unpack("!L", packed_ip)[0] % 100


def get_ips_for_bucket(hosted_zone_id, record_name, bucket):
    response = ''
    
    route53_client = boto3.client('route53')
    
    counter = 1
    while counter <= 25:
        
        try:
            response = route53_client.list_resource_record_sets(
                    HostedZoneId=hosted_zone_id
            )
            
            break
        
        except Exception as e:
            
            sleepy_time = counter ** 2
            print('Exception trying to get list of records for bucket.')
            print('XXX Exception: %s' % str(e.args))
            print('XXX Iteration %s, sleeping for %s seconds.' % (str(counter), str(sleepy_time)))
            sleep(sleepy_time)
        
        counter += 1
    
    response = response['ResourceRecordSets']
    
    ip_list = []
    for response_item in response:
        
        if 'SetIdentifier' in response_item and response_item['SetIdentifier'] == record_name + '_' + str(bucket):
            
            for resource_records in response_item['ResourceRecords']:
                ip_list.append(resource_records['Value'])
    
    return ip_list


def get_value_string_from_ips(ip_list: list):
    ip_string = []
    tmp = {}
    for ip in ip_list:
        tmp['Value'] = ip
        ip_string.append(tmp)
        tmp = {}
    
    return ip_string


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--record_name', required=True,
                        help='Value of record name for the record set entry.')
    parser.add_argument('--record_type', required=True, help='Record type.')
    parser.add_argument('--record_ttl', required=True, type=int, help='Record TTL.')
    parser.add_argument('--hosted_zone_id', required=True,
                        help='Route 53 hosted zone ID of zone to which this entry will be added.')
    parser.add_argument('--action', required=True, choices=['add', 'remove'],
                        help='Whether to add or remove the entry for this machine.')
    parser.add_argument('--testing_ip', help='IP address to use for testing.')
    
    args = parser.parse_args()
    
    if args.testing_ip:
        my_ip = args.testing_ip
    else:
        my_ip = requests.get('http://www.wgetip.com').text
    
    ip_bucket = get_ip_bucket(my_ip)
    ips = get_ips_for_bucket(args.hosted_zone_id, args.record_name, ip_bucket)
    
    already_exists = False
    if args.action == 'add':
        
        print(my_ip + ' --- Adding entry in hosted zone %s, record name %s, TTL %s, and IP %s, in record bucket %s.' % (
            args.hosted_zone_id, args.record_name, args.record_ttl, my_ip, ip_bucket))
        
        for item in ips:
            
            if item == my_ip:
                already_exists = True
                print(my_ip + ' >>> IP already exists. Exiting.')
                sys.exit(1)
        
        if ~ already_exists:
            print(my_ip + ' >>> IP does not already exist. Adding now.')
            ips.append(my_ip)
        
        values = get_value_string_from_ips(ips)
        
        add_entry(this_ip=my_ip, hosted_zone_id=args.hosted_zone_id, record_bucket=ip_bucket,
                  record_set_name=args.record_name,
                  record_type=args.record_type,
                  record_ttl=args.record_ttl, ip_list=values)
    
    elif args.action == 'remove':
        
        print(
                my_ip + ' --- Removing entry in hosted zone %s, record name %s, TTL %s, and IP %s, in record bucket %s.' % (
                    args.hosted_zone_id, args.record_name, args.record_ttl, my_ip, ip_bucket))
        
        if len(ips) == 1 and ips[0] == my_ip:
            
            print(my_ip + ' >>> This is the only value in the record. Removing entire record.')
            
            values = get_value_string_from_ips(ips)
            
            remove_entry(this_ip=my_ip, hosted_zone_id=args.hosted_zone_id, record_bucket=ip_bucket,
                         record_set_name=args.record_name,
                         record_type=args.record_type,
                         record_ttl=args.record_ttl, ip_list=values)
        else:
            
            if my_ip in ips:
                
                print(my_ip + ' >>> Removing IP from record.')
                
                ips.remove(my_ip)
                values = get_value_string_from_ips(ips)
                
                add_entry(this_ip=my_ip, hosted_zone_id=args.hosted_zone_id, record_bucket=ip_bucket,
                          record_set_name=args.record_name,
                          record_type=args.record_type,
                          record_ttl=args.record_ttl, ip_list=values)
            else:
                print(my_ip + ' >>> IP not present in record.')
    else:
        print(my_ip + ' --- Incorrect action.')
