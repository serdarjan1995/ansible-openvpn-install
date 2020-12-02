#!/usr/bin/python3

import os
import sys
import requests
import json
import argparse

SCRIPT_DESC = "Python script for converting .ovpn configs to json format and "
SCRIPT_DESC += "posting to backend api"
IPSTACK_APIKEY = '18ee3005da87fb8725d51d8323710904'
VERIFY_SSL = False

def main(args):
    filename = args.file
    premium = args.premium
    url_base = args.url
    auth_token = args.auth_token
    
    if url_base[-1] == '/':
        url_base = url_base[0:-1]
    
    with open(filename, 'r') as f:
        f_content = f.read()
    
    servers = {}
    vpn_config = {}
    tag = ''
    tag_content = ''
    tag_open = False
    for line in f_content.split('\n'):
        if len(line) > 3 and '#' not in line and ';' not in line:
            if '</' in line:
                vpn_config[tag] = tag_content
                tag = ''
                tag_content = ''
                tag_open = False
                continue
            elif '<' in line:
                tag = line.replace('<','').replace('>','').replace('\n','')
                tag_open = True
                continue
            
            if tag_open:
                tag_content += line
            else:
                splitted = line.split()
                if len(splitted) == 1:
                    vpn_config[splitted[0]] = True
                elif len(splitted) == 2:
                    vpn_config[splitted[0]] = splitted[1]
                else:
                    vpn_config[splitted[0]] = line.replace(splitted[0]+' ','')
        
    ip, port = vpn_config['remote'].split()
    if ip not in servers.keys():
        servers[ip] = {}
    servers[ip][port] = vpn_config
        
    headers = { 'Authorization': 'Token ' + auth_token }
    
    for ip in servers.keys():
        resp = requests.get(url_base + '/servers/' + ip, headers=headers, verify=VERIFY_SSL)
        if resp.status_code != 200:
            ipstack_resp = requests.get('http://api.ipstack.com/' + ip + '?access_key='
                                        + IPSTACK_APIKEY + '&format=1')
            ipstack_resp_json = json.loads(ipstack_resp.text)
            
            url = url_base + '/servers/'
            resp = requests.post(url, data={'ip': ip,
                                            'country': ipstack_resp_json['country_code'],
                                            'city': ipstack_resp_json['region_name'],
                                            'free': premium}, headers=headers, verify=VERIFY_SSL)
            print('Creating server ', ip, ' ............... ', resp.status_code)
            if resp.status_code > 201:
                sys.exit(resp.content)  
        for port in servers[ip].keys():
            url = url_base + '/servers/' + ip + '/instances/'
            resp = requests.post(url, data={'port': port,
                                            'protocol': servers[ip][port]['proto'],
                                            'auth': True}, headers=headers, verify=VERIFY_SSL)
            print('---Creating instance ', port, ' ........ ', resp.status_code)
            if resp.status_code > 201:
                sys.exit(resp.content)  
            
            url = url_base + '/servers/' + ip + '/instances/' + port + '/config/'
            resp = requests.post(url, data=servers[ip][port], headers=headers, verify=VERIFY_SSL)
            print('-------Creating config ', port, ' .... ', resp.status_code)
            if resp.status_code > 201:
                sys.exit(resp.content) 
            
            url = url_base + '/servers/' + ip + '/instances/' + port + '/config/file/'
            resp = requests.post(url, data=f_content, headers={**{'Content-type':'text/plain'}, **headers},
                                 verify=VERIFY_SSL)
            print('-------Creating config file', port, ' .... ', resp.status_code)
            if resp.status_code > 201:
                sys.exit(resp.content) 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=SCRIPT_DESC,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-f', '--file', type=str, required=True,
                        help='.ovpn config file input path\n')
    parser.add_argument('-u', '--url', type=str, required=True,
                        help='Url base to post converted to json format configs\n'+
                        'Example: https://tenorvpn.com')
    parser.add_argument('-a', '--auth-token', type=str, required=True,
                        help='Server authentication token')
    parser.add_argument('-p', '--premium', type=bool,
                        default=True,
                        help='Mark servers as premium\n' +
                             'Default: True')

    main(parser.parse_args())
