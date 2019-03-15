    serSV = serial.Serial('/dev/ttyO4')
    serSV.baudrate = 19200
    serSV.isOpen() 
    testcode = ("test  serial send over new pin") + '\r\n'
    serSV.write("134679")       #this works for sending
    serSV.write(testcode.encode('utf_8'))   #this works as well
    serSV.close()