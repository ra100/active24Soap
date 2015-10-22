#!/usr/bin/env python
'''
Script which checks DNS record and updates if IP address differs
if IP address is not set, chooses public IP
'''

import argparse
import subprocess as sp
from suds.client import Client

def getIP(ip):
    '''Check if IP is set, if not, get public IP'''

    if ip is not None:
        return ip
    else:
        print 'Digging IP'
        newIp = sp.getoutput(
            'dig +short myip.opendns.com @resolver1.opendns.com').split()[0]
        print 'Using your public ip: ' + newIp
        return newIp


def checkErrors(result):
    # print result
    if len(result.errors) != 0:
        print result.errors[0].item[0].value[0]
        exit(1)


def updateRecord(args):
    '''Update DNS record'''

    login = args.login
    password = args.password
    domain = args.domain
    record = args.record
    name = args.name
    ip = getIP(args.ip)
    ttl = args.ttl

    client = Client(
        'https://centrum.active24.cz/services/a24PartnerService?wsdl')

    # login
    result = client.service.login(args.login, args.password)
    checkErrors(result)

    result = client.service.getDnsRecords('ra100.net')
    checkErrors(result)
    print result

    # logout
    result = client.service.logout()
    print 'Done'


def main():
    parser = argparse.ArgumentParser(
        description='''Updates DNS record on Active24,
        if IP is not set, sets public IP.''')
    parser.add_argument('-l', '--login', required=True, dest='login',
                        help='Active24 login name')
    parser.add_argument('-p', '--password', required=True, dest='password',
                        help='Active24 password')
    parser.add_argument('-r', '--record', nargs='?', dest='record', default='A',
                        choices=['A', 'AAAA'], help='Record type, default=A')
    parser.add_argument('-d', '--domain', required=True, dest='domain',
                        help='Domain name')
    parser.add_argument('-i', '--ip', dest='ip', nargs='?',
                        help='IP address')
    parser.add_argument('-n', '--name', required=True, dest='name',
                        help='DNS record name')
    parser.add_argument('-t', '--ttl', nargs='?', default='3600', dest='ttl',
                        help='TTL in seconds, default=3600')

    updateRecord(parser.parse_args())

if __name__ == '__main__':
    main()
