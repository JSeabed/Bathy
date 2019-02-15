                            # IP adresses and ports for Ethernet transfers
UDP_IP1 = "10.68.5.91"      
#UDP_IP1 = "172.16.10.50"
UDP_PORT1 = 5001
#UDP_IP2 = "10.68.5.92"      
UDP_IP2 = "172.16.10.50"
UDP_PORT2 = 5001

                            # naming the sockets for UDP communication
sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#////////////////////////////////////// Ethernet write loops   //////////////////////////////////////////

def UDPsender():
    global UDP_IP1                                              #Getting some global variables
    global UDP_PORT1
    global UDP_IP2
    global UDP_PORT2
    
    while True:                                                 # Do forever
        global dataToSend; #print (dataToSend + '\r\n')          # Get the string to sent over UDP and print it to terminal
        sock1.sendto(dataToSend, (UDP_IP1, UDP_PORT1))          # send the string to the first IP address over UDP
        sock2.sendto(dataToSend, (UDP_IP2, UDP_PORT2))          # Send the string to the second IP adress over UDP
        clearAml()                                              # Clear the string to avoid duplicates 
        time.sleep(1)                                           # Wait for a second (minus runtime of the code) and repeat



#Start thread Ethernet UDP
thrUDP = threading.Thread(name='UDPsender', target=UDPsender) # Create a thread for serial communication(thrAML) 
thrUDP.start()                                                      # Start said thread
