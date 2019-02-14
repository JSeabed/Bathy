# Original code by Mehmet Ozturk 
# Modified by Sebastiaan van Essen 07/2016
# This code combines the time precision of the GNSS network and data from ALM sensors
# and sends the data via Ethernet to a computer as a stand alone module.
#

#from _overlapped import NULL
#from test.support import temp_cwd


#/////////////////////////////////  Importing modules for functions later used    ///////////////////////

import os
import sys
import serial
import threading
import datetime
import time
import logging
import socket
import Adafruit_BBIO.GPIO as GPIO
import string



#/////////////////////////////////  Defining variables used for the data splitting    ///////////////////


#                   These variables are for the parsing of the ZDA data

sDay = ''
#sMonth = ''
#sYear = ''
#sHour = ''
#sMinute = ''
#sSecond = ''
#sMSecond = ''
#date = ''
#time = ''

#sDag = ''
sMaand = ''
sJaar = ''
sUur = ''
sMinuut = ''
sSecond = ''
sMSecond = ''
datum = ''
tijd = ''

#                   These variables are for the parsing of the AML data

status = 'st'
dataToSend = '$SBDAML,,,,,,,,ST' + '\r\n'

#                   These variables are used to pull the time from the systemclock and use them for tagging
sDayNow = ''
sMonthNow = ''
sYearNow = ''
#sHourNow = ''
#sMinuteNow = ''
#sSecondNow = ''
#sMSecondNow = ''
dateNow = ''
timeNow = ''
#setTime = ''
dateTime = '' 

#sDagNu = ''
#sMaandNu = ''
#sJaarNu = ''
#sUurNu = ''             isnt being used at all
#datumNu = ''
#tijdNu = ''
setTime = '' 
#datumTijd = ''
#AmlMessage = ''

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



#/////////////////////////////////   Defining triggers for functions    /////////////////////////////////
# trigger is used for the PPS input. ZDA is used to monitor the time that has passed since the requested time(?) [original line: This trigger is to keep track of the "freshness" of the ZDA time info]. 
# AML trigger is to see if there is unsend AML info
bTrigger = False                                            # This trigger is used for the PPS input
bZdaOntvangen = False                                       # This trigger is to keep track of the "freshness" of the ZDA time info
bAmlOntvangen = False                                       # This trigger is to see if there is unsent AML info.


#/////////////////////////////////    Error/debug logging functionality   ///////////////////////////////

#logging.basicConfig(level=logging.DEBUG,
#                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
#                    )


#/////////////////////////////////  GPIO configuration   ////////////////////////////////////////////////

#Configuring the general pins for input/output (GPIO
#GPIO.setmode(GPIO.BCM)                                      
# setup GPIO using Board numbering
GPIO.setup("P9_42", GPIO.IN, pull_up_down=GPIO.PUD_DOWN)          # setting Pin P9_42 as input, also a pull-down resistor is turned on internally


#///////////////////   Serial communication configurations    ///////////////////////////////////////////

#Open Com port of GPZDA (Connected through P9_26)
# Linking serZDA to the correct Com port with the correct baudrate and setting the state of the port to open.
serZda = serial.Serial('/dev/ttyO1')
serZda.baudrate = 19200
serZda.isOpen()


#Open Com port of AML (connected through P9_21 and P9_22)
# Linking serAml to the correct Com port with the correct baudrate and setting the state of the port to open.
serAml = serial.Serial('/dev/ttyO2')                      # Linking serAml to the correct Com port
serAml.baudrate = 38400                                     # Setting the communication speed of the serial port
serAml.isOpen()                                             # Open serial port


def clearAml():
    global status                                           # Requesting access to global variable named status
    global dateNow; dateNow = ''                            # Requesting access to global variable named dateNow, then empty it
    global dataToSend; dataToSend = '$SBDAML,,,,,,,,' + status + '\r\n'     # Requesting access to global variable named datToSend, then put an default empty string in it
    print ('AML cleared\r\n')                               # Show a message (AML cleared) in the terminal that started the program

                        #Pulling the time from the system and write it into a usable variable

def getTime():

    currentDateTimeRaw = datetime.datetime.now() + datetime.timedelta(seconds =1)   # currentDateTime is the current time plus one second 
    currentDateTime = currentDateTimeRaw.strftime('%H:%M:%S.%f,%d,%m,%Y')           # puts the DateTime in a specific format
    currentTime = currentDateTime.split(',')                    # with split() each comma seperated piece of currentDateTime is written in array currentTime.   
        
    global timeNow; timeNow = currentTime[0]                      # Splitting the array into time       
    global sDayNow; sDayNow = currentTime[1]                      # Day
    global sMonthNow; sMonthNow = currentTime[2]                  # Month      
    global sYearNow; sYearNow = currentTime[3]                    # And year     
    global dateNow; dateNow = sDayNow + '-' + sMonthNow + '-' + sYearNow + ',' + timeNow   # The combined data of day+month+year makes the variable dateNow (date)     

#////////////////////////////////////// Serial Write loops  /////////////////////////////////////////////
def writeCom1(textToWrite):                                                 # Serial port 1 ZDA Writer
    serZda.write(textToWrite.encode(encoding='utf_8', errors='strict'))     # Encode data to serial protocol for Com1

def writeCom2(textToWrite):                                                 # Serial poort 2 AML Writer
    serAml.write(textToWrite.encode(encoding='utf_8', errors='strict'))     # Encode data to serial protocol for Com2


#///////////////////////////////// This is what happenes when pin 7 (PPS) goes high   ///////////////////

                        #When pulse() is used this is what happens
def pulse(channel):
    print('trigger' )                                       # Give the terminal that PPS was received
    print (datetime.datetime.now())                         # Print to console the current time
    global bZdaOntvangen                                    # Getting some global variables and stuff
    global dateTime
    global status
    print (bZdaOntvangen)                                   #Print the current value of bZdaOntvangen to the terminal



    if bZdaOntvangen == True:                                   # if ZDAontvangen is true
        bZdaOntvangen = False                                       # ZDAontvangnen is set to false (as we are doing something with the data it's not fresh anymore
        os.system('date -s %s' % dateTime)                         # Sets the system time to dateTime (the time set per ZDA)
        dateTime = False                                           # dateTime is cleared out so when we receive another puls before  ZDA we won't get stuck in the past
        status = "OK"                                               # status is set to ok as all seems ok
    else:                                                       # If ZDAontvangen was false 
        status = 'NZ'                                               # Status is set to NZ (no Zda) 
        bZdaOntvangen = False                                       # Zda ontvangen is set to False (just to be sure)

    
                        #This is the detector that sees the pin goes high then starts the function pulse
GPIO.add_event_detect("P9_42", GPIO.RISING, callback=pulse, bouncetime = 300)  # When the triggerpin goes high start function pulse()

#////////////////////////////////////// Ethernet write loops   //////////////////////////////////////////
def UDPsender():
    global UDP_IP1                                              #Getting some global variables
    global UDP_PORT1
    global UDP_IP2
    global UDP_PORT2
    
    while True:                                                 # Do forever
        
       # print('Send over Ethernet')                             # send to console that data is being sent over ethernet                    
        global dataToSend; print (dataToSend + '\r\n')          # Get the string to sent over UDP and print it to terminal
        sock1.sendto(dataToSend, (UDP_IP1, UDP_PORT1))          # send the string to the first IP address over UDP
        sock2.sendto(dataToSend, (UDP_IP2, UDP_PORT2))          # Send the string to the second IP adress over UDP
        clearAml()                                              # Clear the string to avoid duplicates 
        time.sleep(1)                                           # Wait for a second (minus runtime of the code) and repeat


#//////////////////////////////////// Serial loop    ////////////////////////////////////////////////////
#Start thread Ethernet UDP
thrUDP = threading.Thread(name='UDPsender', target=UDPsender) # Create a thread for serial communication(thrAML) 
thrUDP.start()                                                      # Start said thread

#Start thread serial 1 ZDA Reader
thrZda = threading.Thread(name='serZdaReader', target=serZdaReader) # Create a thread for serial communication(thrZDA) 
thrZda.start()                                                      # Start said thread

#Start thread serial 2 AML Reader
thrAml = threading.Thread(name='serAmlReader', target=serAmlReader) # Create a thread for serial communication(thrAML) 
thrAml.start()                                                      # Start said thread
