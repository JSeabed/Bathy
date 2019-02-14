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
        global sDay; sDay = sLines[2]                           # the 3th string of sLines is the day
        global sMaand; sMaand = sLines[3]                       # the 4th string of sLines is the month      
        global sJaar; sJaar = sLines[4]                         # the 3th string of sLines is the year     
        global datum; datum = sJaar + '-' + sMaand + '-' + sDay # The combined data of day+month+year makes the variable datum (date)     
#        return ' ZDA OK' + ' >> ' +datum + ' ' + tijd           # Send confirmation + data (ZDA OK >> parsed data ) to console and Com1
        global dateTime; dateTime = "'" + datum + ' ' + tijd +"'" # The combined data of day+month+year makes the variable dateNow (date)
#        print (dateTime)
#        status = "00"
        return ' ZDA OK' + ' >> ' + dateTime           # Send confirmation + data (ZDA OK >> parsed data ) to console and Com1

    except Exception as e:                                      # if something goes wrong print the error to console      
        print ('Exception: ' + e)


#/////////////////////////////////   Serial receive loops   /////////////////////////////////////////////
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
       # print (' COM1 ZDA: ' + sLine)                        # Write the ZDA data to terminal
        dateTime = parseZda(sLine)                         # parse the raw data string into usable variables
        if dateTime == None:                               # if there is no usable data print "dateTime is none"
            print('dateTime is none:')
            bZdaOntvangen = False                           # Boolean bZdaOntvangen is set to False
            status = "IZ"                                   # Change the status to IZ (Invalid ZDA)
        else:                                               # If the data is usable 

#            if status == "NZ":
#                status = "FC"
#                dateTime = False
#            else:
                bZdaOntvangen = True                        # Boolean bZdaOntvangen is set to True
                #print ('ZDA out' + ' ' + dateTime + '\r\n'+ '\r\n')               # Print the usable date and time to terminal
#                status = "OK"

                            #Serial AML (Com2)
