import socket
import sched
import time

UDP_IP = "192.168.1.22"
UDP_PORT = 5001
MESSAGE = "hello world" +'\r\n'



sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


while True:
#    print ('1 sec')
    time.sleep(1 - time.time() %1)
    print ("UDP TARGET IP" , UDP_IP)
    print ("UDP TARGET PORT", UDP_PORT)
    print ("message:" , MESSAGE)
    sock.sendto(bytes(MESSAGE, "utf-8"), (UDP_IP, UDP_PORT))
    
