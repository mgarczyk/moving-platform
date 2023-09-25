import time
import adafruit_tfmini
import serial
import periphery
import adafruit_us100
from periphery import GPIO

##MUX PINOUT##
MUX_PIN_A=154
MUX_PIN_B=156
MUX_GPIO_A=GPIO(MUX_PIN_A,"out")
MUX_GPIO_B=GPIO(MUX_PIN_B,"out")

def lift():
    Dir_LIFT_GPIO.write(True)
    PWM_LIFT_GPIO.write(True)

def lower():
    Dir_LIFT_GPIO.write(False)
    PWM_LIFT_GPIO.write(True)

def stop():
    PWM_LIFT_GPIO.write(False)


def height_return(uart, tfmini):
    height=tfmini.distance
    return height

# uart = serial.Serial("/dev/ttyS2", timeout=1)
# tfmini = adafruit_tfmini.TFmini(uart)

Dir_LIFT_GPIO=periphery.GPIO(157,"out")
PWM_LIFT_GPIO=periphery.GPIO(42,"out")


stop()