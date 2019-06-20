import os
import sys
import serial
import datetime
import time
import Adafruit_BBIO.GPIO as GPIO

GPIO.setup("P9_42", GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

serZda = serial.Serial('/dev/ttyO1')
serZda.baudrate = 19200
serZda.isOpen()

def serZdaReader():

    while True:
        try:
            bLine = serZda.readline()
            sLine = bLine.decode(encoding='utf_8')
        except:
            sLine = "0"
            return
        dateTime = parseZda(sLine)
        time.sleep(0.1)
        return dateTime

def parseZda(raw_message):
    # If no data is sent stop the madness
    # (Stefan: legendary comment by our lord sebas. We should keep this comment)
    try:
        sLines = raw_message.split(',')

        if len(sLines) < 7:
            return None
        if len(sLines[1]) < 9:
            return None

        realTime = zdaParseTime(sLines[1])
        if len(sLines[2]) < 2 or len(sLines[3]) < 2 or len(sLines[4]) < 2:
            return None
        date = zdaParseDate(sLines)
        dateTime = "'" + date + ' ' + realTime + "'"
        return dateTime

    except Exception as e:
        print ('Exception: ' + str(e))
        return None

#Time 
def zdaParseTime(tempTime):
    return tempTime[:2] + ':' + tempTime[2:4] + ':' + tempTime[4:6] + '.' + tempTime[7:]

def zdaParseDate(sLines):
    return sLines[4] + '-' + sLines[3] + '-' + sLines[2]

def pulse(channel):
    dateTime = serZdaReader()
    os.system('date -s %s' % dateTime)
    return

datetime.datetime.now
GPIO.add_event_detect("P9_42", GPIO.RISING, callback=pulse, bouncetime = 300)
print('gpio initialised')