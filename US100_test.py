import adafruit_us100
import time
import serial
import subprocess
import os
os.system("systemctl stop serial-getty@ttyS2.service")
uart_2=serial.Serial("/dev/ttyS2",baudrate=9600,timeout=1)
uart_4=serial.Serial("/dev/ttyS4",baudrate=9600,timeout=1)
while True:
    uart_2_speed = subprocess.getoutput("sudo stty -F /dev/ttyS2 speed")
    uart_4_speed = subprocess.getoutput("sudo stty -F /dev/ttyS4 speed")
    CPU_temp = subprocess.getoutput("sudo cat /sys/class/thermal/thermal_zone0/temp")
    us100_uart_2 = adafruit_us100.US100(uart_2)
    us100_uart_4 = adafruit_us100.US100(uart_4)
    print("CPU_temp: ", CPU_temp)
    print("UART_2: ", "Speed: ", uart_2_speed, "Temp: ", us100_uart_2.temperature, "Distance: ", us100_uart_2.distance)
    print("UART_4: ", "Speed: ", uart_4_speed, "Temp: ", us100_uart_4.temperature, "Distance: ", us100_uart_4.distance)
    time.sleep(0.1)
