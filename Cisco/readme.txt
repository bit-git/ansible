As a quick reminder, we have three parts to our templating system - 

/home/omz/ansible/Cisco/roles/router

omz@DevOps:~/ansible/Cisco/roles/router$ ls
tasks  templates  vars

1)the tasks file (tasks/main.yml)
2)the vars file (vars/main.yml)
3)the template file (templates/router.j2)

These are all organized under an Ansible role (in my example, /home/omz/ansible/Cisco/roles/router)

configs are saved in CFG folder - tasks/main.yml

omz@DevOps:~/ansible/Cisco$ ls
CFGS  hosts  readme.txt  roles  site.yml


--- Cisco/site.yml ---
/home/omz/ansible/Cisco
omz@DevOps:~/ansible/Cisco$ cat site.yml 
---
- name: Generate router configuration files
  hosts: localhost

  roles:
    - router


--- tasks/main.yml ---
/home/omz/ansible/Cisco/roles/router/tasks
omz@DevOps:~/ansible/Cisco/roles/router/tasks$ cat main.yml 
---
- name: Generate configuration files
  template: src=router.j2 dest=/home/omz/ansible/Cisco/CFGS/{{item.hostname}}.txt
  with_items: test_routers


--- vars/main.yml ---
omz@DevOps:~/ansible/Cisco/roles/router/vars$ cat main.yml 
---
test_routers:
    - { hostname: twb-sf-rtr1,
        secret: apassword,
        timezone: PST,
        timezone_dst: PDT,
        timezone_offset: -8,
        DHCP: true,
        dhcp_exclude1_start: 10.1.1.1,
        dhcp_exclude1_end: 10.1.1.99,
        dhcp_network: 10.1.1.0,
        dhcp_netmask: 255.255.255.0,
        dhcp_gateway: 10.1.1.1,
        CBAC: true,
        public_ip: 6.6.6.6,
        public_netmask: 255.255.255.0,
        public_gateway: 6.6.6.1,
        vlan10_ip: 10.1.1.1,
        vlan10_network: 10.1.1.0 }
#   - { hostname: twb-sf-rtr2 }

#   - { hostname: twb-la-rtr1 }

#   - { hostname: twb-la-rtr2 }

#   - { hostname: twb-den-rtr1 }

cisco_881_l2_interfaces:
  - FastEthernet0
  - FastEthernet1
  - FastEthernet2
  - FastEthernet3


--- templates/router.j2 ---
no service pad
service tcp-keepalives-in
service tcp-keepalives-out
service timestamps debug datetime msec localtime show-timezone
service timestamps log datetime msec localtime show-timezone
service password-encryption
!
hostname {{item.hostname}}
!
boot-start-marker
boot-end-marker
!
logging buffered 32000
no logging console
enable secret 0 {{item.secret}}
!
aaa new-model
!
!
aaa authentication login default local-case
aaa authorization exec default local 
!
!
!
!
!
aaa session-id common
!
!
!
memory-size iomem 10
clock timezone {{item.timezone}} {{item.timezone_offset}}
clock summer-time {{item.timezone_dst}} recurring
!
no ip source-route
ip options drop
!
!
!
!
ip dhcp bootp ignore
{% if item.DHCP %} 
no ip dhcp conflict logging
ip dhcp excluded-address {{item.dhcp_exclude1_start}} {{item.dhcp_exclude1_end}}
!
ip dhcp pool POOL1
   network {{item.dhcp_network}} {{item.dhcp_netmask}}
   default-router {{item.dhcp_gateway}}
   dns-server 8.8.8.8 8.8.4.4
{% endif %}
!
!         
ip cef
no ip domain lookup
ip domain name whatever.com
{% if item.CBAC %}
ip inspect name INTERNET cuseeme
ip inspect name INTERNET dns
ip inspect name INTERNET ftp
ip inspect name INTERNET h323
ip inspect name INTERNET icmp
ip inspect name INTERNET imap
ip inspect name INTERNET pop3
ip inspect name INTERNET netshow
ip inspect name INTERNET rcmd
ip inspect name INTERNET realaudio
ip inspect name INTERNET rtsp
ip inspect name INTERNET sqlnet
ip inspect name INTERNET streamworks
ip inspect name INTERNET tftp
ip inspect name INTERNET vdolive
ip inspect name INTERNET pptp
ip inspect name INTERNET tcp router-traffic
ip inspect name INTERNET udp router-traffic
{% endif %}
no ipv6 cef
!
!
!
!
username admin privilege 15 secret 0 {{item.secret}}
!
!
ip ssh version 2
!
!
!
! 
!
!
!
!
!
!
!
!
{% for interface in cisco_881_l2_interfaces %}
interface {{interface}}
 switchport access vlan 10
 spanning-tree portfast
 !
!
{% endfor %}
interface FastEthernet4
 ip address {{item.public_ip}} {{item.public_netmask}}
 ip access-group INTERNET in
 no ip redirects
 no ip proxy-arp
 ip nat outside
{% if item.CBAC %} ip inspect INTERNET out
{% endif %}
 ip virtual-reassembly
 duplex auto
 speed auto
 no cdp enable
 !
!
interface Vlan1
 no ip address
 !
!
interface Vlan10
 description Internal LAN
 ip address {{item.vlan10_ip}} 255.255.255.0
 ip nat inside
 ip virtual-reassembly
 !
!         
no ip http server
no ip http secure-server
!
!
ip nat inside source list NAT interface FastEthernet4 overload
ip route 0.0.0.0 0.0.0.0 {{item.public_gateway}}
!
ip access-list extended INTERNET
 permit icmp any any host {{item.public_ip}}
ip access-list extended NAT
 permit ip {{item.vlan10_network}} 0.0.0.255 any
!
!
!
!
!
!
!
control-plane
!
banner login %

Unauthorized access is prohibited!

%
!
line con 0
 exec-timeout 20 0
 logging synchronous
 no modem enable
line aux 0
 exec-timeout 0 1
 no exec
 transport output none
line vty 0 4
 exec-timeout 20 0
 logging synchronous
 transport input ssh
 transport output ssh
!
ntp source Vlan10
ntp update-calendar
ntp server 1.1.1.1
ntp server 2.2.2.2
end

---------------------------------------------------------------------------------------

omz@DevOps:~/ansible/Cisco$ ansible-playbook site.yml 
 [WARNING]: provided hosts list is empty, only localhost is available

PLAY [Generate router configuration files] *************************************

TASK [setup] *******************************************************************
ok: [localhost]

TASK [router : Generate configuration files] ***********************************
ok: [localhost] => (item={u'timezone_dst': u'PDT', u'dhcp_network': u'10.1.1.0', u'CBAC': True, u'vlan10_ip': u'10.1.1.1', u'timezone_offset': -8, u'hostname': u'twb-sf-rtr1', u'vlan10_network': u'10.1.1.0', u'dhcp_gateway': u'10.1.1.1', u'public_ip': u'6.6.6.6', u'dhcp_netmask': u'255.255.255.0', u'public_gateway': u'6.6.6.1', u'dhcp_exclude1_end': u'10.1.1.99', u'public_netmask': u'255.255.255.0', u'DHCP': True, u'timezone': u'PST', u'dhcp_exclude1_start': u'10.1.1.1', u'secret': u'apassword'})

PLAY RECAP *********************************************************************
localhost                  : ok=2    changed=0    unreachable=0    failed=0   

omz@DevOps:~/ansible/Cisco$
