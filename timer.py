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

#sDay = ''
#sMonth = ''
#sYear = ''
#sHour = ''
#sMinute = ''
#sSecond = ''
#sMSecond = ''
#date = ''
#time = ''

sDag = ''
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
#sDayNow = ''
#sMonthNow = ''
#sYearNow = ''
#sHourNow = ''
#sMinuteNow = ''
#sSecondNow = ''
#sMSecondNow = ''
#dateNow = ''
#timeNow = ''
#setTime = ''
#dateTime = '' 

sDagNu = ''
sMaandNu = ''
sJaarNu = ''
sUurNu = ''
sMinuutNu = ''
sSecondNu = ''
sMSecondNu = ''
datumNu = ''
tijdNu = ''
setTime = ''
datumTijd = ''
#AmlMessage = ''

                            # IP adresses and ports for Ethernet transfers

#UDP_IP1 = "10.68.5.91"      
UDP_IP1 = "172.16.10.101"
UDP_PORT1 = 5001
#UDP_IP2 = "10.68.5.92"      
UDP_IP2 = "172.16.10.102"
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




#/////////////////////////////////  Processing the incoming data by splitting it and putting it in usable variables  //////////



                        #Clearing data from AML

def clearAml():
    global status                                           # Requesting access to global variable named status
    global datumNu; datumNu = ''                            # Requesting access to global variable named datumNu, then empty it
    global dataToSend; dataToSend = '$SBDAML,,,,,,,,' + status + '\r\n'     # Requesting access to global variable named datToSend, then put an default empty string in it
    print ('AML cleared\r\n')                               # Show a message (AML cleared) in the terminal that started the program

                        #Pulling the time from the system and write it into a usable variable

def getTime():

    currentDateTimeRaw = datetime.datetime.now() + datetime.timedelta(seconds =1)   # currentDateTime is the current time plus one second 
    currentDateTime = currentDateTimeRaw.strftime('%H:%M:%S.%f,%d,%m,%Y')           # puts the DateTime in a specific format
    currentTime = currentDateTime.split(',')                    # with split() each comma seperated piece of currentDateTime is written in array currentTime.   
        
    global tijdNu; tijdNu = currentTime[0]                      # Splitting the array into time       
    global sDagNu; sDagNu = currentTime[1]                      # Day
    global sMaandNu; sMaandNu = currentTime[2]                  # Month      
    global sJaarNu; sJaarNu = currentTime[3]                    # And year     
    global datumNu; datumNu = sDagNu + '-' + sMaandNu + '-' + sJaarNu + ',' + tijdNu   # The combined data of day+month+year makes the variable datumNu (date)     




                        #Splitting the ZDA data into 8 variables, then process it to time and date

def parseZda(raw_message):
    global bZdaOntvangen                                    # Requesting access to global variable named bZdaOntvangen
    global status                                           # Requesting access to global variable named status
    
    if raw_message is None:                                 # if no data is sent stop the madness
        return None
        bZdaOntvangen = False
        status = "IZ"
            
    try:
        sLines = raw_message.split(',')                     # with split() each comma seperated piece of raw_message is written in array sLines.   
        if len(sLines) < 7:                                 # if the data contains less then 7 blocks
            return None
        if len(sLines[1]) < 9:                              # or more then 9
            return None                                     # do nothing
        
        tempTijd = sLines[1]                                # tempTijd is the 2nd string of data from array sLines 
        global sUur; sUur = tempTijd[:2]                    # the first two digits are the hours
        global sMinuut; sMinuut = tempTijd[2:4]             # digits 3 and 4 are minutes  
        global sSecond; sSecond = tempTijd[4:6]             # digits 5 and 6 are seconds  
        global sMSecond; sMSecond = tempTijd[7:]            # all digits from 7 and up are milliseconds    
        global tijd; tijd = sUur + ':' + sMinuut + ':' + sSecond + '.' + sMSecond    #Time in format HH:MM:SS        
        
        if len(sLines[2]) < 2 or len(sLines[3]) < 2 or len(sLines[4]) < 2:      # if string 2, 3 or 4 is longer then 2 digits stop the data
            return None
        global sDag; sDag = sLines[2]                           # the 3th string of sLines is the day
        global sMaand; sMaand = sLines[3]                       # the 4th string of sLines is the month      
        global sJaar; sJaar = sLines[4]                         # the 3th string of sLines is the year     
        global datum; datum = sJaar + '-' + sMaand + '-' + sDag # The combined data of day+month+year makes the variable datum (date)     
#        return ' ZDA OK' + ' >> ' +datum + ' ' + tijd           # Send confirmation + data (ZDA OK >> parsed data ) to console and Com1
        global datumTijd; datumTijd = "'" + datum + ' ' + tijd +"'" # The combined data of day+month+year makes the variable datumNu (date)
#        print (datumTijd)
#        status = "00"
        return ' ZDA OK' + ' >> ' + datumTijd           # Send confirmation + data (ZDA OK >> parsed data ) to console and Com1

    except Exception as e:                                      # if something goes wrong print the error to console      
        print ('Exception: ' + e)


                        # Splitting the AML Data into variables and combining with time

def parseAml (raw_mess):
    global AmlMessage
    global UDP_IP1                                              #Getting some global variables
    global UDP_PORT1
    global UDP_IP2
    global UDP_PORT2   
    global sLineAml; sLineAml = raw_mess.split('  ')        # with split() each space seperated piece of raw_mess is written in array sLinesAml. 
    #print sLineAml
    if len(sLineAml) < 4:                                   # if the data is shorter then 5 blocks of data run next line
        print('something weird')                                     #not normal AML sensor info so forwarding to designated IP adress
        sock1.sendto(raw_mess + '\r\n', (UDP_IP1, UDP_PORT1))          # send the string to the first IP address over UDP
        sock2.sendto(raw_mess + '\r\n', (UDP_IP2, UDP_PORT2)) 
    getTime()                                               # Get the current system time and put it in datumNu
    global dataToSend                                       # make dataToSend (variable) usable in this function
    global status                                           # Do the same as above, but for status

                        # This bit customises the string to the amount of data blocks received from the AML

    if len(sLineAml) == 4:                                  # if the data is 3 blocks of data run next line    
        dataToSend = '$SBDAML' + ',1' + datumNu + ',2' + sLineAml[1] + ',3' + sLineAml[2] + ',4' + sLineAml[3] + ',5' + status + '\r\n'    # Create a string of data   

    elif len(sLineAml) == 5:                                # if the data is 4 blocks of data run next line    
        dataToSend = '$SBDAML' + ',1' + datumNu + ',2' + sLineAml[1] + ',3' + sLineAml[2] + ',4' + sLineAml[3] + ',5' + sLineAml[4] + ',6' + status + '\r\n'  

    elif len(sLineAml) == 6:                                # if the data is 5 blocks of data run next line
        dataToSend = '$SBDAML' + ',1' + datumNu + ',2' + sLineAml[1] + ',3' + sLineAml[2] + ',4' + sLineAml[3] + ',5' + sLineAml[4] + ',6' + sLineAml[5] + ',7' + status + '\r\n'  

    elif len(sLineAml) == 7:                                # if the data is 6 blocks of data run next line
        dataToSend = '$SBDAML' + ',1' + datumNu + ',2' + sLineAml[1] + ',3' + sLineAml[2] + ',4' + sLineAml[3] + ',5' + sLineAml[4] + ',6' + sLineAml[5] + ',7' + sLineAml[6] + ',8' + status + '\r\n'  

    elif len(sLineAml) == 8:                                # if the data is 7 blocks of data run next line
        dataToSend = '$SBDAML' + ',1' + datumNu + ',2' + sLineAml[1] + ',3' + sLineAml[2] + ',4' + sLineAml[3] + ',5' + sLineAml[4] + ',6' + sLineAml[5] + ',7' + sLineAml[6] + ',8' + sLineAml[7] + ',9' + status + '\r\n'

    elif len(sLineAml) == 9:                                # if the data is 8 blocks of data run next line 
        dataToSend = '$SBDAML' + ',1' + datumNu + ',2' + sLineAml[1] + ',3' + sLineAml[2] + ',4' + sLineAml[3] + ',5' + sLineAml[4] + ',6' + sLineAml[5] + ',7' + sLineAml[6] + ',8' + sLineAml[7] + ',9' + sLineAml[8] + ',10' + status + '\r\n'   

    elif len(sLineAml) == 10:                               # if the data is 9 blocks of data run next line       
        dataToSend = '$SBDAML' + ',1' + datumNu + ',2' + sLineAml[1] + ',3' + sLineAml[2] + ',4' + sLineAml[3] + ',5' + sLineAml[4] + ',6' + sLineAml[5] + ',7' + sLineAml[6] + ',8' + sLineAml[7] + ',9' + sLineAml[8] + ',10' + sLineAml[9] + ',11' + status+ '\r\n'    

    elif len(sLineAml) == 11:                               # if the data is 10 blocks of data run next line        
        dataToSend = '$SBDAML' + ',1' + datumNu + ',2' + sLineAml[1] + ',3' + sLineAml[2] + ',4' + sLineAml[3] + ',5' + sLineAml[4] + ',6' + sLineAml[5] + ',7' + sLineAml[6] + ',8' + sLineAml[7] + ',9' + sLineAml[8] + ',10' + sLineAml[9] + ',11' + sLineAml[10] + ',12' + status + '\r\n'   

    elif len(sLineAml) == 12:                               # if the data is 11 blocks of data run next line        
        dataToSend = '$SBDAML' + ',1' + datumNu + ',2' + sLineAml[1] + ',3' + sLineAml[2] + ',4' + sLineAml[3] + ',5' + sLineAml[4] + ',6' + sLineAml[5] + ',7' + sLineAml[6] + ',8' + sLineAml[7] + ',9' + sLineAml[8] + ',10' + sLineAml[9] + ',11' + sLineAml[10] + ',12' + sLineAml[11] + ',13' + status + '\r\n'    

    elif len(sLineAml) == 13:                               # if the data is 12 blocks of data run next line        
        dataToSend = '$SBDAML' + ',1' + datumNu + ',2' + sLineAml[1] + ',3' + sLineAml[2] + ',4' + sLineAml[3] + ',5' + sLineAml[4] + ',6' + sLineAml[5] + ',7' + sLineAml[6] + ',8' + sLineAml[7] + ',9' + sLineAml[8] + ',10' + sLineAml[9] + ',11' + sLineAml[10] + ',12' + sLineAml[11] + ',13' + sLineAml[12]+ ',14' + status + '\r\n'   

    elif len(sLineAml) == 14:                               # if the data is 13 blocks of data run next line        
        dataToSend = '$SBDAML' + ',1' + datumNu + ',2' + sLineAml[1] + ',3' + sLineAml[2] + ',4' + sLineAml[3] + ',5' + sLineAml[4] + ',6' + sLineAml[5] + ',7' + sLineAml[6] + ',8' + sLineAml[7] + ',9' + sLineAml[8] + ',10' + sLineAml[9] + ',11' + sLineAml[10] + ',12' + sLineAml[11] + ',13' + sLineAml[12]+ ',14' + sLineAml[13] + ',15' + status + '\r\n'   

    elif len(sLineAml) == 15:                               # if the data is 14 blocks of data run next line       
        dataToSend = '$SBDAML' + ',1' + datumNu + ',2' + sLineAml[1] + ',3' + sLineAml[2] + ',4' + sLineAml[3] + ',5' + sLineAml[4] + ',6' + sLineAml[5] + ',7' + sLineAml[6] + ',8' + sLineAml[7] + ',9' + sLineAml[8] + ',10' + sLineAml[9] + ',11' + sLineAml[10] + ',12' + sLineAml[11] + ',13' + sLineAml[12]+ ',14' + sLineAml[13] + ',15' + sLineAml[14]+ ',16' + status + '\r\n'   

    elif len(sLineAml) == 16:                               # if the data is 15 blocks of data run next line       
        dataToSend = '$SBDAML' + ',1' + datumNu + ',2' + sLineAml[1] + ',3' + sLineAml[2] + ',4' + sLineAml[3] + ',5' + sLineAml[4] + ',6' + sLineAml[5] + ',7' + sLineAml[6] + ',8' + sLineAml[7] + ',9' + sLineAml[8] + ',10' + sLineAml[9] + ',11' + sLineAml[10] + ',12' + sLineAml[11] + ',13' + sLineAml[12]+ ',14' + sLineAml[13] + ',15' + sLineAml[14]+ ',16' + sLineAml[15]+ ',17' + status + '\r\n'   

    elif len(sLineAml) == 17:                               # if the data is 16 blocks of data run next line       
        dataToSend = '$SBDAML' + ',1' + datumNu + ',2' + sLineAml[1] + ',3' + sLineAml[2] + ',4' + sLineAml[3] + ',5' + sLineAml[4] + ',6' + sLineAml[5] + ',7' + sLineAml[6] + ',8' + sLineAml[7] + ',9' + sLineAml[8] + ',10' + sLineAml[9] + ',11' + sLineAml[10] + ',12' + sLineAml[11] + ',13' + sLineAml[12]+ ',14' + sLineAml[13] + ',15' + sLineAml[14]+ ',16' + sLineAml[15]+ ',17' + sLineAml[16]+ ',18' + status + '\r\n'   

    elif len(sLineAml) == 18:                               # if the data is 17 blocks of data run next line        
        dataToSend = '$SBDAML' + ',1' + datumNu + ',2' + sLineAml[1] + ',3' + sLineAml[2] + ',4' + sLineAml[3] + ',5' + sLineAml[4] + ',6' + sLineAml[5] + ',7' + sLineAml[6] + ',8' + sLineAml[7] + ',9' + sLineAml[8] + ',10' + sLineAml[9] + ',11' + sLineAml[10] + ',12' + sLineAml[11] + ',13' + sLineAml[12]+ ',14' + sLineAml[13] + ',15' + sLineAml[14]+ ',16' + sLineAml[15]+ ',17' + sLineAml[16]+ ',18' + sLineAml[17]+ ',19' + status + '\r\n'   
        
    status = "NC"
    del sLineAml                                            # Clearing out the data from sLineAml so no old data is processed the next time
    return ' ALM OK'+' >> '+ dataToSend                     # Send confirmation + data (AML OK >> parsed data ) to console


#/////////////////////////////////   Serial receive loops   /////////////////////////////////////////////


                                #Serial ZDA (Com1)
    
def serZdaReader():
     
    while True:                                             # Run forever
        bLine = serZda.readline()                           # Read the incoming data from serial ZDA and put it in bLine
        try:                                                # if possible do
            sLine = bLine.decode(encoding='utf_8')          # decode it into usable data      

        except:                                             # if not possible
            pass                                            # don't do anything

        pass
        global bZdaOntvangen                                # Requesting access to global variable named bZdaOntvangen
        global status                                       # Requesting access to global variable named status
        print (' COM1 ZDA: ' + sLine)                        # Write the ZDA data to terminal
        datumtijd = parseZda(sLine)                         # parse the raw data string into usable variables
        if datumtijd == None:                               # if there is no usable data print "datumtijd is none"
            print('Datumtijd is none:')
            bZdaOntvangen = False                           # Boolean bZdaOntvangen is set to False
            status = "IZ"                                   # Change the status to IZ (Invalid ZDA)
        
        else:                                               # If the data is usable 

#            if status == "NZ":
#                status = "FC"
#                datumtijd = False
#            else:
                bZdaOntvangen = True                        # Boolean bZdaOntvangen is set to True
                print ('ZDA out' + ' ' + datumtijd + '\r\n'+ '\r\n')               # Print the usable date and time to terminal
#                status = "OK"
            

                            #Serial AML (Com2)
def serAmlReader():
    
    while True:                                             # loop forever
        b1Line = serAml.readline()                          # read the line from serial ALM and write it to blLine
#        print b1Line
        s1Line = b1Line.decode(encoding='utf_8')            # Decode the data from serial ALM to usable data
        s1Line = s1Line.rstrip(' ' +'\r\n')
#        global AmlMessage
#        AmlMessage = 
        pass
        print (' COM2 AML: '+s1Line)                        # Print the raw data to console 
        print ( datetime.datetime.now())                    # Print to console AML was received
        isAmlValid = parseAml(s1Line)                       # turn the raw data into usable data blocks
        global bZdaOntvangen
        if isAmlValid == None:                              # if the data is garbage print "AML not valid" to console
            print('AML not valid')
        
        else:
            print (isAmlValid+ '\r\n'+ '\r\n')              # Print status (OK)to console 


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
    global datumTijd
    global status
    print (bZdaOntvangen)                                   #Print the current value of bZdaOntvangen to the terminal



    if bZdaOntvangen == True:                                   # if ZDAontvangen is true
        bZdaOntvangen = False                                       # ZDAontvangnen is set to false (as we are doing something with the data it's not fresh anymore
        os.system('date -s %s' % datumTijd)                         # Sets the system time to datumtijd (the time set per ZDA)
        datumtijd = False                                           # datumTijd is cleared out so when we receive another puls before  ZDA we won't get stuck in the past
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
        
        print('Send over Ethernet')                             # send to console that data is being sent over ethernet                    
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




                                                  # terminate thread
