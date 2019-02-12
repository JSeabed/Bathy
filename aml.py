def parseAml (raw_mess):
    global AmlMessage
    global UDP_IP1                                              #Getting some global variables
    global UDP_PORT1
    global UDP_IP2
    global UDP_PORT2
    global sLineAml; sLineAml = raw_mess.split('  ')        # with split() each space seperated piece of raw_mess is written in array sLinesAml. 
    #print sLineAml

    if len(sLineAml) < 4:
        sock1.sendto(raw_mess + '\r\n', (UDP_IP1, UDP_PORT1))          # send the string to the first IP address over UDP
        sock2.sendto(raw_mess + '\r\n', (UDP_IP2, UDP_PORT2)) 

    getTime()
    global dataToSend
    global status


    i = 1
    LinesToSend = ""
    dataToSend = 'AML OK >> $SBDAML' + ',' + dateNow
    while i < len(sLineAml):
        linesToSend = linesToSend + ',' + sLineAml[i]
    dataToSend = dataToSend + lineToSend + status + '\r\n'

    return dataToSend

    status = "NC"
    del sLineAml                                            # Clearing out the data from sLineAml so no old data is processed the next time
    return ' AML OK'+' >> '+ dataToSend                     # Send confirmation + data (AML OK >> parsed data ) to console


def serAmlReader():
    while True:
        b1Line = serAml.readline()                          # read the line from serial ALM and write it to blLine
        result = "$SBDAML,01-01-2000,02:17:02.722622,0000.000,00.000,21.923,0001.567,008.07,00.000,0000.000,0000.00,st"
        dummy = "0000.000  00.000  21.158  0001.534  008.07  00.000  0000.000  0000.00"
        b1Line = dummy

        s1Line = b1Line.decode(encoding='utf_8')            # Decode the data from serial ALM to usable data
        s1Line = s1Line.rstrip(' ' +'\r\n')
#        global AmlMessage
#        AmlMessage = 
        pass
        isAmlValid = parseAml(s1Line)                       # turn the raw data into usable data blocks
        global bZdaOntvangen
   #     if isAmlValid == None:                              # if the data is garbage print "AML not valid" to console
            #print('AML not valid')
       # else:
         #   print (isAmlValid+ '\r\n'+ '\r\n')              # Print status (OK)to console 
