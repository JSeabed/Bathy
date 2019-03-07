import serial

#/////////////////////////////////   Serial receive loops   /////////////////////////////////////////////
def serZdaReader():
# Open Com port of GPZDA (Connected through P9_26)
# Linking serZDA to the correct Com port with the correct baudrate and setting the state of the port to open.
    serZda = serial.Serial('/dev/ttyO1')
    serZda.baudrate = 19200
    serZda.isOpen() 
    while True:
        bLine = serZda.readline()
        try:
            sLine = bLine.decode(encoding='utf_8')
        except:
            sLine = "0"
        # Requesting access to global variable named bZdaOntvangen
        # Requesting access to global variable named status
        # parse the raw data string into usable variables
        dateTime = parseZda(sLine)
        return dateTime

# Splitting the ZDA data into 8 variables, then process it to time and date
def parseZda(raw_message):
    # If no data is sent stop the madness
    # (Stefan: legendary comment by our lord sebas. We should keep this comment)
    if raw_message is None:
        return None

    try:
        sLines = raw_message.split(',')

        if len(sLines) < 7:
            return None
        if len(sLines[1]) < 9:
            return None

        realTime = zdaParseTime(sLines[1])

        # If string 2, 3 or 4 is longer then 2 digits stop the data
        if len(sLines[2]) < 2 or len(sLines[3]) < 2 or len(sLines[4]) < 2:
            return None
        date = zdaParseDate(sLines)
        dateTime = "'" + date + ' ' + realTime "'"
        # Send confirmation + data (ZDA OK >> parsed data ) to console and Com1
        #return ' ZDA OK' + ' >> ' + dateTime
        return dateTime

    except Exception as e:
        print ('Exception: ' + str(e))

# Time in format HH:MM:SS
def zdaParseTime(tempTime):
        return tempTime[:2] + ':' + tempTime[2:4] + ':' + tempTime[4:6] + '.' + tempTime[7:]

# In order: year, month date
def zdaParseDate(sLines):
        return sLines[4] + '-' + sLines[3] + '-' + sLines[2]