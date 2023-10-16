import time
from rplidar import RPLidar
from math import floor

lidar = RPLidar("COM11") 
scan_data = [0]*360

try:
    lidar.connect()
    lidar.start_motor()
    time.sleep(2)  # Engine start delay.
    for scan in lidar.iter_scans():
        for (_, angle, distance) in scan:
            scan_data[min([359, floor(angle)])] = int(distance/10)
            print(scan_data)
except KeyboardInterrupt:
    pass
finally:
    lidar.stop()
    lidar.stop_motor()
    lidar.disconnect()
