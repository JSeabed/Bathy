# Original code by Mehmet Ozturk 
# Modified by Sebastiaan van Essen 07/2016
# This code combines the time precision of the GNSS network and data from ALM sensors
# and sends the data via Ethernet to a computer as a stand alone module.
#

#from _overlapped import NULL
#from test.support import temp_cwd


#/////////////////////////////////  Importing modules for functions later used    ///////////////////////

import os                                                   # importing the possibility to operate system commands
import sys                                                  # Importing the possibility to use some system variables
import serial                                               # Importing the possibility to use serial communication
import threading                                            # Importing the possibility to run multiple operations at the same time
import datetime                                             # Importing some (system) clock operations
import time                                                 # Importing some (system) clock operations
import logging                                              # importing the possibility to track events and log them
import socket                                               # Importing Networking interface
from macpath import join
sys.path.append(r'/home/pi/pysrc')
import Adafruit_BBIO.GPIO as GPIO                                # readying the code for GPIO usage
#import pydevd                                               # Import remote debugger
import string



#/////////////////////////////////  Defining variables used for the data splitting    ///////////////////


#                   These variables are for the parsing of the ZDA data
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
#freshTime = 0

#/////////////////////////////////   Defining triggers for functions    /////////////////////////////////

bTrigger = False                                            # This trigger is used for the PPS input
bZdaOntvangen = False                                       # This trigger is to keep track of the "freshness" of the ZDA time info
bAmlOntvangen = False                                        # This trigger is to see if there is unsent AML info.


#/////////////////////////////////    Error/debug logging functionality   ///////////////////////////////

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )


#/////////////////////////////////  GPIO configuration   ////////////////////////////////////////////////

#Configuring the general pins for input/output (GPIO
#GPIO.setmode(GPIO.BCM)                                      # setup GPIO using Board numbering
GPIO.setup("P9_42", GPIO.IN, pull_up_down=GPIO.PUD_DOWN)          # setting Pin 7 as input, also a pull-down resistor is turned on internally


#///////////////////   Serial communication configurations    ///////////////////////////////////////////

#Open Com port of GPZDA (connected via pin 8 and 10 of GPIO)
serZda = serial.Serial('/dev/ttyO1')                      # Linking serZDA to the correct Com port
serZda.baudrate = 9600                                      # Setting the communication speed of the serial port
serZda.isOpen()                                             # Open serial port


#Open Com port of AML (connected via USB)
serAml = serial.Serial('/dev/ttyO2')                      # Linking serAml to the correct Com port
serAml.baudrate = 38400                                     # Setting the communication speed of the serial port
serAml.isOpen()                                             # Open serial port




#/////////////////////////////////  Processing the incoming data by splitting it and putting it in usable variables  //////////



                        #Clearing data from AML

def clearAml():
    global status
    global datumNu; datumNu = ''
    global dataToSend; dataToSend = '$SBDAML,,,,,,,,' + status + '\r\n'
    print ('AML cleared\r\n')
#    writeCom2('AML cleared\r\n')

                        #Pulling the time from the system and write it into a usable variable

def getTime():

    currentDateTimeRaw = datetime.datetime.now() + datetime.timedelta(seconds =1)
    currentDateTime = currentDateTimeRaw.strftime('%H:%M:%S.%f,%d,%m,%Y')
    currentTime = currentDateTime.split(',')                    # with split() each comma seperated piece of currentDateTime is written in array currentTime.   
        
    global tijdNu; tijdNu = currentTime[0]                      # Splitting the array into time       
    global sDagNu; sDagNu = currentTime[1]                      # Day
    global sMaandNu; sMaandNu = currentTime[2]                  # Month      
    global sJaarNu; sJaarNu = currentTime[3]                    # And year     
    global datumNu; datumNu = sDagNu + '-' + sMaandNu + '-' + sJaarNu + ',' + tijdNu   # The combined data of day+month+year makes the variable datumNu (date)     




                        #Splitting the ZDA data into 8 variables, then process it to time and date

def parseZda(raw_message):
    global bZdaOntvangen
    global status
    
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
#        bZdaOntvangen = False
#        status = "IZ"        
        print ('Exception: ' + e)


                        #Splitting the AML Data into variables and combining with time

def parseAml (raw_mess):
    global sLineAml; sLineAml = raw_mess.split('  ')        # with split() each space seperated piece of raw_mess is written in array sLinesAml. 
    if len(sLineAml) < 4:                                   # if the data is shorter then 5 blocks of data run next line
        return None                                         # return stops the function if the "if statement" is met (see above)
    getTime()                                               # Get the current system time and put it in datumNu
    global dataToSend                                       # make dataToSend (variable) usable in this function
    global status                                           # Do the same as above, but for status

    if len(sLineAml) == 4:                                  # if the data is longer then 3 blocks of data run next line    
        dataToSend = '$SBDAML' + ',' + datumNu + ',' + sLineAml[1] + ',' + sLineAml[2] + ',' + sLineAml[3] + ',' + status + '\r\n'    # Create a string of data   

    elif len(sLineAml) == 5:                                # if the data is longer then 3 blocks of data run next line    
        dataToSend = '$SBDAML' + ',' + datumNu + ',' + sLineAml[1] + ',' + sLineAml[2] + ',' + sLineAml[3] + ',' + sLineAml[4] + ',' + status + '\r\n'  

    elif len(sLineAml) == 6:                                # if the data is longer then 4 blocks of data run next line
        dataToSend = '$SBDAML' + ',' + datumNu + ',' + sLineAml[1] + ',' + sLineAml[2] + ',' + sLineAml[3] + ',' + sLineAml[4] + ',' + sLineAml[5] + ',' + status + '\r\n'  

    elif len(sLineAml) == 7:                                # if the data is longer then 5 blocks of data run next line
        dataToSend = '$SBDAML' + ',' + datumNu + ',' + sLineAml[1] + ',' + sLineAml[2] + ',' + sLineAml[3] + ',' + sLineAml[4] + ',' + sLineAml[5] + ',' + sLineAml[6] + ',' + status + '\r\n'  

    elif len(sLineAml) == 8:                                # if the data is longer then 6 blocks of data run next line
        dataToSend = '$SBDAML' + ',' + datumNu + ',' + sLineAml[1] + ',' + sLineAml[2] + ',' + sLineAml[3] + ',' + sLineAml[4] + ',' + sLineAml[5] + ',' + sLineAml[6] + ',' + sLineAml[7] + ',' + status + '\r\n'

    elif len(sLineAml) == 9:                                # if the data is longer then 8 blocks of data run next line  
        dataToSend = '$SBDAML' + ',' + datumNu + ',' + sLineAml[1] + ',' + sLineAml[2] + ',' + sLineAml[3] + ',' + sLineAml[4] + ',' + sLineAml[5] + ',' + sLineAml[6] + ',' + sLineAml[7] + ',' + sLineAml[8] + ',' + status + '\r\n'   

    elif len(sLineAml) == 10:                               # if the data is longer then 9 blocks of data run next line        
        dataToSend = '$SBDAML' + ',' + datumNu + ',' + sLineAml[1] + ',' + sLineAml[2] + ',' + sLineAml[3] + ',' + sLineAml[4] + ',' + sLineAml[5] + ',' + sLineAml[6] + ',' + sLineAml[7] + ',' + sLineAml[8] + ',' + sLineAml[9] + ',' + status+ '\r\n'    

    elif len(sLineAml) == 11:                               # if the data is longer then 9 blocks of data run next line        
        dataToSend = '$SBDAML' + ',' + datumNu + ',' + sLineAml[1] + ',' + sLineAml[2] + ',' + sLineAml[3] + ',' + sLineAml[4] + ',' + sLineAml[5] + ',' + sLineAml[6] + ',' + sLineAml[7] + ',' + sLineAml[8] + ',' + sLineAml[9] + ',' + sLineAml[10] + ',' + status + '\r\n'   

    elif len(sLineAml) == 12:                               # if the data is longer then 9 blocks of data run next line        
        dataToSend = '$SBDAML' + ',' + datumNu + ',' + sLineAml[1] + ',' + sLineAml[2] + ',' + sLineAml[3] + ',' + sLineAml[4] + ',' + sLineAml[5] + ',' + sLineAml[6] + ',' + sLineAml[7] + ',' + sLineAml[8] + ',' + sLineAml[9] + ',' + sLineAml[10] + ',' + sLineAml[11] + ',' + status + '\r\n'    

    elif len(sLineAml) == 13:                               # if the data is longer then 9 blocks of data run next line        
        dataToSend = '$SBDAML' + ',' + datumNu + ',' + sLineAml[1] + ',' + sLineAml[2] + ',' + sLineAml[3] + ',' + sLineAml[4] + ',' + sLineAml[5] + ',' + sLineAml[6] + ',' + sLineAml[7] + ',' + sLineAml[8] + ',' + sLineAml[9] + ',' + sLineAml[10] + ',' + sLineAml[11] + ',' + sLineAml[12]+ ',' + status + '\r\n'   

    elif len(sLineAml) == 14:                               # if the data is longer then 9 blocks of data run next line        
        dataToSend = '$SBDAML' + ',' + datumNu + ',' + sLineAml[1] + ',' + sLineAml[2] + ',' + sLineAml[3] + ',' + sLineAml[4] + ',' + sLineAml[5] + ',' + sLineAml[6] + ',' + sLineAml[7] + ',' + sLineAml[8] + ',' + sLineAml[9] + ',' + sLineAml[10] + ',' + sLineAml[11] + ',' + sLineAml[12]+ ',' + sLineAml[13] + ',' + status + '\r\n'   

    elif len(sLineAml) == 15:                               # if the data is longer then 9 blocks of data run next line        
        dataToSend = '$SBDAML' + ',' + datumNu + ',' + sLineAml[1] + ',' + sLineAml[2] + ',' + sLineAml[3] + ',' + sLineAml[4] + ',' + sLineAml[5] + ',' + sLineAml[6] + ',' + sLineAml[7] + ',' + sLineAml[8] + ',' + sLineAml[9] + ',' + sLineAml[10] + ',' + sLineAml[11] + ',' + sLineAml[12]+ ',' + sLineAml[13] + ',' + sLineAml[14]+ ',' + status + '\r\n'   

    elif len(sLineAml) == 16:                               # if the data is longer then 9 blocks of data run next line        
        dataToSend = '$SBDAML' + ',' + datumNu + ',' + sLineAml[1] + ',' + sLineAml[2] + ',' + sLineAml[3] + ',' + sLineAml[4] + ',' + sLineAml[5] + ',' + sLineAml[6] + ',' + sLineAml[7] + ',' + sLineAml[8] + ',' + sLineAml[9] + ',' + sLineAml[10] + ',' + sLineAml[11] + ',' + sLineAml[12]+ ',' + sLineAml[13] + ',' + sLineAml[14]+ ',' + sLineAml[15]+ ',' + status + '\r\n'   

    elif len(sLineAml) == 17:                               # if the data is longer then 9 blocks of data run next line        
        dataToSend = '$SBDAML' + ',' + datumNu + ',' + sLineAml[1] + ',' + sLineAml[2] + ',' + sLineAml[3] + ',' + sLineAml[4] + ',' + sLineAml[5] + ',' + sLineAml[6] + ',' + sLineAml[7] + ',' + sLineAml[8] + ',' + sLineAml[9] + ',' + sLineAml[10] + ',' + sLineAml[11] + ',' + sLineAml[12]+ ',' + sLineAml[13] + ',' + sLineAml[14]+ ',' + sLineAml[15]+ ',' + sLineAml[16]+ ',' + status + '\r\n'   

    elif len(sLineAml) == 18:                               # if the data is longer then 9 blocks of data run next line        
        dataToSend = '$SBDAML' + ',' + datumNu + ',' + sLineAml[1] + ',' + sLineAml[2] + ',' + sLineAml[3] + ',' + sLineAml[4] + ',' + sLineAml[5] + ',' + sLineAml[6] + ',' + sLineAml[7] + ',' + sLineAml[8] + ',' + sLineAml[9] + ',' + sLineAml[10] + ',' + sLineAml[11] + ',' + sLineAml[12]+ ',' + sLineAml[13] + ',' + sLineAml[14]+ ',' + sLineAml[15]+ ',' + sLineAml[16]+ ',' + sLineAml[17]+ ',' + status + '\r\n'   

    status = "NC"
    del sLineAml                                            # Clearing out the data from sLineAml so no old data is processed the next time
    return ' ALM OK'+' >> '+ dataToSend                     # Send confirmation + data (AML OK >> parsed data ) to console


#/////////////////////////////////   Serial receive loops   /////////////////////////////////////////////


                                #Serial ZDA (Com1)
    
def serZdaReader():
     
    while True:                                             # Run forever
        bLine = serZda.readline()                           # Read the incoming data from serial ZDA and put it in bLine
        try:
            sLine = bLine.decode(encoding='utf_8')              # decode it into usable data      

        except:
            pass

        pass
        global bZdaOntvangen
        global status
        print (' COM1 ZDA: ' +sLine)                        # Write the raw data to terminal
        datumtijd = parseZda(sLine)                         # parse the raw data string into usable variables
        if datumtijd == None:                               # if there is no usable data print "datumtijd is none"
            print('Datumtijd is none:')
            bZdaOntvangen = False
            status = "IZ"
        
        else:                                               # If the data is usable 

#            if status == "NZ":
#                status = "FC"
#                datumtijd = False
#            else:
                bZdaOntvangen = True                            # The trigger that the data is fresh is put to true
                print ('ZDA out' + ' ' + datumtijd + '\r\n'+ '\r\n')               # Print the usable date and time to terminal
#                status = "OK"
            

                            #Serial AML (Com2)
def serAmlReader():
    
    while True:                                             # loop forever
        b1Line = serAml.readline()                          # read the line from serial ALM and write it to blLine
        s1Line = b1Line.decode(encoding='utf_8')            # Decode the data from serial ALM to usable data
        s1Line = s1Line.rstrip(' ' +'\r\n')

        pass
        print (' COM2 AML: '+s1Line)                        # Print the raw data to console 
        print ( datetime.datetime.now())                    # Print to console AML was received
        isAmlValid = parseAml(s1Line)                       # turn the raw data into usable data blocks
        global bZdaOntvangen
        if isAmlValid == None:                              # if the data is garbage print "AML not valid" to console
            print('AML not valid')
        
        else:
#            bAlmOntvangen = True                            # If the data is not garbage do the following
            print (isAmlValid+ '\r\n'+ '\r\n')              # Print status (OK)to console 


#////////////////////////////////////// Serial Write loops  /////////////////////////////////////////////


def writeCom1(textToWrite):                                                 # Serial port 1 ZDA Writer
    serZda.write(textToWrite.encode(encoding='utf_8', errors='strict'))     # Encode data to serial protocol for Com1


def writeCom2(textToWrite):                                                 # Serial poort 2 AML Writer
    serAml.write(textToWrite.encode(encoding='utf_8', errors='strict'))     # Encode data to serial protocol for Com2



#///////////////////////////////// This is what happenes when pin 7 (PPS) goes high   ///////////////////

                        #When pulse() is used this is what happens
def pulse(channel):
#    global bTrigger; bTrigger = True                        # First the bTrigger is set to True to show a fresh pulse has been received    
    print('trigger' )                                       # Give the terminal that PPS was received
    print (datetime.datetime.now())                         # Print to console PPS was received
    global bZdaOntvangen
    global datumTijd
    global status
    print (bZdaOntvangen)



    if bZdaOntvangen == True:
        bZdaOntvangen = False
        os.system('date -s %s' % datumTijd)                     # Sets the system time to datumtijd (the time set per ZDA)
        datumtijd = False
        status = "OK"
    else:
        status = 'NZ'
        bZdaOntvangen = False

#    bZdaOntvangen = False
    
                        #This is the detector that sees the pin goes high then starts the function pulse
GPIO.add_event_detect("P9_42", GPIO.RISING, callback=pulse, bouncetime = 300)  # add rising edge detection on a channel the rest of your program...





#////////////////////////////////////// Ethernet write loops   //////////////////////////////////////////


UDP_IP = "192.168.1.22"
#UDP_IP = "192.168.1.22"
UDP_PORT = 5001
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def UDPsender():
    while True:

        print('Send over Ethernet')                             # send to console that data is being sent over ethernet                    
        global dataToSend; print (dataToSend + '\r\n')                         # Print to console the message sent to Ethernet
#        sock.sendto(bytes(dataToSend, "utf-8"), (UDP_IP, UDP_PORT))
        sock.sendto(dataToSend, (UDP_IP, UDP_PORT))
#        global status; status = "AZ"
        clearAml()
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
