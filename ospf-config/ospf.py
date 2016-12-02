#!/usr/bin/env python 

import argparse
import sys
import time
import os


BASIC_TMPL = """---
basic_tmpl:
   - { hostname: %s, ospf_PID: %s }

loopback_int:
"""
LOOPBACK_TMPL = "   - { num: %s, address: %s, mask: %s }\n"

NET_TMPL = "   - { network: %s, wildmask: %s, area: %s }\n"""


def loopbackInt():
    """ This function asks the user to insert information about loopback interfaces. """
    
    print "\n*** OSPF Configuration ***"
    dict_ospf = {}
    
    ospfPID = raw_input("Insert OSPF process id: ")
    
    while True:
        ospf_loopback = {}

        loopback_name = raw_input("\nProvide loopback interface number (eg. 0)\nor (Press 'q' to quit): ")
        if loopback_name is not 'q':
            ospf_loopback["address"] = raw_input("Loopback IP (eg. 1.1.1.1): ")
            ospf_loopback["mask"] = raw_input("Loopback mask (eg. 255.255.255.0): ")
            
            dict_ospf[loopback_name] = ospf_loopback        
        elif loopback_name == 'q':
            break
        else:
            print "Input error!"
    return (dict_ospf, ospfPID)


def Networks():
    """ This function asks the user to insert information about BGP neighbors. """
    
    print "\n*** OSPF NETWORKS ***\nNetworks to advertise into OSPF."
    dict_networks = {}
    count = 0
    while True:
        ospf_nets = {}        
        count += 1
        userInput = raw_input("\nHit Enter to add networks. Press 'q' to quit: ")
        if userInput is not 'q':
            network = raw_input("Network or IP address (eg. 172.16.1.0): ")
            network_wildmask = raw_input("Network wildcard-mask (eg. 0.0.0.255): ")
            network_area = raw_input("Network area: ")

            ospf_nets["network"] = network
            ospf_nets["wildmask"] = network_wildmask
            ospf_nets["area"] = network_area
            
            dict_networks[count] = ospf_nets
        elif userInput == 'q':
            break
        else:
            print "Input error!"
    return dict_networks

def help():
    """This creates a nice and userfriendly command line."""
    parser = argparse.ArgumentParser(description="OSPF Single Area Config Generation!")
    
    parser.add_argument('-f', '--filename', dest='filename',
            help='text file containing the node data (expected format...)')
    return parser.parse_args()

def main(args):
   
    # Open file to write vars
    vars_file = open("/home/omz/ansible-play/ospf-config/roles/router/vars/main.yml", 'w')
    
    print "\n*** Disclaimer! Be careful with the format of inputs.\nThere is NO input validation. :) ***\n"   
    hostname = raw_input("Enter hostname : ")
    ospf, ospfPID = loopbackInt()
    
    # Networks to adv into ospf
    networks = Networks()
    
    # Build .tmpl vat file to sue with j2 to generate configs
    basic_vars = BASIC_TMPL % (hostname, ospfPID)
    vars_file.write(basic_vars)

    for interface in ospf:
        intYml = LOOPBACK_TMPL % (interface, ospf[interface]["address"], ospf[interface]["mask"])
        vars_file.write(intYml)

    vars_file.write("\nnetworks:\n")

    for net in networks:
        netYml = NET_TMPL %  (networks[net]["network"], networks[net]["wildmask"], networks[net]["area"])
        vars_file.write(netYml)

    # file close
    vars_file.close()
    print "../vars/main.yml generating..."
    time.sleep(2)
    print "../vars/main.yml generated!"

    # Generating the configs.
    print "Generating ospf configs snippet in ../CFGS foler...\n"
    time.sleep(2)
    os.system("ansible-playbook site.yml")
    #time.sleep(2)
    print "*** Config snippet ***"
    os.system("cat /home/omz/ansible-play/ospf-config/CFGS/%s.txt" % (hostname))
    
if __name__ == "__main__":
    sys.exit(main(help()))
