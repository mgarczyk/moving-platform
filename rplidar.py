from math import floor
from adafruit_rplidar import RPLidar
from paho.mqtt import client as mqtt_client

# Setup the RPLidar
PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(None, PORT_NAME, timeout=3)

# used to scale data to fit on the screen
max_distance = 0
def connect_mqtt(client_id : str, broker : str, port : int ):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client
     
def distances(scan_data):
    Front=scan_data[180]
    print(f'Front: {Front}')   
    Left=scan_data[90]
    print(f'Left: {Left}')
    Right=scan_data[270]
    print(f'Right: {Right}')
    Back=scan_data[0]
    print(f'Back: {Back}')
    return Front, Left, Right, Back

scan_data = [0]*360

if __name__ == '__main__':
    client_id = f'subscribe-test'
    broker = 'localhost'
    port = 1883
    topic = "mqtt/lidar"
    client = connect_mqtt(client_id, broker, port)

    try:
        for scan in lidar.iter_scans():
            for (_, angle, distance) in scan:
                scan_data[min([359, floor(angle)])] = int(distance/10)
            print(scan_data)
            mess=f"{scan_data}"
            client.publish(topic, mess)
            
   
    except KeyboardInterrupt:
        print('Stopping.')
        lidar.stop()
        lidar.disconnect()