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
import RPi.GPIO as GPIO                                     # readying the code for GPIO usage
import pydevd                                               # Import remote debugger
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
sAml0 = ''
sAml1 = ''
sAml2 = ''
sAml3 = ''
sAml4 = ''
sAml5 = ''
sAml6 = ''
sAml7 = ''
sAml8 = ''
sAml9 = ''
sAml10 = ''
sAml11 = ''
sAml12 = ''
sAml13 = ''
sAml14 = ''
sAml15 = ''
sAml16 = ''
sAml17 = ''
status = '00'
dataToSend = '\r\n'+'$SBDAML,,,,,,,,00'

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

#/////////////////////////////////   Defining triggers for functions    /////////////////////////////////

bTrigger = False                                            # This trigger is used for the PPS input
bZdaOntvangen = False                                       # This trigger is to keep track of the "freshness" of the ZDA time info
bAmlOntvange = False                                        # This trigger is to see if there is unsent AML info.


#/////////////////////////////////    Error/debug logging functionality   ///////////////////////////////

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )


#/////////////////////////////////  GPIO configuration   ////////////////////////////////////////////////

#Configuring the general pins for input/output (GPIO
GPIO.setmode(GPIO.BCM)                                      # setup GPIO using Board numbering
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)          # setting Pin 7 as input, also a pull-down resistor is turned on internally


#///////////////////   Serial communication configurations    ///////////////////////////////////////////

#Open Com port of GPZDA (connected via pin 8 and 10 of GPIO)
serZda = serial.Serial('/dev/ttyUSB0')                      # Linking serZDA to the correct Com port
#serZda = serial.Serial('/dev/ttyAMA0')                      # Linking serZDA to the correct Com port
#serZda.baudrate = 38400                                     # Setting the communication speed of the serial port
serZda.baudrate = 9600                                      # Setting the communication speed of the serial port
serZda.isOpen()                                             # Open serial port


#Open Com port of AML (connected via USB)
serAml = serial.Serial('/dev/ttyAMA0')                      # Linking serAml to the correct Com port
#serAml = serial.Serial('/dev/ttyUSB0')                      # Linking serAml to the correct Com port
#serAml.baudrate = 9600                                      # Setting the communication speed of the serial port
serAml.baudrate = 38400                                     # Setting the communication speed of the serial port
serAml.isOpen()                                             # Open serial port




#/////////////////////////////////  Processing the incoming data by splitting it and putting it in usable variables  //////////



                        #Clearing data from AML

def clearAml():
    global sAml0; sAml0 = ''                      #resetting all Aml data to 0
    global sAml1; sAml1 = ''                       
    global sAml2; sAml2 = ''
    global sAml3; sAml3 = ''
    global sAml4; sAml4 = ''
    global sAml5; sAml5 = ''
    global sAml6; sAml6 = ''
    global sAml7; sAml7 = ''
    global sAml8; sAml8 = ''
    global sAml9; sAml9 = ''
    global sAml10; sAml10 = ''
    global sAml11; sAml11 = ''
    global sAml12; sAml12 = ''
    global sAml13; sAml13 = ''
    global sAml14; sAml14 = ''
    global sAml15; sAml15 = ''
    global sAml16; sAml16 = ''
    global sAml17; sAml17 = ''
    global datumNu; datumNu = ''
    global dataToSend; dataToSend = '\r\n'+'$SBDAML,,,,,,,,00'
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
    if raw_message is None:                                 # if no data is sent stop the madness
        return None
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
        return ' ZDA OK' + ' >> ' + datumTijd           # Send confirmation + data (ZDA OK >> parsed data ) to console and Com1    
    except Exception as e:                                      # if something goes wrong print the error to console
        print ('Exception: ' + e)
        #pass


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


    del sLineAml                                            # Clearing out the data from sLineAml so no old data is processed the next time
    return ' ALM OK'+' >> '+ dataToSend                     # Send confirmation + data (AML OK >> parsed data ) to console


#/////////////////////////////////   Serial receive loops   /////////////////////////////////////////////


                                #Serial ZDA (Com1)
    
def serZdaReader():
#    writeCom1('Hallo ZDA\r\n');                            # just a happy hello while starting up (to see if startup goes the way expected)
     
    while True:                                             # Run forever
        bLine = serZda.readline()                           # Read the incoming data from serial ZDA and put it in bLine
        sLine = bLine.decode(encoding='utf_8')              # decode it into usable data      
#        writeCom1(sLine)                                   # Write the raw data to Com1
        pass
        print (' COM1 ZDA: ' +sLine)                        # Write the raw data to terminal
        datumtijd = parseZda(sLine)                         # parse the raw data string into usable variables
        if datumtijd == None:                               # if there is no usable data print "datumtijd is none"
            print('Datumtijd is none:')
        
        else:                                               # If the data is usable 
            bZdaOntvangen = True                            # The trigger that the data is fresh is put to true
            print (datumtijd+ '\r\n'+ '\r\n')               # Print the usable date and time to terminal
#            writeCom1(datumtijd + '\r\n')                  # Write the usable date and time to Com1 




                            #Serial AML (Com2)
def serAmlReader():
    
#    writeCom2('Hallo AML\r\n')
    while True:                                             # loop forever
        b1Line = serAml.readline()                          # read the line from serial ALM and write it to blLine
        s1Line = b1Line.decode(encoding='utf_8')            # Decode the data from serial ALM to usable data
        s1Line = s1Line.rstrip(' ' +'\r\n')

#        getTime()
#        writeCom2(s1Line)                                   # Write the raw data to Com2
        pass
        print (' COM2 AML: '+s1Line)                        # Print the raw data to console 
        print ( datetime.datetime.now())                    # Print to console AML was received
        isAmlValid = parseAml(s1Line)                       # turn the raw data into usable data blocks
        if isAmlValid == None:                              # if the data is garbage print "AML not valid" to console
            print('AML not valid')
        
        else:
            bZdaOntvangen = True                            # If the data is not garbage do the following
            print (isAmlValid+ '\r\n'+ '\r\n')              # Print status (OK)to console 
#            writeCom2(isAmlValid + '\r\n')                  # Print status (OK) to Com2


#////////////////////////////////////// Serial Write loops  /////////////////////////////////////////////


def writeCom1(textToWrite):                                                 # Serial port 1 ZDA Writer
    serZda.write(textToWrite.encode(encoding='utf_8', errors='strict'))     # Encode data to serial protocol for Com1


def writeCom2(textToWrite):                                                 # Serial poort 2 AML Writer
    serAml.write(textToWrite.encode(encoding='utf_8', errors='strict'))     # Encode data to serial protocol for Com2



#///////////////////////////////// This is what happenes when pin 7 (PPS) goes high   ///////////////////

                        #When pulse() is used this is what happens
def pulse(channel):
    global bTrigger; bTrigger = True                        # First the bTrigger is set to True to show a fresh pulse has been received    
#    writeCom1('Trigger gekregen\n')                         # A confirmation is sent to Com1
#    writeCom2('Trigger gekregen\n')                         # A confirmation is sent to Com2 
    print('trigger' )                                       # Give the terminal that PPS was received
    print (datetime.datetime.now())                         # Print to console PPS was received
#    print ('3'+ datumTijd)
    os.system('date -s %s' % datumTijd)
#    os.system('date -s "1 second"')

    
                        #This is the detector that sees the pin goes high then starts the function pulse
GPIO.add_event_detect(7, GPIO.RISING, callback=pulse, bouncetime = 300)  # add rising edge detection on a channel the rest of your program...





#////////////////////////////////////// Ethernet write loops   //////////////////////////////////////////

def socketWriter (conn): 
    while True:

            print('Send over Ethernet')                             # send to console that data is being sent over ethernet                   
            try:                                                    # Try to do following, if there is an error go to exept
#                print (datetime.datetime.now())                     # Print to console the message sent to Ethernet
                global dataToSend 
                print (dataToSend + '\r\n')                         # Print to console the message sent to Ethernet
                conn.send(dataToSend.encode())                      # Send data through ethernet (after encoding it)
                clearAml()
                
            except socket.error as msg:                             # if there is an error print it to console
                print ('Socket failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])

            time.sleep(1)                                           # Wait for a second (minus runtime of the code) and repeat
#            time.sleep(1 - time.time() %1)                          # Wait for a second (minus runtime of the code) and repeat


#//////////////////////////////////// Ethernet connection setup   ///////////////////////////////////////

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # Create an ethernet socket
#bind the socket to a public host,
# and a well-known port
try:
    serversocket.bind(('', 5001))                                   # Bind the socket to port 5001
    print ('Binding ' + socket.gethostname())                       # Print "binding 'hostname' " to show it is ready for connection 
except socket.error as msg:                                         # if there is an error do following
    print ('Bind failed. Error Code : ' + str(msg) )                # print the error to console
    #sys.exit() 
    #become a server socket
serversocket.listen(5)                                              # set as passive socket


#//////////////////////////////////// Serial loop    ////////////////////////////////////////////////////

#Start thread serial 1 ZDA Reader
thrZda = threading.Thread(name='serZdaReader', target=serZdaReader) # Create a thread for serial communication(thrZDA) 
thrZda.start()                                                      # Start said thread

#Start thread serial 2 AML Reader
thrAml = threading.Thread(name='serAmlReader', target=serAmlReader) # Create a thread for serial communication(thrAML) 
thrAml.start()                                                      # Start said thread


#////////////////////////////////// Ethernet Loop   /////////////////////////////////////////////////////

while 1:                                                            # do forever    
    conn, addr = serversocket.accept()                              # wait to accept a connection - blocking call
    print ('Connected with ' + addr[0] + ':' + str(addr[1]))        # Print confirmation of an ethernet connection by showing IP address and port
     
    tSock = threading.Thread(target=socketWriter(conn))             # Create a thread for Ethernet communication
    tSock.start()                                                   # Start said thread
    tSock.join()                                                    # terminate thread
