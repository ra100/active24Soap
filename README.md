# active24Soap

Python script for updating DNS records on Active24.cz

With this script you can update A and AAAA records on active24.cz, you need
to enter your login and password, name of the domain, name of DNS record and IP
address. If IP address is not set, script uses ```dig``` to find out what your
public IP is and sets that instead. If no TTL is set, this won't change.

You can use this script to dynamically change your IP of your machine using
cron.

## Requirements

+   python2 or python3
+   suds-jurko
+   argparse

## Installation

get script copy

```bash
git clone https://github.com/ra100/active24Soap
```

install required libraries

```bash
pip3 install suds-jurko
pip3 install argparse
```

## Usage

Show help ```./active24 -h```

```none
usage: active24.py [-h] -l LOGIN -p PASSWORD -d DOMAIN [-r [{A,AAAA}]]
                   [-i [IP]] -n NAME [-t [TTL]] [-a [{UPDATE,CREATE,DELETE}]]

Updates DNS record on Active24, if IP is not set, sets public IP. Updates
record only if IP and TTL are different than already set.

optional arguments:
  -h, --help            show this help message and exit
  -l LOGIN, --login LOGIN
                        Active24 login name
  -p PASSWORD, --password PASSWORD
                        Active24 password
  -d DOMAIN, --domain DOMAIN
                        Domain name
  -r [{A,AAAA}], --record [{A,AAAA}]
                        Record type, default=A
  -i [IP], --ip [IP]    IP address
  -n NAME, --name NAME  DNS record name (without domain)
  -t [TTL], --ttl [TTL]
                        TTL in seconds, if empty, uses TTL from DNSrecord
  -a [{UPDATE,CREATE,DELETE}], --action [{UPDATE,CREATE,DELETE}]
                        Action type, default=UPDATE
```

+   LOGIN - your active24 username
+   PASSWORD - your active24 password
+   DOMAIN - domain name you want to work with, e.g. ra100.net
+   A, AAAA - DNS record type you wish to change
+   NAME - name of DNS record, e.g. for awesome.ra100.net it will be 'awesome'
+   IP - (optional) IP address in format ```xxx.xxx.xxx.xxx```, if not set, your public IP will be used
+   TTL - (optional) TTL value, if not set, value from DNSrecord will be used
+   ACTION - (optiona) UPDATE, CREATE or DELETE record


By default works with python3, to run with python2 use:

```bash
python2 active24 -h
```

## cron example

add this to ```/etc/crontab``` or other equivalent file

```crontab
*/5 * * * * root /path/to/python /path/to/script/active24.py -l USERNAME -p PASSWORD -d example.cz -r A -n sub
```

This will check every 5 minutes public IP of machine, check it against DNS
records and when it's different, it updates that record.

## bugs

CREATE method is not working ```suds.WebFault: Server raised fault: 'java.lang.NullPointerException'```




