#!/usr/bin/env python3

# scapy module lets us work with network packets
# you must use this command to forward packets echo 1 > /proc/sys/net/ipv4/ip_forward 

import scapy.all as scapy
import sys
import time
import optparse
import socket
import struct
import sys
from termcolor import colored, cprint 
  
#text = colored('Hello, World!', 'red', attrs=['reverse', 'blink']) 

def get_default_gateway_linux():
    """Read the default gateway directly from /proc."""
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue

            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

gateway_ip = get_default_gateway_linux()


def py_scan(ip):

    # what subnet are we scanning?
    arp_request = scapy.ARP(pdst=ip)

    # Broadcast our ARP to all devices on the network with ff:ff:ff:ff:ff:ff
    broadcast_destination = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")

    # ARP packets contain two main parts 1. The subnet to scan 2. The broadcast address
    arp_request_packet = broadcast_destination/arp_request

    # Now lets catch the responses in a variable
    # note that we timeout after one second so our script doesnt just hang, waiting for a response

    responses = scapy.srp(arp_request_packet, timeout=1)[0]

    # lets see who responded with a scapy function called .summary()
    # print(responses.summary())
    print('\n')
    print("ID\tIP\t\t\tAt MAC Address\n---------------------------------------------------")
    counter = 1
    results = []
    for response in responses:
        if response[1].psrc == gateway_ip:
            device_id = "Gateway Router"
            color = "yellow"
        else:
            device_id = response[1].hwsrc
            color = "white"
        new_result = (str(counter) + ")\t" + response[1].psrc + "\t\t" + device_id)
        results.append(new_result)
#        if gateway_ip in new_result:
#            new_result += " - Gateway Router"
        print(colored(new_result, color))
        print("---------------------------------------------------")
        counter += 1
    return results
target_subnet = sys.argv[1]
ip_options = py_scan(target_subnet)
print("\n")

result_id = int(input("ID Number of the address you want to target: "))
print("\n")

ip_selection = (ip_options[result_id - 1])
ip_selection = ip_selection.split("\t")
ip_selection = ip_selection[1]

#print(f"Spoofing target {ip_selection} and gateway router {gateway_ip}", end = '')

with open('/tmp/mitm.txt', 'w') as output:
    output.write(f"{ip_selection} {gateway_ip}")
