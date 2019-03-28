# Original code by Mehmet Ozturk 
# Modified by Sebastiaan van Essen 07/2016
# This code combines the time precision of the GNSS network and data from ALM sensors
# and sends the data via Ethernet to a computer as a stand alone module.

import os
import sys
import serial
import threading
import datetime
import time
import socket
import Adafruit_BBIO.GPIO as GPIO
#import pulsegpio

import aml
import zda

#import gpio

date = ''
status = ',st'
dataToSend = '$SBDAML,,,,,,,,ST' + '\r\n'
timeNow = ''
dateTime = '' 
setTime = '' 
GPIO.setup("P9_42", GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


#/////////////////////////////////   Defining triggers for functions    /////////////////////////////////
# trigger is used for the PPS input. ZDA is used to monitor the time that has passed since the requested time(?)
# [original line: This trigger is to keep track of the "freshness" of the ZDA time info]
# AML trigger is to see if there is unsend AML info
bZdaOntvangen = False
bAmlOntvangen = False

# Open Com port of GPZDA (Connected through P9_26)
# Linking serZDA to the correct Com port with the correct baudrate and setting the state of the port to open.
serZda = serial.Serial('/dev/ttyO1')
serZda.baudrate = 19200
serZda.isOpen()

# Open Com port of AML (connected through P9_21 and P9_22)
# Linking serAml to the correct Com port with the correct baudrate and setting the state of the port to open.
serAml = serial.Serial('/dev/ttyO2')
serAml.baudrate = 38400
serAml.isOpen()

#///////////////////////////////// This is what happenes when pin 7 (PPS) goes high   ///////////////////
#this function needs to be triggered by the gpio pins so that it can synchronise the time of the beaglebone with the receiver. the pps pulse is connected to gpio P9_42.
#the pulse function is only called when there is an analog pulse detected on designated pin. the only information that this function requeres to opperate is the time that was send over the ZDA string.
def pulse(channel):
    #bZdaOntvangen = zda.serZdaReader()
    #print bZdaOntvangen
    serSV = serial.Serial('/dev/ttyO5')
    serSV.baudrate = 19200
    serSV.isOpen() 
    testcode = ("test  serial send over new pin") + '\r\n'
    serSV.write("134679")
    serSV.write(testcode.encode('utf_8'))
    serSV.close()
    
    print "pulse start"
    print datetime.datetime.now()
    #dateTime = zda.serZdaReader()
    print dateTime
            # If there is no usable data print "dateTime is none"
    if dateTime is None:
            # print('dateTime is none:')
        bZdaOntvangen = False
            # Change the status to IZ (Invalid ZDA)
        status = ",IZ"
        # If the data is usable 
    else:
        os.system('date -s %s' % dateTime)
        status = ",OK"
    # Checking if the data has been received and setting the system time to the received date.
    # After setting the time the statement gets reset to False for checking in the next cycle. status is also 
    print status
    return


#////////////////////////////////////// Ethernet write loops   //////////////////////////////////////////
def UDPsender():
    # IP adresses and ports for Ethernet transfers
    UDP_IP1 = "10.68.5.91"
    # UDP_IP1 = "172.16.10.50"
    UDP_PORT1 = 5001
    # UDP_IP2 = "10.68.5.92"
    UDP_IP2 = "172.16.10.50"
    UDP_PORT2 = 5001

    sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        dataToSend_raw = aml.serAmlReader()
        dataToSend = dataToSend_raw + '\r\n'
        # send the string to the first IP address over UDP
        sock1.sendto(dataToSend, (UDP_IP1, UDP_PORT1))

        # Send the string to the second IP adress over UDP
        sock2.sendto(dataToSend, (UDP_IP2, UDP_PORT2))

        timeAml = aml.getTime()
        time.sleep(0.5)

GPIO.add_event_detect("P9_42", GPIO.RISING, callback=pulse, bouncetime = 300)
print('gpio initialised')
# Start thread Ethernet UDP
thrUDP = threading.Thread(name='UDPsender', target=UDPsender) # Create a thread for serial communication(thrAML) 
thrUDP.start()

# Start thread serial 1 ZDA Reader
thrZda = threading.Thread(name='serZdaReader', target=zda.serZdaReader) # Create a thread for serial communication(thrZDA) 
thrZda.start()

# Start thread serial 2 AML Reader
thrAml = threading.Thread(name='serAmlReader', target=aml.serAmlReader) # Create a thread for serial communication(thrAML) 
thrAml.start()
