import serial
import time
arduino = serial.Serial("/dev/ttyACM0", 115200)
arduino.reset_input_buffer()

def encoder_status():
    arduino.reset_input_buffer()
    encoder_ticks=arduino.readline().decode('utf-8').rstrip()
    return encoder_ticks

while True:
    print(float(encoder_status()))
