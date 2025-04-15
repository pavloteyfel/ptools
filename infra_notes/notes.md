# gather domain names
```bash

# network traffic, arp, mdns
wireshark -E eth0
responder -A -I eth0

nbtscan -r <target-ip range>
nmblookup -A <ip>

# 445
rpcclient -U "" <target-ip>
#> srvinfo
#> enumdomains
#> querydominfo <domain-name>

# 445
netexec smb <target-ip>
sudo nmap <ip> -sV -sC -p139,445

# Zone transfer - 53
dig @<dns-ip> -t ns .
dig @<dns-ip> -t soa .
dig @nameserver axfr mydomain.com

# ldap - 389
ldapsearch -x -H ldap://<target-ip> -s base namingcontexts

# web redirects
curl -kI https://<ip>
curl -I http://<ip>

# certs
openssl s_client -connect <ip>:443

```

# gather users
```bash
# kerbrute
kerbrute userenum -d <domname> --dc ip userlist.txt -o valid_users
samrdump.py 10.129.14.128
```


# smb
```bash
#Dump interesting information 
enum4linux -a [-u "<username>" -p "<passwd>"] <IP> 
enum4linux-ng -A [-u "<username>" -p "<passwd>"] <IP> 
nmap --script "safe or smb-enum-*" -p 445 <IP>
```