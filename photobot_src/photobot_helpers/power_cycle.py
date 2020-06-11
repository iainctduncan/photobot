#import RPi.GPIO as GPIO
import time

def power_cycle(seconds=5,pin=21):

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

    time.sleep(seconds)
    GPIO.output(pin, GPIO.LOW)

    time.sleep(1)
    GPIO.cleanup()