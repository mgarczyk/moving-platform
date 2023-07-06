import adafruit_us100
import time
import serial



while True:
	ser=serial.Serial(port="/dev/ttyS2",baudrate=9600,timeout=1)
	ser.write(b'U')
	time.sleep(0.1)
	response=ser.read()	
	print(response)

	distance=int.from_bytes(response,byteorder='little')
	print("Distance: ",distance)
	time.sleep(0.1)
	ser.close()
	
