import numpy as np
import paho.mqtt.client as mqtt
import cv2
import time
from godsBrain import findTarget, findRobot, motionMonitor, imageGUI

POSITION_ERROR = 5  # positioning error in pixels
fromPico = ""


def on_message(client, userdata, msg):
    global fromPico
    fromPico = msg.payload.decode()
    print("Got message: ", fromPico)


pico = mqtt.Client("itsGod")
pico.connect("10.243.65.201")
pico.on_message = on_message
pico.subscribe("ahoy")

cam = cv2.VideoCapture(0)
time.sleep(3)

state = "start"
target = None
base = None
magnet = None
lastFrame = None


def pos2string(pos):
    if len(pos) == 4:
        return str(pos[0]) + " " + str(pos[1]) + " " + str(pos[2]) + " " + str(pos[3])
    elif len(pos) == 3:
        return str(pos[0]) + " " + str(pos[1]) + " " + str(pos[2])
    elif len(pos) == 2:
        return str(pos[0]) + " " + str(pos[1])


while True:
    _, image = cam.read()
    image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    pico.subscribe("ahoy")

    if fromPico == "Bad message / no data":
        print("Error: MQTT connection is bad")

    target = findTarget(image)
    magnet = findRobot(image)

    if target and magnet[0]:
        # motion = motionMonitor(magnet, lastFrame, image)
        pos = [target[0], target[1], magnet[0], magnet[1]]
        pico.publish("hello", pos2string(pos))
        print("Published Target + Magnet: ", pos2string(pos))
    elif target:
        pos = [target[0], target[1]]
        pico.publish("hello", pos2string(pos))
        print("Published Target: ", pos2string(pos))
    elif magnet[0]:
        pos = ["blank", magnet[0], magnet[1]]
        pico.publish("hello", pos2string(pos))
        print("Published Magnet: ", pos2string(pos))

    niceImg = imageGUI(image, target, base, magnet)
    lastFrame = image

    time.sleep(0.01)

    # Program Termination
    cv2.imshow("GodsEye", niceImg)
    if cv2.waitKey(10) & 0xFF == ord("q"):
        cam.release()
        cv2.destroyAllWindows()
        break
