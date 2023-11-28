import numpy as np
import paho.mqtt.client as mqtt
import cv2
import time

TARGET_THRESH = 50
ROBOT_THRESH = 100

def findTarget(img):
    # Convert image to HSV color space
    hsvFrame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # HSV Color Threshold
    # BUG needs new BLUE threshold values
    target_lower = np.array([25, 80, 100], np.uint8)
    target_upper = np.array([90, 255, 230], np.uint8)
    target_mask = cv2.inRange(hsvFrame, target_lower, target_upper)

    # Creating contour to track blue color
    contours, hierarchy = cv2.findContours(
        target_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    foundTarget = False
    foundArea = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > foundArea and area > TARGET_THRESH:
            foundTarget = True
            foundArea = area
            x, y, w, h = cv2.boundingRect(contour)
            scene = cv2.drawContours(scene, [contour], 0, (0, 0, 255), 5)

    if foundTarget:
        return [x, y, w, h]
    else:
        return [0]


def findRobot(img, scene):
    # Convert image to HSV color space
    hsvFrame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # HSV Color Threshold
    # BUG needs new GREEN threshold values
    target_lower = np.array([25, 80, 100], np.uint8)
    target_upper = np.array([90, 255, 230], np.uint8)
    target_mask = cv2.inRange(hsvFrame, target_lower, target_upper)

    # Creating contour to track green color
    contours, hierarchy = cv2.findContours(
        target_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    for contour in contours:
        area = cv2.contourArea(contour)

        if area > 100:
            # get number of sides
            approx = cv2.approxPolyDP(
                contour, 0.01 * cv2.arcLength(contour, True), True
            )

            # draw contour of shapes
            scene = cv2.drawContours(scene, [contour], 0, (0, 0, 255), 5)

            # finding center point of shape
            M = cv2.moments(contour)
            if M["m00"] != 0.0:
                x = int(M["m10"] / M["m00"])
                y = int(M["m01"] / M["m00"])

            if len(approx) == 4:
                cv2.putText(
                    img,
                    "Base",
                    (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )
                baseLoc = [x, y]
            elif len(approx) > 6:
                cv2.putText(
                    img,
                    "Magnet",
                    (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )
                magnetLoc = [x, y]

    return img, baseLoc, magnetLoc

def motionMonitor(base,last,now):
    w = 50 # pixel width of robot arm
    exclusion = [base - w,base + w]



cam = cv2.VideoCapture(0)
time.sleep(1)

state = "start"

while True:
    _, image = cam.read()
    image = cv2.flip(image, 1)

    if state == "start":
        # BUG !!! set arm position to be out of the way
        state = "findTarget"
    elif state == "findtarget":
        # BUG check that arm is out of the way
        # if it isnt reset it

        targetLoc = findTarget(image)
        if len(targetLoc) > 1:
            state = "setX"
    elif state == "setX":
        if motionMonitor:
            state = "findtarget"
        else:
            scene, base, magnet = findRobot(image)

            # BUG adjust stepper according to base and target

            # BUG if statement to check if within error allowance
            state = "setY"
    elif state == "setY":
        if motionMonitor:
            state = "findtarget"
        else:
            scene, base, magnet = findRobot(image)

            # BUG adjust stepper according to base and target

            # BUG if statement to check if within error allowance
            state = "retreive"
    elif state == "retreive":
        if motionMonitor:
            state = "findtarget"
        else:
            # BUG run preprogrammed motion to lower and raise magnet
            state = "verify"
    elif state == "verify":
        # BUG get the arm out of the way
        
        # BUG search area of target for blue color
        # if there is blue color below threshold target has been retrieved
        # do something to end program

    # Program Termination
    cv2.imshow("GodsEye", image)
    if cv2.waitKey(10) & 0xFF == ord("q"):
        cam.release()
        cv2.destroyAllWindows()
        break
