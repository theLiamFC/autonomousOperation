import numpy as np
import cv2

TARGET_THRESH = 25
ROBOT_THRESH = 50
MOTION_THRESH = 125


## findTarget()
## Uses color thresholding to find a blue object in the image and return its coordinates
def findTarget(img):
    # Convert image to HSV color space
    hsvFrame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # HSV Blue Color Threshold
    target_lower = np.array([105, 50, 100], np.uint8)
    target_upper = np.array([135, 255, 200], np.uint8)
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

    if foundTarget:
        return [round(x + (0.5 * w)), round(y + (0.5 * h))]
    else:
        return None


## findRobot()
## Uses color thresholding to find a green objects in the image
def findRobot(img):
    # Convert image to HSV color space
    hsvFrame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # HSV Green Color Threshold
    target_lower = np.array([40, 60, 50], np.uint8)
    target_upper = np.array([85, 255, 250], np.uint8)
    target_mask = cv2.inRange(hsvFrame, target_lower, target_upper)

    # Creating contour to track green color
    contours, hierarchy = cv2.findContours(
        target_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    package = [None, None]
    for contour in contours:
        area = cv2.contourArea(contour)

        if area > 200:
            M = cv2.moments(contour)
            if M["m00"] != 0.0:
                x = int(M["m10"] / M["m00"])
                y = int(M["m01"] / M["m00"])
            cv2.putText(
                img,
                "Magnet",
                (x - 25, y - 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )
            package = [round(x), round(y)]

    return package


def imageGUI(img, target=None, base=None, magnet=None):
    if target:
        [x, y] = target
        img = cv2.circle(
            img, center=(int(x), int(y)), radius=15, color=(0, 0, 255), thickness=10
        )
    if base:
        [x, y] = base
        img = cv2.circle(img, center=(x, y), radius=50, color=(0, 255, 0), thickness=10)
    if magnet:
        [x, y] = magnet
        img = cv2.circle(img, center=(x, y), radius=25, color=(0, 255, 0), thickness=10)
    return img
