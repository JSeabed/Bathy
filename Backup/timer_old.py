#!/usr/bin/python

import sys
import socket
import threading
import time
import serial

sys.path.append(r'/home/pi/pysrc')
import pydevd
pydevd.settrace('192.168.2.40')

dataToSend = 'Hallo\r\n';
print (dataToSend)
# Configure Thread Com1 Reader to read data.
'''
def c1Reader():
    ser = serial.Serial('/dev/ttyAMA0')
    ser.baudrate = 9600
    ser.isOpen()
    ser.write(dataToSend.encode(encoding='utf_8', errors='strict'))
    bLine = ser.readline()
    sLine = bLine.decode(encoding='utf_8')
    pass
    print (sLine)
    parser = sergpzparser.SerGpzParser()
    datumtijd = parser.parse(sLine)
    print (datumtijd)
    #pass

tCom1 = FuncThreadthreading.Thread(target=c1Reader)
tCom1.start()
tCom1.join()
 '''

def serGpzParser():   
    dataToSend = 'Hallo\r\n'; 
    ser = serial.Serial('/dev/ttyAMA0')
    ser.baudrate = 9600
    ser.isOpen()       
   # while True:
    ser.write(dataToSend.encode(encoding='utf_8', errors='strict'))
    bLine = ser.readline()
    sLine = bLine.decode(encoding='utf_8')
    pass
    print (sLine)
    datumtijd = parse(sLine)
    print (datumtijd)
    ser.write(datumtijd.encode(encoding='utf_8', errors='strict'))

t1 = threading.Thread(target=serGpzParser)
t1.start
#t1.join
  


def parse(raw_message):
    if raw_message is None:
        return None
    try:
        sLines = raw_message.split(',')
        if sLines.length < 7:
            return None
            if sLines[1].length < 9:
                return None
            tempTijd = sLines[1];
            tijd = tempTijd[:2] + ':' + tempTijd[2:4] + ':' + tempTijd[4:]
            if sLines[2].length < 2 or sLines[3].length < 2 or sLines[4].length < 2:
                return None
            datum = sLines[2] + '/' + sLines[3] + '/' + sLines[4]
            return (datum + ' ' + tijd)
    except Exception as e:
        raise ParserError("Parse error (%s)." % str(e))
    

  

#create an INET, STREAMing socket
#create an INET, STREAMing socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#bind the socket to a public host,
# and a well-known port
#Bind socket to local host and port
try:
    serversocket.bind(('', 5001))
    print ('Binding ' + socket.gethostname())
except socket.error as msg:
    print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
    #become a server socket
serversocket.listen(5)
    
def clientthread(conn):
    #Sending message to connected client
    conn.send('Welcome to the server. Type something and hit enter\r\n'.encode(encoding='utf_8', errors='strict')) #send only takes string
     
    #infinite loop so that function do not terminate and thread do not end.
    while True:
         
        conn.send(dataToSend.encode())
        time.sleep(1)
                 
    #came out of loop
    conn.close()    



#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = serversocket.accept()
    print ('Connected with ' + addr[0] + ':' + str(addr[1]))
     
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    #start_new_thread(clientthread ,(conn,))
    tSock = threading.Thread(target=clientthread(conn))
 
serversocket.close()

# configure the serial connections (the parameters differs on the device you are connecting to)



# get keyboard input
#data = 'Selamunaleykum world!'

# send the character to the device
# (note that I happend a \r\n carriage return and line feed to the characters - this is requested by my device)
#data = ser.read(10)                     #Read ten characters from serial port to data
#print (type(data))
#bytes = str.encode(data)
#ser.write(bytes)
#out = ''
# let's wait one second before reading output (let's give device time to answer)
#time.sleep(1)
#while ser.inWaiting() > 0:
#    out += ser.read(1)
#    if out != '':
#        print (">>" + out)
