import serial
import time
import threading

ser = serial.Serial('/dev/ttyS1', baudrate = 115200)
ser.close()


def talk():
    while True:
        ser.open()
        print (ser)
        ser.write('\r\n'+'bloody hell')
        ser.close()
        time.sleep(1)


loop = threading.Thread(name = 'talk', target=talk)
loop.start()
