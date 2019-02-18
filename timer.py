# Original code by Mehmet Ozturk 
# Modified by Sebastiaan van Essen 07/2016
# This code combines the time precision of the GNSS network and data from ALM sensors
# and sends the data via Ethernet to a computer as a stand alone module.
#from _overlapped import NULL
#from test.support import temp_cwd

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
date = ''
status = ',st'
dataToSend = '$SBDAML,,,,,,,,ST' + '\r\n'
dateNow = ''
timeNow = ''
dateTime = '' 
setTime = '' 

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
# trigger is used for the PPS input. ZDA is used to monitor the time that has passed since the requested time(?) [original line: This trigger is to keep track of the "freshness" of the ZDA time info]

# AML trigger is to see if there is unsend AML info
bTrigger = False
bZdaOntvangen = False
bAmlOntvangen = False

#/////////////////////////////////  GPIO configuration   ////////////////////////////////////////////////
#Configuring the general pins for input/output (GPIO)
# setting Pin P9_42 as input, also a pull-down resistor is turned on internally
GPIO.setup("P9_42", GPIO.IN, pull_up_down=GPIO.PUD_DOWN)



#Open Com port of GPZDA (Connected through P9_26)
# Linking serZDA to the correct Com port with the correct baudrate and setting the state of the port to open.
serZda = serial.Serial('/dev/ttyO1')
serZda.baudrate = 19200
serZda.isOpen()

#Open Com port of AML (connected through P9_21 and P9_22)
# Linking serAml to the correct Com port with the correct baudrate and setting the state of the port to open.
serAml = serial.Serial('/dev/ttyO2')
serAml.baudrate = 38400
serAml.isOpen()

#/////////////////////////////////  Processing the incoming data by splitting it and putting it in usable variables  //////////
#Clearing data from AML
def clearAml():
    global status                                           # Requesting access to global variable named status
    global dateNow; dateNow = ''                            # Requesting access to global variable named dateNow, then empty it
   # global dataToSend; dataToSend = '$SBDAML,,,,,,,,' + status + '\r\n'     # Requesting access to global variable named datToSend, then put an default empty string in it
                        #Pulling the time from the system and write it into a usable variable


def getTime():
    currentDateTimeRaw = datetime.datetime.now() + datetime.timedelta(seconds =1)   # currentDateTime is the current time plus one second 
    currentDateTime = currentDateTimeRaw.strftime('%H:%M:%S.%f,%d,%m,%Y')           # puts the DateTime in a specific format
    currentTime = currentDateTime.split(',')                    # with split() each comma seperated piece of currentDateTime is written in array currentTime.   

    timeNow = currentTime[0]
    sDayNow = currentTime[1]
    sMonthNow = currentTime[2]
    sYearNow = currentTime[3]
    global dateNow; dateNow = sDayNow + '-' + sMonthNow + '-' + sYearNow + ',' + timeNow   # The combined data of day+month+year makes the variable dateNow (date)     


#Splitting the ZDA data into 8 variables, then process it to time and date
def parseZda(raw_message):
    global bZdaOntvangen
    global status

    if raw_message is None:                                 # if no data is sent stop the madness
        return None

    try:
        sLines = raw_message.split(',')                     # with split() each comma seperated piece of raw_message is written in array sLines.   
        if len(sLines) < 7:                                 # if the data contains less then 7 blocks
            return None
        if len(sLines[1]) < 9:
            return None

        realTime = zdaParseTime(sLines[1])

        if len(sLines[2]) < 2 or len(sLines[3]) < 2 or len(sLines[4]) < 2:      # if string 2, 3 or 4 is longer then 2 digits stop the data
            return None

        date = zdaParseDate(sLines)

        global dateTime; dateTime = "'" + date + ' ' + realTime +"'"

        return ' ZDA OK' + ' >> ' + dateTime           # Send confirmation + data (ZDA OK >> parsed data ) to console and Com1

    except Exception as e:
        print ('Exception: ' + str(e))


def zdaParseTime(tempTime):
        sHour = tempTime[:2]
        sMinute = tempTime[2:4]
        sSecond = tempTime[4:6]
        sMSecond = tempTime[7:]
        #Time in format HH:MM:SS
        return sHour + ':' + sMinute + ':' + sSecond + '.' + sMSecond

def zdaParseDate(sLines):
        #in order: year, month date
        return sLines[4] + '-' + sLines[3] + '-' + sLines[2]



# Splitting the AML Data into variables and combining with time
def parseAml (raw_mess):
    global UDP_IP1                                              #Getting some global variables
    global UDP_PORT1
    global UDP_IP2
    global UDP_PORT2   
    global sLineAml; sLineAml = raw_mess.split('  ')        # with split() each space seperated piece of raw_mess is written in array sLinesAml. 
    if len(sLineAml) < 4:                                   # if the data is shorter then 5 blocks of data run next line
        sock1.sendto(raw_mess + '\r\n', (UDP_IP1, UDP_PORT1))
        sock2.sendto(raw_mess + '\r\n', (UDP_IP2, UDP_PORT2))
    getTime()
    global dataToSend#; dataToSend = '$SBDAML,,,,,,,,' + status + '\r\n'
    global status

    #i = 1
    #LinesToSend = ""
    dataToSend = '$SBDAML' + ',' + dateNow
    LinesToSend = ','.join(sLineAml[1:])
    dataToSend = dataToSend + LinesToSend + status + '\r\n'
    return dataToSend

#/////////////////////////////////   Serial receive loops   /////////////////////////////////////////////
def serZdaReader():
    while True:
        bLine = serZda.readline()
        try:
            sLine = bLine.decode(encoding='utf_8')          # decode it into usable data
        except:
            sLine = "0"
            pass                                            # don't do anything

        global bZdaOntvangen                                # Requesting access to global variable named bZdaOntvangen
        global status                                       # Requesting access to global variable named status
        dateTime = parseZda(sLine)                         # parse the raw data string into usable variables

        if dateTime is None:                               # if there is no usable data print "dateTime is none"
            print('dateTime is none:')
            bZdaOntvangen = False                           # Boolean bZdaOntvangen is set to False
            status = ",IZ"                                   # Change the status to IZ (Invalid ZDA)
        else:                                               # If the data is usable 
                bZdaOntvangen = True
                #Serial AML (Com2)
def serAmlReader():
    while True:
        b1Line = serAml.readline()                          # read the line from serial ALM and write it to blLine
        s1Line = b1Line.decode(encoding='utf_8')            # Decode the data from serial ALM to usable data
        s1Line = s1Line.rstrip(' ' +'\r\n')
        isAmlValid = parseAml(s1Line)                       # turn the raw data into usable data blocks
        global bZdaOntvangen


#////////////////////////////////////// Serial Write loops  /////////////////////////////////////////////
def writeCom1(textToWrite):                                                 # Serial port 1 ZDA Writer
    serZda.write(textToWrite.encode(encoding='utf_8', errors='strict'))     # Encode data to serial protocol for Com1

def writeCom2(textToWrite):                                                 # Serial poort 2 AML Writer
    serAml.write(textToWrite.encode(encoding='utf_8', errors='strict'))     # Encode data to serial protocol for Com2


#///////////////////////////////// This is what happenes when pin 7 (PPS) goes high   ///////////////////
def pulse(channel):
    global bZdaOntvangen
    global dateTime
    global status

#checking if the data has been received and setting the system time to the received date. after setting the time the statement gets reset to False for checking in the next cycle. status is also 
    if bZdaOntvangen is True:
        os.system('date -s %s' % dateTime)                         # Sets the system time to dateTime (the time set per ZDA)
        #dateTime = False                                           # dateTime is cleared out so when we receive another puls before  ZDA we won't get stuck in the past
        status = ",OK"                                               # status is set to ok as all seems ok
       # bZdaOntvangen = False
    else:
        status = ',NZ'
        bZdaOntvangen = False
                        #This is the detector that sees the pin goes high then starts the function pulse
GPIO.add_event_detect("P9_42", GPIO.RISING, callback=pulse, bouncetime = 300)  # When the triggerpin goes high start function pulse()


#////////////////////////////////////// Ethernet write loops   //////////////////////////////////////////
def UDPsender():
    global UDP_IP1
    global UDP_PORT1
    global UDP_IP2
    global UDP_PORT2

    while True:
        global dataToSend
        sock1.sendto(dataToSend, (UDP_IP1, UDP_PORT1))          # send the string to the first IP address over UDP
        sock2.sendto(dataToSend, (UDP_IP2, UDP_PORT2))          # Send the string to the second IP adress over UDP
        clearAml()                                              # Clear the string to avoid duplicates 
        time.sleep(0.5)


#Start thread Ethernet UDP
thrUDP = threading.Thread(name='UDPsender', target=UDPsender) # Create a thread for serial communication(thrAML) 
thrUDP.start()

#Start thread serial 1 ZDA Reader
thrZda = threading.Thread(name='serZdaReader', target=serZdaReader) # Create a thread for serial communication(thrZDA) 
thrZda.start()

#Start thread serial 2 AML Reader
thrAml = threading.Thread(name='serAmlReader', target=serAmlReader) # Create a thread for serial communication(thrAML) 
thrAml.start()
