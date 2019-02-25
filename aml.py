import datetime

# Splitting the AML Data into variables and combining with time
def parseAml (raw_mess):
    #Getting some global variables
    global UDP_IP1
    global UDP_PORT1
    global UDP_IP2
    global UDP_PORT2   
    # with split() each space seperated piece of raw_mess is written in array sLinesAml. 
    global sLineAml; sLineAml = raw_mess.split('  ')
    print sLineAml

    # if the data is shorter then 5 blocks of data run next line
    if len(sLineAml) < 2:
        sock1.sendto(raw_mess + '\r\n', (UDP_IP1, UDP_PORT1))
        sock2.sendto(raw_mess + '\r\n', (UDP_IP2, UDP_PORT2))

    dateNow = getTime()
    global dataToSend; dataToSend = '$SBDAML' + ',' + dateNow
    global status
    LinesToSend = ','.join(sLineAml[1:])
    dataToSend = dataToSend + LinesToSend + status + '\r\n'
    return dataToSend

def serAmlReader():
    while True:
        # read the line from serial ALM and write it to blLine
        b1Line = serAml.readline()

        result = "$SBDAML,01-01-2000,02:17:02.722622,0000.000,00.000,21.923,0001.567,008.07,00.000,0000.000,0000.00,st"
        dummy = "0000.000  00.000  21.158  0001.534  008.07  00.000  0000.000  0000.00"
        b1Line = dummy
        # Decode the data from serial ALM to usable data
        s1Line = b1Line.decode(encoding='utf_8')
        s1Line = s1Line.rstrip(' ' +'\r\n')
        # turn the raw data into usable data blocks
        isAmlValid = parseAml(s1Line)
        global bZdaOntvangen

def getTime():
    # currentDateTime is the current time plus one second 
    currentDateTimeRaw = datetime.datetime.now() + datetime.timedelta(seconds =1)
    currentDateTime = currentDateTimeRaw.strftime('%H:%M:%S.%f,%d,%m,%Y')
    currentTime = currentDateTime.split(',')
    # format is day+month+year
    return  currentTime[1] + '-' + currentTime[2] + '-' + currentTime[3] + ',' + currentTime[0]

