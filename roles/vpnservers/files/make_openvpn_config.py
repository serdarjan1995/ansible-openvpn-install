#!/usr/bin/python3
import argparse

SCRIPT_DESC = "Python script to create openvpn config"

SERVER_CONFIG_TEMP = """port {port}
proto {protocol}
dev tun
ca ca.crt
cert server.crt
key server.key
dh dh.pem
tls-auth ta.key 0
topology subnet
duplicate-cn
server {ip} {mask}
ifconfig-pool-persist /var/log/openvpn/ipp-{ip}.txt
push "redirect-gateway def1 bypass-dhcp"
push "dhcp-option DNS 208.67.222.222"
push "dhcp-option DNS 208.67.220.220"
keepalive 10 90
cipher AES-256-CBC
auth SHA256
compress lz4-v2
push "compress lz4-v2"
max-clients 100
user nobody
group nogroup
persist-key
persist-tun
status /var/log/openvpn/openvpn-status-{ip}.log
log-append  /var/log/openvpn/openvpn-{ip}.log
verb 6
mute 20
script-security 2
auth-user-pass-verify {username_check} via-file
"""

CLIENT_CONFIG_TEMP = """client
dev tun
proto {protocol}
remote {ip} {port}
resolv-retry infinite
nobind
user nobody
group nogroup
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-CBC
auth SHA256
comp-lzo
verb 3
mute 20
auth-user-pass
key-direction 1

#comment out if you use systemd-resolved
; script-security 2
; up /etc/openvpn/update-systemd-resolved
; down /etc/openvpn/update-systemd-resolved
; down-pre
; dhcp-option DOMAIN-ROUTE .

#comment out if you use resolvconf
; script-security 2
; up /etc/openvpn/update-resolv-conf
; down /etc/openvpn/update-resolv-conf
"""

def main(args):
    config_type = args.type
    ip = args.ip
    port = args.listen_port
    protocol = args.protocol
    output = args.output
    version = args.version
    if config_type == 'server':
        ip = args.ip
        mask = args.mask
        username_check = args.username_check
        config = SERVER_CONFIG_TEMP
        if version == '2.5':
            config += "data-ciphers AES-256-GCM:AES-128-GCM\ndata-ciphers-fallback AES-256-CBC"
        with open(output, 'w') as o_file:
            o_file.write(config.format(ip=ip,
                                       mask=mask,
                                       username_check=username_check,
                                       port=port,
                                       protocol=protocol))
    elif config_type == 'client':
        cert = args.cert
        key = args.key
        ca = args.cert_authority
        ta = args.tls_auth
        config = CLIENT_CONFIG_TEMP
        if version == '2.5':
            config += "data-ciphers AES-256-GCM:AES-128-GCM\ndata-ciphers-fallback AES-256-CBC"
        
        config = config.format(ip=ip,
                               port=port,
                               protocol=protocol)
        if protocol == 'udp':
            config = config + '\nexplicit-exit-notify 1'
        
        config += '\n<ca>\n'
        with open(ca, 'r') as ca_file:
            config += ca_file.read()
        config += '</ca>\n'
        
        config += '<cert>\n'
        with open(cert, 'r') as cert_file:
            write = False
            for line in cert_file:
                if '-----BEGIN CERTIFICATE-----' in line:
                    write = True
                if write:
                    config += line
        config += '</cert>\n'
        
        config += '<key>\n'
        with open(key, 'r') as key_file:
            config += key_file.read()
        config += '</key>\n'
        
        config += '<tls-auth>\n'
        with open(ta, 'r') as ta_file:
            config += ta_file.read()
        config += '</tls-auth>\n'
        
        with open(output, 'w') as o_file:
            o_file.write(config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=SCRIPT_DESC)
    parser.add_argument('-t', '--type', type=str, default='server',
                        help='config type ( client | server )\n'+
                             'default=server')
    parser.add_argument('-c', '--cert', type=str,
                        help='client cert (For client config)')
    parser.add_argument('-k', '--key', type=str,
                        help='client key (For client config)')
    parser.add_argument('-a', '--cert-authority', type=str,
                        help='CA cert (For client config)')
    parser.add_argument('-s', '--tls-auth', type=str,
                        help='TA file (For client config)')
    parser.add_argument('-i', '--ip', type=str, required=True,
                        help='server ip')
    parser.add_argument('-m', '--mask', type=str,
                        help='server ip range (mask)')
    parser.add_argument('-l', '--listen-port', type=str, required=True,
                        help='openvpn serve port')
    parser.add_argument('-p', '--protocol', type=str,
                        default='udp',
                        help='protocol ( tcp | udp )\n'+
                             'default=udp')
    parser.add_argument('-u', '--username-check', type=str,
                        help='username check script')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='output filename')
    parser.add_argument('-v', '--version', type=str, default='2.4',
                        help='OpenVpn version, default=2.4')
    main(parser.parse_args())
