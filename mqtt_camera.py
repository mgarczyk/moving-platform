import cv2
import time
import mqtt_pub
import mqtt_sub
client = mqtt_pub.connect_mqtt("rockPi", "localhost", 1883)
camera = cv2.VideoCapture(0)
while True:
    return_value, image = camera.read()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    im_resize = cv2.resize(image, (500,500))
    is_succes, im_buf_arr = cv2.imencode(".jpg", im_resize)
    bytearray_image = im_buf_arr.tobytes()
    cv2.imwrite('camera/opencv.png', image)
    print(bytearray_image)
    mqtt_pub.publish(client, "testtopic/3", bytearray_image)
    time.sleep(5)