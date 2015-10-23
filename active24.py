#!/usr/bin/env python3
'''
Script which checks DNS record and updates if IP address differs
if IP address is not set, chooses public IP
'''

import argparse
import subprocess
from suds.client import Client
import datetime


def get_ip(ip):
    '''Check if IP is set, if not, get public IP'''
    if ip is not None:
        return ip
    print('Digging IP')
    newip = subprocess.getoutput(
        'dig +short myip.opendns.com @resolver1.opendns.com').split()[0]
    print('Using your public ip: ' + newip)
    return newip


def check_errors(result):
    if len(result.errors) != 0:
        print(result.errors[0].item[0].value[0])
        exit(1)


def create_record(client, ip, ttl, domain, record_type, name):
    '''Creates new DNS record'''
    newrecord = client.factory.create('DnsRecord' + str(record_type))
    newrecord['from'] = datetime.datetime.utcnow()
    newrecord['to'] = datetime.datetime.utcfromtimestamp(2147483647)
    if ttl is None:
        ttl = 3600
    newrecord.ttl = ttl
    newrecord.type = client.factory.create('soapenc:string')
    newrecord.type.value = record_type
    newrecord.ip.value = ip
    newrecord.name.value = name
    newrecord.value = client.factory.create('soapenc:Array')
    newrecord.value.item = [newrecord.ip]
    # print(newrecord)
    result = client.service.addDnsRecord(newrecord, domain)
    check_errors(result)
    print('New DNS record created.')


def update_record(client, dnsrecord, ip, ttl, domain, record_type):
    '''Modifies existing DNS record'''
    if dnsrecord.ip != ip and ttl != dnsrecord.ttl:
        print('Updating record')
        newrecord = client.factory.create('DnsRecord' + str(record_type))
        newrecord['from'] = datetime.datetime.utcnow()
        newrecord.id = dnsrecord.id
        newrecord.to = dnsrecord.to
        if ttl is None:
            ttl = dnsrecord.ttl
        newrecord.ttl = ttl
        newrecord.type = client.factory.create('soapenc:string')
        newrecord.type.value = record_type
        newrecord.ip.value = ip
        newrecord.name.value = dnsrecord.name
        newrecord.value = client.factory.create('soapenc:Array')
        result = client.service.updateDnsRecord(newrecord, domain)
        check_errors(result)
        print('DNS record updated')
    else:
        print('DNS record already has same IP and TTL')


def delete_record(client, record):
    '''Deletes existing DNS record'''
    result = client.service.deleteDnsRecord(record.id, domain)
    check_errors(result)
    print('Record deleted.')


def get_record(client, domain, name, record_type):
    '''finds DNS recodr by Name and Type'''
    result = client.service.getDnsRecords(domain)
    check_errors(result)
    dnsrecord = None
    for record in result.data:
        if (record.type == record_type) and (record.name == name):
            dnsrecord = record
    if dnsrecord is None:
        print('DNS Record not found')
        client.service.logout()
        exit(1)
    return dnsrecord


def record_action(args):
    '''Update DNS record'''

    login = args.login
    password = args.password
    domain = args.domain
    record_type = args.record
    name = args.name
    action = args.action
    ttl = args.ttl
    if action in ['UPDATE', 'CREATE']:
        ip = get_ip(args.ip)

    client = Client(
        'https://centrum.active24.cz/services/a24PartnerService?wsdl')

    # login
    result = client.service.login(args.login, args.password)
    check_errors(result)

    if action == 'DELETE':
        dnsrecord = get_record(client, domain, name, record_type)
        delete_record(client, record)

    if action == 'UPDATE':
        dnsrecord = get_record(client, domain, name, record_type)
        update_record(client, dnsrecord, ip, ttl, domain, record_type)

    if action == 'CREATE':
        create_record(client, ip, ttl, domain, record_type, name)

    # logout
    result = client.service.logout()
    print('Done')


def main():
    parser = argparse.ArgumentParser(
        description='''Updates DNS record on Active24,
        if IP is not set, sets public IP.
        Updates record only if IP and TTL are different than already set.''')
    parser.add_argument('-l', '--login', required=True, dest='login',
                        help='Active24 login name', type=str)
    parser.add_argument('-p', '--password', required=True, dest='password',
                        help='Active24 password', type=str)
    parser.add_argument('-d', '--domain', required=True, dest='domain',
                        help='Domain name', type=str)
    parser.add_argument('-r', '--record', nargs='?', dest='record', default='A',
                        choices=['A', 'AAAA'], help='Record type, default=A', type=str)
    parser.add_argument('-i', '--ip', dest='ip', nargs='?', type=str,
                        help='IP address')
    parser.add_argument('-n', '--name', required=True, dest='name', type=str,
                        help='DNS record name (without domain)')
    parser.add_argument('-t', '--ttl', nargs='?', dest='ttl',
                        help='TTL in seconds, if empty, uses TTL from DNSrecord', type=str)
    parser.add_argument('-a', '--action', nargs='?', dest='action', default='UPDATE',
                        choices=['UPDATE', 'CREATE', 'DELETE'], help='Action type, default=UPDATE', type=str)

    record_action(parser.parse_args())

if __name__ == '__main__':
    main()
