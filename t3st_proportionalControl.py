import cv2
import time
import paho.mqtt.client as mqtt
from godsBrain import findTarget, findRobot, motionMonitor, imageGUI

fromPico = ""


def on_message(client, userdata, msg):
    global fromPico
    fromPico = msg.payload.decode()
    print("Got message: ", fromPico)


def pos2string(pos):
    if len(pos) == 4:
        return str(pos[0]) + " " + str(pos[1]) + " " + str(pos[2]) + " " + str(pos[3])
    elif len(pos) == 3:
        return str(pos[0]) + " " + str(pos[1]) + " " + str(pos[2])
    elif len(pos) == 2:
        return str(pos[0]) + " " + str(pos[1])


pico = mqtt.Client("itsGod")
pico.connect("10.243.65.201")
pico.on_message = on_message
pico.subscribe("ahoy")

cam = cv2.VideoCapture(0)
time.sleep(3)

while True:
    _, image = cam.read()
    image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    pico.subscribe("ahoy")

    if fromPico == "bad message":
        print("Error: MQTT connection is bad")

    target = [600, 600]
    [base, magnet] = findRobot(image)

    if target and magnet:
        pos = [target[0], target[1], magnet[0], magnet[1]]
        pico.publish("hello", pos2string(pos))
        print("Published Target + Magnet: ", pos2string(pos))
    elif target:
        pos = [target[0], target[1]]
        pico.publish("hello", pos2string(pos))
        print("Published Target: ", pos2string(pos))
    elif magnet:
        pos = ["blank", magnet[0], magnet[1]]
        pico.publish("hello", pos2string(pos))
        print("Published Magnet: ", pos2string(pos))

    niceImg = imageGUI(image, target, base, magnet)
    lastFrame = image

    cv2.imshow("GodsEye", image)
    if cv2.waitKey(10) & 0xFF == ord("q"):
        cam.release()
        cv2.destroyAllWindows()
        break
