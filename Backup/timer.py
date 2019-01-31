#from _overlapped import NULL
#from test.support import temp_cwd


import sys
import serial
import threading
import time
import logging
import threading
import time
import socket
from macpath import join
sys.path.append(r'/home/pi/pysrc')
import RPi.GPIO as GPIO
import pydevd
#sys.path.append(r'/home/pi/RPi.GPIO-0.1.0')
#pydevd.settrace('192.168.2.40')

sDag = ''; sMaand = ''; sJaar = ''; sUur = ''; sMinuut = ''; sSecond = ''; sMSecond = ''; datum = ''; tijd = ''
sAml0 = ''; sAml1 = ''; sAml2 = ''; sAml3 = ''; sAml4 = ''; sAml5 = ''; sAml6 = '';


bTrigger = False    #Dit is de trigger die aangezet wordt door de input. Hij zal vervolgens False gemaakt als de string wordt verstuurdt
bZdaOntvangen = False # Dit is om te bepalen of een recente ZDA ontvangen is. Anders weten we dat de variabelen met tijd en datum niet vers zijn
bAmlOntvange = False # Dit is om te bepalen of een recente AML ontvangen is.

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

#Stel GPIO IN
GPIO.setmode(GPIO.BCM)  #setup GPIO using Board numbering
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#Open Com poort van GPZDA
serZda = serial.Serial('/dev/ttyAMA0')
serZda.baudrate = 9600
serZda.isOpen()      


#Open Com poort van AML
serAml = serial.Serial('/dev/ttyUSB0')
serAml.baudrate = 9600
serAml.isOpen()      

#Define trigger op Kanaal 7 BCM
def pulse(channel):
    global bTrigger; bTrigger = True
    
    writeCom1('Trigger gekregen\r\n')
    writeCom2('Trigger gekregen\r\n')
    
GPIO.add_event_detect(7, GPIO.RISING, callback=pulse, bouncetime = 300)  # add rising edge detection on a channel the rest of your program...

def parseAml (raw_mess):
    sLineAml = raw_mess.split(' ')
    if len(sLineAml) < 7:
        return None
    global sAml0; sAml0 = sLineAml[0]
    global sAml1; sAml1 = sLineAml[1]
    global sAml2; sAml2 = sLineAml[2]
    global sAml3; sAml3 = sLineAml[3]
    global sAml4; sAml4 = sLineAml[4]
    global sAml5; sAml5 = sLineAml[5]
    global sAml6; sAml6 = sLineAml[6]
    
    return 'OK'

def parseZda(raw_message):
    if raw_message is None:
        return None
    try:
        sLines = raw_message.split(',')
        if len(sLines) < 7:
            return None
        if len(sLines[1]) < 9:
            return None
        tempTijd = sLines[1]
        global sUur
        sUur = tempTijd[:2]
        global sMinuut
        sMinuut = tempTijd[2:4]
        global sSecond
        sSecond = tempTijd[4:6]
        global sMSecond
        sMSecond = tempTijd[7:]
        global tijd
        tijd = tempTijd[:2] + ':' + tempTijd[2:4] + ':' + tempTijd[4:]                  #Tijd wordt hier bepaald
        if len(sLines[2]) < 2 or len(sLines[3]) < 2 or len(sLines[4]) < 2:
            return None
        global sDag
        sDag = sLines[2]
        global sMaand
        sMaand = sLines[3]
        global sJaar
        sJaar = sLines[4]
        global datum
        datum = sDag + '/' + sMaand + '/' + sJaar                           #Datum wordt hier bepaald
        return (datum + ' ' + tijd)
    except Exception as e:
        print ('Exception: ' + e)
        pass
    
#Serial port 1 ZDA Reader
def serZdaReader():
    dataToSend = 'Hallo\r\n'; 
     
    while True:
       # serZda.write(dataToSend.encode(encoding='utf_8', errors='strict'))
        bLine = serZda.readline()
        sLine = bLine.decode(encoding='utf_8')
        
        writeCom1(sLine)
        pass
        print (sLine)
        datumtijd = parseZda(sLine)
        if datumtijd == None:
            print('Datumtijd is none:')
        
        else:
            bZdaOntvangen = True #ZDA is ontvangen, de variabelen zijn ingevuld, ze zijn dus vers
            print (datumtijd)
            writeCom1(datumtijd + '\r\n')

#Serial port 2 AML Reader
def serAmlReader():
    
    writeCom2('Hallo\r\n')
    while True:
       # serZda.write(dataToSend.encode(encoding='utf_8', errors='strict'))
        b1Line = serAml.readline()
        s1Line = b1Line.decode(encoding='utf_8')
        pass
        print ('\r\nOntvangen van COM2 AML: '+s1Line)
        writeCom2('\r\nOntvangen van COM2 AML: '+s1Line)
        isAmlValid = parseAml(s1Line)
        if isAmlValid == None:
            print('AML not valid')
        
        else:
            bZdaOntvangen = True #ZDA is ontvangen, de variabelen zijn ingevuld, ze zijn dus vers
            print (isAmlValid)
            writeCom2(isAmlValid + '\r\n')




#Serial poort 1 ZDA Writer
def writeCom1(textToWrite):
    serZda.write(textToWrite.encode(encoding='utf_8', errors='strict'))

#Serial poort 2 AML Writer
def writeCom2(textToWrite):
    serAml.write(textToWrite.encode(encoding='utf_8', errors='strict'))




def socketWriter (conn):
    while True:
        if bTrigger:
            print('In Socket writer\r\n')
            dataToSend = '\r\n'
            if sDag is not None and sAml0 is not None :
                dataToSend = ''+sDag +'/'+ sMaand +'/'+ sJaar +' ' + sUur + ':'+ sMinuut+ ':' + sSecond + ':' + sMSecond + ' ' + sAml2 + ' ' + sAml3 + ' ' + sAml4 + ' ' + sAml5 + ' ' + sAml6 
                        
            try:
                
                print (dataToSend)
                conn.send(dataToSend.encode())
            except socket.error as msg:
                print ('Socket failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            #global bTrigger
            global bTrigger;     bTrigger = False
        




serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#bind the socket to a public host,
# and a well-known port
#Bind socket to local host and port
try:
    serversocket.bind(('', 5001))
    print ('Binding ' + socket.gethostname())
except socket.error as msg:
    print ('Bind failed. Error Code : ' + str(msg) )
    #sys.exit()
    #become a server socket
serversocket.listen(5)

#Start thread serial 1 ZDA Reader
thrZda = threading.Thread(name='serZdaReader', target=serZdaReader)
thrZda.start()

#Start thread serial 2 AML Reader
thrAml = threading.Thread(name='serAmlReader', target=serAmlReader)
thrAml.start()


while 1:
    #wait to accept a connection - blocking call
    conn, addr = serversocket.accept()
    print ('Connected with ' + addr[0] + ':' + str(addr[1]))
     
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    #start_new_thread(clientthread ,(conn,))
    tSock = threading.Thread(target=socketWriter(conn))
    tSock.start()
    tSock.join()
