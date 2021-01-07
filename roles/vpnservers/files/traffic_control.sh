#!/bin/bash
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root" 
    exit 1
fi

if [ -z "$1" ]; then
    echo "No input file provided"
    exit 1
fi

if [ -z "$2" ]; then
    echo "Rate not provided"
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
    tc qdisc add dev $interface root handle 1: htb
    tc class add dev $interface parent 1:1 classid 1:11 htb rate $2 ceil $2
    tc qdisc add dev $interface parent 1:11 sfq perturb 10
    tc filter add dev $interface protocol ip parent 1: prio 1 handle 11 fw flowid 1:11
done < "$1"

