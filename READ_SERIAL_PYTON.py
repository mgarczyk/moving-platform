import serial
import time

arduino = serial.Serial("/dev/ttyACM1", 115200)
arduino.reset_input_buffer()

def read_encoders():
    try:
        data = arduino.readline().decode().strip() # <- GENERALNIE JAK ROCK odbiera do arduino coś wysyła i dlatgo się psuje to, trzeba to poprawić jakoś.
    except serial.serialutil.SerialException:
        data = None
    print(data)
while True:
    read_encoders()