#!/usr/bin/env python 

import argparse
import sys
import time
import os
from jinja2 import Environment, FileSystemLoader, Template
import yaml

BASIC_TMPL = """---
basic_tmpl:
   hostname: %s
   ospf_PID: %s
   ospf_RID: %s

loopback_int:
"""
LOOPBACK_TMPL = "   - { num: %s, address: %s, mask: %s }\n"

NET_TMPL = "   - { network: %s, wildmask: %s, area: %s }\n"""


def ospfConfig():
    """ This function asks the user to insert information about loopback interfaces. """
    
    print "\n*** OSPF Configuration ***"
    dict_ospf = {}
    
    ospfPID = raw_input("Insert OSPF process id: ")
    ospfRID = raw_input("Insert OSPF router-id: ")

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
    return (dict_ospf, ospfPID, ospfRID)


def networks():
    """ Get OSPF networks to advertise. """
    
    print "\n*** OSPF NETWORKS ***\nnetworks to advertise into OSPF."
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


def hostName():
    hostname = raw_input("Enter hostname : ")
    if hostname is not 'q':
        return hostname
    elif hostname == 'q':
        sys.exit(1)



def main():
   
    # Open file to write vars
    
    
    print "\n*** Disclaimer! Be careful with the format of inputs.\nThere is NO input validation. :) ***\n"   
    numHosts = input('Enter the total number of devices to configure: ' )
    while numHosts != 0:
        vars_file = open("/home/omz/ansible-play/ospf-config/roles/cisco/vars/main.yml", 'w')
        
        hostname = hostName()
        ospf, ospfPID, ospfRID = ospfConfig()
        nets = networks()
        numHosts -= 1

        # Build .tmpl vat file to sue with j2 to generate configs
        basic_vars = BASIC_TMPL % (hostname, ospfPID, ospfRID)
        
        vars_file.write(basic_vars)
            
        for interface in ospf:
            intYml = LOOPBACK_TMPL % (interface, ospf[interface]["address"], ospf[interface]["mask"])
            vars_file.write(intYml)
           
        vars_file.write("\nnetworks:\n")
          
        # networks to adv into ospf    
        for net in nets:
            netYml = NET_TMPL %  (nets[net]["network"], nets[net]["wildmask"], nets[net]["area"])
            vars_file.write(netYml)
        # file close
        vars_file.close()


        with open("/home/omz/ansible-play/ospf-config/roles/cisco/vars/main.yml", "r") as var:
            yml = yaml.load(var)
   
        templateLoader = FileSystemLoader("/home/omz/ansible-play/ospf-config/roles/cisco/templates/")
        templateEnv = Environment(loader = templateLoader, trim_blocks=True)
        template = templateEnv.get_template("cisco_ospf.j2")
        output = template.render(yml=yml)
        
        #print output

        config_file = open("/home/omz/ansible-play/ospf-config/CFGS/{}.txt".format(hostname), "w")
        config_file.write(output)
        config_file.close()       













        #print "../vars/main.yml generating..."
        #time.sleep(2)
        #print "../vars/main.yml generated!"
        # Generating the configs.
        #print "Generating ospf configs snippet in ../CFGS foler...\n"
    #time.sleep(2)
    os.system("ansible-playbook site.yml")
    #time.sleep(2)
    #print "*** Config snippet ***"
    #os.system("cat /home/omz/ansible-play/ospf-config/CFGS/%s.txt" % (hostname))
   
    
if __name__ == "__main__":
    main()
