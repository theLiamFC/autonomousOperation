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
    target_lower = np.array([105, 20, 50], np.uint8)
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
        return [x + (0.5 * w), y + (0.5 * h)]
    else:
        return None


## findRobot()
## Uses color thresholding to find a green objects in the image
## Classifies all green objects by shape and returns the location of
## a circle (magnet) and quadrilateral (base)
def findRobot(img):
    # Convert image to HSV color space
    hsvFrame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # HSV Green Color Threshold
    target_lower = np.array([45, 60, 100], np.uint8)
    target_upper = np.array([85, 255, 230], np.uint8)
    target_mask = cv2.inRange(hsvFrame, target_lower, target_upper)

    # Creating contour to track green color
    contours, hierarchy = cv2.findContours(
        target_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    package = [None, None]
    for contour in contours:
        area = cv2.contourArea(contour)

        if area > 200 and area < 1800:
            M = cv2.moments(contour)
            if M["m00"] != 0.0:
                x = int(M["m10"] / M["m00"])
                y = int(M["m01"] / M["m00"])
            cv2.putText(
                img,
                "Magnet",
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )
            package[1] = [x, y]
        elif area > 1800:
            M = cv2.moments(contour)
            if M["m00"] != 0.0:
                x = int(M["m10"] / M["m00"])
                y = int(M["m01"] / M["m00"])
            cv2.putText(
                img,
                "Base",
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )
            package[0] = [x, y]
            # # get number of sides
            # approx = cv2.approxPolyDP(
            #     contour, 0.01 * cv2.arcLength(contour, True), True
            # )

            # # draw contour of shapes
            # # scene = cv2.drawContours(scene, [contour], 0, (0, 0, 255), 5)

            # # finding center point of shape
            # M = cv2.moments(contour)
            # if M["m00"] != 0.0:
            #     x = int(M["m10"] / M["m00"])
            #     y = int(M["m01"] / M["m00"])

            # if len(approx) <= 6:
            #     cv2.putText(
            #         img,
            #         "Base",
            #         (x, y),
            #         cv2.FONT_HERSHEY_SIMPLEX,
            #         0.6,
            #         (255, 255, 255),
            #         2,
            #     )
            #     package[0] = [x, y]
            # elif len(approx) > 6:
            #     cv2.putText(
            #         img,
            #         "Magnet",
            #         (x, y),
            #         cv2.FONT_HERSHEY_SIMPLEX,
            #         0.6,
            #         (255, 255, 255),
            #         2,
            #     )
            #     package[1] = [x, y]

    return package


## motionMonitor()
## Detects motion between two images excluding the area that the robot arm occupies
## Returns True if there is motion and False if there is no motion
def motionMonitor(base, last, now):
    armWidth = 150  # pixel width of robot arm
    # BUG adjust exclusion zone experimentally
    exclusion = [base[0] - armWidth, base[0] + armWidth]

    # convert to greyscale and blur images
    current_frame = cv2.cvtColor(now, cv2.COLOR_BGR2GRAY)
    current_frame = cv2.GaussianBlur(src=current_frame, ksize=(5, 5), sigmaX=0)
    previous_frame = cv2.cvtColor(last, cv2.COLOR_BGR2GRAY)
    previous_frame = cv2.GaussianBlur(src=previous_frame, ksize=(5, 5), sigmaX=0)

    # calculate difference
    diff_frame = cv2.absdiff(src1=previous_frame, src2=current_frame)

    # dilute the image a bit to make differences more seeable; more suitable for contour detection
    kernel = np.ones((5, 5))
    diff_frame = cv2.dilate(diff_frame, kernel, 1)

    # threshold differences
    thresh_frame = cv2.threshold(
        src=diff_frame, thresh=20, maxval=255, type=cv2.THRESH_BINARY
    )[1]

    # find contours of motion
    contours, _ = cv2.findContours(
        image=thresh_frame, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE
    )

    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        # filter contours for size and arm motion
        if cv2.contourArea(contour) > MOTION_THRESH and (
            (x + (0.5 * w) < exclusion[0]) or (x + (0.5 * w) > exclusion[1])
        ):
            return True
    return False


def imageGUI(img, target=None, base=None, magnet=None):
    if target:
        [x, y] = target
        img = cv2.circle(
            img, center=(int(x), int(y)), radius=15, color=(255, 0, 0), thickness=10
        )
    if base:
        [x, y] = base
        img = cv2.circle(img, center=(x, y), radius=50, color=(255, 0, 0), thickness=10)
    if magnet:
        [x, y] = magnet
        img = cv2.circle(img, center=(x, y), radius=25, color=(255, 0, 0), thickness=10)
    return img
