# Splitting the AML Data into variables and combining with time
# parseAml gets called from within serAmlReader and is expected to
# return a value that is to be send over the sockets to the designated IP adresses.
# This function 

import datetime
import serial
import socket

def parseAml (raw_mess):
    UDP_IP1 = "10.68.5.91"
    UDP_PORT1 = 5001

    UDP_IP2 = "172.16.10.50"
    UDP_PORT2 = 5001

    sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # with split() each space seperated piece of raw_mess is written in array sLinesAml. 
    sLineAml = raw_mess.split('  ')
    print sLineAml

    # if the data is shorter then 5 blocks of data run next line
    if len(sLineAml) < 2:
        sock1.sendto(raw_mess + '\r\n', (UDP_IP1, UDP_PORT1))
        sock2.sendto(raw_mess + '\r\n', (UDP_IP2, UDP_PORT2))
#
    dateNow = getTime()
    dataToSend = '$SBDAML' + ',' + dateNow
    LinesToSend = ','.join(sLineAml[1:])
    dataToSend = dataToSend + ',' + LinesToSend
    return dataToSend

def serAmlReader():
    import serial
    # Open Com port of AML (connected through P9_21 and P9_22)
    # Linking serAml to the correct Com port with the correct baudrate and setting the state of the port to open.
    serAml = serial.Serial('/dev/ttyO2')
    serAml.baudrate = 38400
    serAml.isOpen()

    while True:
        # read the line from serial ALM and write it to blLine
        b1Line = serAml.readline()

        result = "$SBDAML,01-01-2000,02:17:02.722622,0000.000,00.000,21.923,0001.567,008.07,00.000,0000.000,0000.00,st"
        dummy = "0000.000  00.000  21.158  0001.534  008.07  00.000  0000.000  0000.00"
        #b1Line = dummy
        # Decode the data from serial ALM to usable data
        try:
            s1Line = b1Line.decode(encoding='utf_8')
            s1Line = s1Line.rstrip(' ' +'\r\n')
        except:
            s1Line = "0,0,0,0"
            
            # turn the raw data into usable data blocks
        isAmlValid = parseAml(s1Line)
        return isAmlValid

def getTime():
    # currentDateTime is the current time plus one second 
    currentDateTimeRaw = datetime.datetime.now() + datetime.timedelta(seconds =1)
    currentDateTime = currentDateTimeRaw.strftime('%H:%M:%S.%f,%d,%m,%Y')
    currentTime = currentDateTime.split(',')
    # format is day+month+year
    return  currentTime[1] + '-' + currentTime[2] + '-' + currentTime[3] + ',' + currentTime[0]

