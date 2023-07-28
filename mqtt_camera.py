import cv2
import time
import mqtt_pub
import mqtt_sub
import logging
client = mqtt_pub.connect_mqtt("rockPi", "localhost", 1883)
camera = cv2.VideoCapture(0)
while True: 
    try:
        return_value, image = camera.read()
        if image is None:
            raise ValueError
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        im_resize = cv2.resize(image, (500,500))
        is_succes, im_buf_arr = cv2.imencode(".jpg", im_resize)
        bytearray_image = im_buf_arr.tobytes()
        cv2.imwrite('camera/opencv.png', image)
        print(bytearray_image)
        mqtt_pub.publish(client, "camera/photo", bytearray_image)
    except ValueError:
            logging.error("CAMERA MQTT: There is no camera detected on /dev/USB0")    
    time.sleep(5)