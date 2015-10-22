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
    else:
        print('Digging IP')
        newip = subprocess.getoutput(
            'dig +short myip.opendns.com @resolver1.opendns.com').split()[0]
        print('Using your public ip: ' + newip)
        return newip


def check_errors(result):
    # print result
    if len(result.errors) != 0:
        print(result.errors[0].item[0].value[0])
        exit(1)


def update_record(args):
    '''Update DNS record'''

    login = args.login
    password = args.password
    domain = args.domain
    record_type = args.record
    name = args.name
    ip = get_ip(args.ip)
    ttl = args.ttl

    client = Client(
        'https://centrum.active24.cz/services/a24PartnerService?wsdl')

    # login
    result = client.service.login(args.login, args.password)
    check_errors(result)

    result = client.service.getDnsRecords(domain)
    check_errors(result)

    for record in result.data:
        if (record.type == record_type) and (record.name == name):
            dnsrecord = record

    if dnsrecord is None:
        print('DNS Record not found')
        client.service.logout()
        exit(1)

    if dnsrecord.ip != ip:
        print('Updating record')
        print(dnsrecord)
        newrecord = client.factory.create('DnsRecord'+str(record_type))
        newrecord['from'] = datetime.datetime.utcnow()
        # strftime("%Y-%m-%d %H:%M:%S", gmtime())
        newrecord.id = dnsrecord.id
        newrecord.to = dnsrecord.to
        newrecord.ttl = ttl
        newrecord.type = client.factory.create('soapenc:string')
        newrecord.type.value = record_type
        newrecord.ip.value = ip
        newrecord.name.value = dnsrecord.name
        # dnsrecord.ip = ip
        # dnsrecord.value[0] = ip
        # dnsrecord.ttl = int(ttl)
        # result = client.service.updateDnsRecord(newrecord, domain)
        # check_errors(result)
        # print(result)
        print(newrecord)
        print('DNS record updated')

    # print result

    # logout
    result = client.service.logout()
    print('Done')


def main():
    parser = argparse.ArgumentParser(
        description='''Updates DNS record on Active24,
        if IP is not set, sets public IP.''')
    parser.add_argument('-l', '--login', required=True, dest='login',
                        help='Active24 login name', type=str)
    parser.add_argument('-p', '--password', required=True, dest='password',
                        help='Active24 password', type=str)
    parser.add_argument('-r', '--record', nargs='?', dest='record', default='A',
                        choices=['A', 'AAAA'], help='Record type, default=A', type=str)
    parser.add_argument('-d', '--domain', required=True, dest='domain',
                        help='Domain name', type=str)
    parser.add_argument('-i', '--ip', dest='ip', nargs='?', type=str,
                        help='IP address')
    parser.add_argument('-n', '--name', required=True, dest='name', type=str,
                        help='DNS record name (without domain)')
    parser.add_argument('-t', '--ttl', nargs='?', default='3600', dest='ttl',
                        help='TTL in seconds, default=3600', type=str)

    update_record(parser.parse_args())

if __name__ == '__main__':
    main()
