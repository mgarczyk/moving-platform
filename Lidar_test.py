import time
import adafruit_tfmini
import serial

UART_LIDAR=serial.Serial("/dev/ttyS4",timeout=1)

tfmini = adafruit_tfmini.TFmini(UART_LIDAR)

#You can put in 'short' or 'long' distance mode
tfmini.mode = adafruit_tfmini.MODE_SHORT
print("Now in mode", tfmini.mode)

while True:
    print("Distance: %d cm (strength %d, mode %x)" %
          (tfmini.distance, tfmini.strength, tfmini.mode))
    time.sleep(0.1)