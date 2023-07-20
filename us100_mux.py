from re import U
from periphery import GPIO
import time
import adafruit_us100
import time
import serial
import os
import subprocess

##MUX PINOUT##
MUX_PIN_A=71
MUX_PIN_B=72
MUX_GPIO_A=GPIO(MUX_PIN_A,"out")
MUX_GPIO_B=GPIO(MUX_PIN_B,"out")

##UART ENABLE / US100
os.system("systemctl stop serial-getty@ttyS2.service")

def Sensors(VAR_A,VAR_B):     
    UART_US100=serial.Serial("/dev/ttyS4",baudrate=9600,timeout=1)
    MUX_GPIO_A.write(VAR_A)
    MUX_GPIO_B.write(VAR_B)
    time.sleep(0.5)    
    us100= adafruit_us100.US100(UART_US100)
    distance=us100.distance
    return(distance)

def main():
    while True:
        try:
            x1=Sensors(False,False)
            print("X1",x1)
            time.sleep(0.1)
            x2=Sensors(False,True)
            print("X2", x2)
            time.sleep(0.1)
            x3=Sensors(True,False)
            print("x3:",x3)
            time.sleep(0.1)
            x=Sensors(True,True)
            print("x4 ",x)
            time.sleep(0.1)
        except KeyboardInterrupt:
            MUX_GPIO_A.write(False)
            MUX_GPIO_B.write(False)
            break

if __name__ == "__main__":
    main()
