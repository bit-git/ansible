#Open telnet connection to devices
def open_telnet_conn(ip):
    #Change exception message
    try:
        #Define telnet parameters
        username = 'omz'
        password = 'omz'
        TELNET_PORT = 23
        TELNET_TIMEOUT = 5
        READ_TIMEOUT = 5
        import telnetlib
	import time
        #Logging into device
        connection = telnetlib.Telnet(ip, TELNET_PORT, TELNET_TIMEOUT)
        time.sleep(1)
	connection.write("\n")
        
        output = connection.read_until("name:", READ_TIMEOUT)
        connection.write(username + "\n")
        
        output = connection.read_until("word:", READ_TIMEOUT)
        connection.write(password + "\n")
        time.sleep(1)	
        
        #Setting terminal length for entire output - no pagination
        connection.write("terminal length 0\n")
        time.sleep(1)
        
        #Entering global config mode
        connection.write("\n")
        connection.write("show line\n")
        time.sleep(3)
        
        # #Open user selected file for reading
        # selected_cmd_file = open(cmd_file, 'r')
            
        # #Starting from the beginning of the file
        # selected_cmd_file.seek(0)
        
        # #Writing each line in the file to the device
        # for each_line in selected_cmd_file.readlines():
        #     connection.write(each_line + '\n')
        #     time.sleep(1)
    
        # #Closing the file
        # selected_cmd_file.close()
        
        #Test for reading command output
        output1 = connection.read_very_eager()
        print output1
        
	for line in range(66,70):
            connection.write("clear line {} \n".format(line))
            connection.write("\n")

 	connection.write("show line\n")
        time.sleep(3)

	output2 = connection.read_very_eager()
        print output2


        #Closing the connection
        connection.close()
        
    except IOError:
        print "Input parameter error! Please check username, password and file name."
		
#Calling the Telnet function
ip='10.10.10.5'
open_telnet_conn(ip)
