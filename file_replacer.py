#!/usr/bin/env python

#1. apt-get install build-essential python-dev libnetfilter-queue-dev
#2. apt install python3-pip git libnfnetlink-dev libnetfilter-queue-dev
#3. pip3 install NFQP3 --> install netfilterqueue
import netfilterqueue
import scapy.all as scapy

def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.Raw):
        print(scapy.show())


    packet.accept()

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()