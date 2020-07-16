# Me In The Middle

Me In The Middle is a pentration testing and red team tool for achieving MITM positioning on a local network, and facilitating additional attacks once your device is in the middle. The core functionality is written in Python with a Bash wrapper script that provides a command-line interface.

DO NOT use this program to target machines you do not own without express written permission.

***

## Installation Instructions + Dependencies

<b>TO-DO</b>

## Capabilities and Use

### Network Scanning and Target Selection

Me In The Middle sends ARP packets for quick scanning of the local subnet. It accepts CIDR notation as an argument to determine which subnet to scan. You may also skip the scan by providing the target device IP and the gateway router IP at the command line.

```./main.sh <subnet>```
or
```./main.sh <target_ip> <gateway_router_ip>```

If main.sh is run without arguments, it will prompt for a subnet to scan.

Once you have your scan results, select a target device and initiate the MITM attack. The gateway router is automatically detected and spoofed, using regular ARP broadcasts to intercept traffic between the router and the target.

### Credential Sniffing and sslstrip

Once the attack begins, sslstrip (installed separately - see instructions above) and packet_sniffer.py begin to run. 

[sslstrip](https://github.com/moxie0/sslstrip) is a tool by Moxie Marlinspike that blocks external sites from requesting a protocol upgrade from HTTP to HTTPS-- that is, if the target types "google.com" into their browser, sslstrip can cause them to access the unencrypted http://google.com and allow us to view traffic in the clear.

packet_sniffer.py is Me In The Midddle's packet sniffer tool. It checks every packet coming over the wire for login credentials, ad saves those credentials in ./output.txt. (By default, it it does not save any credential-free packets to your drive).

### DNS Spoofing

The DNS Spoof module alters DNS responses coming from an external DNS server back to the target device, editing the IP address of the response packet to match a server of your choice. 

By default, the module alters *all* DNS responses and edits them. It also autodetects your own IP address and inserts that into each DNS response. This allows for the creation of a makeshift "captive portal." 

In our example, the targeted user must input credentials on our malicious webpage and click Sign In to escape the portal. Those credentials are caught by Me In The Middle's packet sniffer and saved to output.txt. (The Sign In button on this sample page sends a crafted response to a specific URL, which is detected by the DNS spoofer as a signal to end the attack and stop altering packets.)

Since DNS traffic is normally unencrypted, this module does not depend on sslstrip to downgrade the target's web protocol.

### File Replacement

The File Replacement module detects when the user attempts to download a file with a certain file extension. It then redirects that user to download a file of your choice (from a server of your choice) instead.

Both the redirect link and the file extension to detect are predefined in file_replacer.py. The ability to input those options on chossing this module is planned for a future update.

### Code Injection

This powerful module intercepts HTML files sent from an external server to the target machine, and edits those responses to include Javascript (or other code) of your choice. This code will be executed in the target's browser whenever they load a compatible HTML page, allowing XSS-style attacks across a variety of sites. In tests, this attack succeeded against browsers visiting google.com, bing.com, and more.

The Javascript to execute is predefined in code_injector.py. The ability to input a line of code or read code from an external file, and then inject that code, is planned for a future update.

### Mac Address Spoofing

This module is not included in the main wrapper as of July 2020, but MACChanger.py can be run on its own to spoof your MAC address to other devices on the network. Use it to get around MAC blacklisting or add a layer of protection to your identity on the network.
