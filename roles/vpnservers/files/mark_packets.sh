#!/bin/bash
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root" 
    exit 1
fi

if [ -z "$1" ]; then
    echo "No input file provided"
    exit 1
fi

while IFS= read -r interface
do
    if [ -z "$interface" ]; then
        echo "Interface not provided"
        exit 1
    fi
    TEST_INTERFACE=`ifconfig | grep -w $interface`
    if [ -z "$TEST_INTERFACE" ]; then
        echo "Interface not found: $interface"
        exit 1
    fi
    iptables -I FORWARD -i $interface -j MARK --set-mark 11
    iptables -I FORWARD -o $interface -j MARK --set-mark 11
done < "$1"
