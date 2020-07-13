# Man in the Middle and Me

Now that we have successfully conducted a Man in the Middle attack with our ARP spoofer from the [Python Quick Scripts](https://github.com/ggedgerton/quickPythonScripts) walkthrough what do we do?

***

The ARP spoofing attack we are conducting is a credentials attack so let's capture some information from our target:

1. **Packet Sniffing** with Python

  - A packet sniffer intercepts log traffic that passes over a network

2. **File Intercepting** with Python

  - When our target downloads a file we are going to modify the download

3. **DNS Spoofer** with Python

***

## Packet Scanning with Python

<details> 
  <summary>Why would we want to capture network traffic?
  </summary>
All of CS boils down to controlling and understanding the flow of data. It is the basis of CIA and AAA. When we capture packets for analysis we are taking a look at the data and painting a deeper picture of what is going on with the network.
</details>

1. Let's take a look at who is on our Network

![ARP SCAN](./images/ARP_scan.png)

    I will be running an ARP Spoofing attack on 10.0.2.15 and our shared gateway router at IP address 10.0.2.1

2. Now that we have our target IP address we re going to run our ARP Spoof attack.

![ARP Spoof Attack](./images/arp_spoof.png)

    We are putting ourselves in the middle of the gateway router and target IP by sending packets to the target IP address claiming we are the gateway IP, and to the gateway IP,claiming we are the target IP. Passing packets back and forth as a middle man is great, but we want to actually see what is going on. For this we need a packet sniffer to capture network data.

3. From our attack machine we can launch our [packet sniffer script](packet_sniffer.py) and capture HTTP data. For this example our target user is signing on to the website http://testing-ground.scraping.pro/login with the credentials ggedgerton:PASSWORD123

![Packet Sniffing](./images/login_sniffed.png)

    This packet sniffer will only capture data that is sent in HTTP, but we can grab this data without the target ever even knowing.

<details> 
  <summary>Why is it much easier for us to steal HTTP data as opposed to HTTPS?
  </summary>
If you're thinking SSL certificates you are indeed correct! HTTP and HTTPS are the same protocol, however HTTPS has an additonal layer of security. Even if we were to capture HTTPS data we still could read it. (we'll not yet at least. Stay posted for a script to help us sidestep the HTTPS protocol)
</details>

***

## File Intercepting with Python

What are the steps to file intercepting?

    1. Our target makes an HTTP request to download a file
    
    2. We modify/replace the request without our target knowing

<details> 
  <summary>For what purpose would we want to replace our target's download file, with a file of our own?
  </summary>
For malware injection and execution.
</details>

1. Now that we have successfully put ourselves in between the gateway router and our target IP, and we are monitoring our targets HTTP request we want to look for a download request/reponse
