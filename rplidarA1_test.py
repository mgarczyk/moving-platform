import os
from math import floor
from adafruit_rplidar import RPLidar
import time

# Setup the RPLidar
PORT_NAME = 'COM3'
lidar = RPLidar(None, PORT_NAME, timeout=3)

# used to scale data to fit on the screen
max_distance = 0

def process_data(data):
    print(data)

scan_data = [0]*360

try:
    lidar.start_motor()
    for scan in lidar.iter_scans():
        for (_, angle, distance) in scan:
            scan_data[min([359, floor(angle)])] = distance
        process_data(scan_data)
        with open('lidar_data/data.txt','a') as file:
            file.write(str(scan_data)+'\n')

except KeyboardInterrupt:
    lidar.stop_motor()
    time.sleep(1)
    print('Stopped.')
lidar.stop()
lidar.disconnect()