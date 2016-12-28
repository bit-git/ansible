#!/usr/bin/env python 

import argparse
import sys
import time
import os

HEADER_TMPL = """---
ospf_config:
"""

CISCO_TMPL = """
    - {
        hostname: %s,
        pid: %s, 
        network: %s, wildmask: %s, area: %s,
        rid: %s
     }       
"""
QUAGGA_TMPL = """
    - {
        hostname: %s,
        pid: %s,
        network: %s, wildmask: %s, area: %s,
        rid: %s
     }       
"""

def ospfConfig():
    """ This function is for OSPF config. """

    dict_ospfconfig = {}
    
    count1 = 0
    while True:
        ospfcfg = {}        
        user_input = raw_input("\nThis will generate OSPF configurations\nPress 'c' to continue OR 'q' to quit: ")
        if user_input == 'c':
            
            hostname = raw_input("Hostname: ")
            ospfPID = raw_input("OSPF process id: ")
            ospfRID = raw_input("OSPF router-id: ")            
            
            ospfcfg["hostname"] = hostname
            ospfcfg["pid"] = ospfPID
            ospfcfg["rid"] = ospfRID
            
            raw_input("Advertise networks. Hit Enter to continue... ").lower()
            networks = {}
            
            count2 = 0
            while True:
                nets = {}
                
                network = raw_input("Network (eg. 192.168.1.0): ")
                network_wildmask = raw_input("Network wildcard-mask (eg. 0.0.0.255): ")
                network_area = raw_input("Network area: ")            
                
                nets["network"] = network
                nets["wildmask"] = network_wildmask
                nets["area"] = network_area
                networks[hostname] = nets

                add_more = raw_input("Add more networks (Y/N) ").lower()
                if add_more == 'y':
                    count2 += 1
                    continue                  
                else:
                    break


            dict_ospfconfig[count1] = ospfcfg
            count1 += 1
        

        elif user_input == 'q':
            break
        else:
            print "Input error!"
    

    return dict_ospfconfig, networks


def main():
    
    # parser = argparse.ArgumentParser(description='****Configuration generation.****')
    # parser.add_argument('-c', '--cisco', help='Cisco devices', required=False)
    # parser.add_argument('-j', '--juniper', help='Juniper devices', required=False)
    # parser.add_argument('-l', '--all', help='All.', required=False)
    # args = vars(parser.parse_args())

    parser = argparse.ArgumentParser(description='****Configuration generation.****')
    parser.add_argument('-g', '--generate', help='Cisco Juniper', required=True)
    args = vars(parser.parse_args())
    arg = args['generate'].split(' ')
    
    print "\n*** Disclaimer! Be careful with the format of inputs.\nThere is NO input validation. :) ***\n"

    
    if len(args) == 1 and "cisco" in args['generate']:
        print "cisco"
        
        # Open file to write vars
        vars_file = open("/home/omz/ansible-play/ospf-config/roles/cisco/vars/main.yml", 'w')
   
        config, networks = ospfConfig()
        print config, networks
    
        # Build var file to use with j2 to generate configs
        vars_file.write( HEADER_TMPL )
      
        # networks to adv into ospf  
        for key in config:
            yaml = CISCO_TMPL %  ( config[key]["hostname"],
                                   config[key]["pid"],
                                   config[key]["network"],
                                   config[key]["wildmask"],
                                   config[key]["area"],
                                   config[key]["rid"] )
            vars_file.write(yaml)
        
        # file close
        vars_file.close()

    elif len(args) == 1 and "quagga" in args['generate']:
        print "Quagga"

        vars_file = open("/home/omz/ansible-play/ospf-config/roles/quagga/vars/main.yml", 'w')
   
        config = ospfConfig()
        #print config
    
        # Build var file to use with j2 to generate configs
        vars_file.write( HEADER_TMPL )
      
        # networks to adv into ospf  
        for key in config:
            yaml = QUAGGA_TMPL %  ( config[key]["hostname"],
                                    config[key]["pid"],
                                    config[key]["network"],
                                    config[key]["wildmask"],
                                    config[key]["area"],
                                    config[key]["rid"] )
            vars_file.write(yaml)
    
        # file close
        vars_file.close()
    else:
        print "all"

    #print yaml
     
    os.system("ansible-playbook site.yml")

    #time.sleep(1)
    #os.system("cat /home/omz/ansible-play/ospf-config/CFGS/%s.txt" % (hostname))
   
    
if __name__ == "__main__":
    main()
