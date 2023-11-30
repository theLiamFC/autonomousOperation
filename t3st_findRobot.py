import cv2
import time
from godsBrain import findRobot

cam = cv2.VideoCapture(0)
time.sleep(3)

while True:
    _, image = cam.read()
    image = cv2.flip(image, 1)

    package = findRobot(image)
    print(package)
    # if len(package) > 1:
    #     [x, y, w, h] = targetLoc
    #     image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 5)

    cv2.imshow("GodsEye", image)
    if cv2.waitKey(10) & 0xFF == ord("q"):
        cam.release()
        cv2.destroyAllWindows()
        break
