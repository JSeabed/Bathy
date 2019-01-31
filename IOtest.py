import Adafruit_BBIO.GPIO as GPIO
import time


pin = "P9_12"

GPIO.setup(pin, GPIO.OUT)
#GPIO.setup("P8_42",GPIO.IN)


while True:
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(0.5)
    print("Hi")
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.5)
    print("Lo")



#if GPIO.input("P8_42"):
#    print("high")

#else:
#    print("Low")

#GPIO.wait_for_edge("P8_42", GPIO.RISING)
#print(Upperty)
