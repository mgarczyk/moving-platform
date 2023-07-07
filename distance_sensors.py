import adafruit_us100
import time
import serial
import os


os.system("systemctl stop serial-getty@ttyS2.service")
while True:
    uart=serial.Serial("/dev/ttyS2",baudrate=9600,timeout=1)
    os.system("sudo stty -F /dev/ttyS2 speed")
    os.system("sudo cat /sys/class/thermal/thermal_zone0/temp")
    us100= adafruit_us100.US100(uart)
    print("----------")
    print("Temp: ", us100.temperature)
    print("distance: ", us100.distance)
    time.sleep(0.1)
