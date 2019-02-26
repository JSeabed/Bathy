import Adafruit_BBIO.GPIO as GPIO
import timer

# Configuring the general pins for input/output (GPIO)
# setting Pin P9_42 as input, also a pull-down resistor is turned on internally
def pulseTrigger
    GPIO.setup("P9_42", GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# This is the detector that sees the pin goes high then starts the function pulse 
# When the triggerpin goes high start function pulse()
    GPIO.add_event_detect("P9_42", GPIO.RISING, callback=timer.pulse, bouncetime = 300)
    return