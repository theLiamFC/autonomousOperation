import mqtt
import ArmDrive
import Servo
import time
import network

arm = ArmDrive.ArmDrive(
    pinA=15, pinB=12, pinM=13, pinStep=9, pinDir=8, lenA=10, lenB=10
)

broker = "10.243.65.201"  # change this as needed
ssid = "Tufts_Wireless"
password = ""
topic_pub = "hello"  # publishing to this topic
# topic_sub = "Pico/listen" #in case 2-way communication, subscribe to the topic that the other device is publishing to
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
while wlan.isconnected() == False:
    print("Waiting for connection...")
    time.sleep(1)
print("Connected to WiFi")
fred = mqtt.MQTTClient("pico", broker, keepalive=600)
fred.connect()
print("Connected and Subscribed")

location = ""
updown = False
message = []
targetHistoryX = []
targetHistoryY = []


def unitStep(target, magnet, step, p):
    p = abs(target - magnet) * p
    if target - magnet != 0:
        unit = (target - magnet) / abs(target - magnet)
        print("in unitstep", unit)
        if round(unit * step * p) < 1:
            return 1
        return unit * step * p
    else:
        return 0


def checkTarget(target, retreived):
    global targetHistory

    # BUG if target has been received and is out of view
    # last received target position will be the OG position
    # resulting in false negative

    if not retreived:
        targetHistoryX.append(target[0])
        targetHistoryY.append(target[1])
    else:
        avgTargetX = sum(targetHistoryX) / len(targetHistoryX)
        avgTargetY = sum(targetHistoryY) / len(targetHistoryY)

    if abs(target[0] - avgTargetX) < 30 and abs(target[1] - avgTargetY) < 30:
        retreived = False
        return False
    else:
        retreived = True
        return True


def whenCalled(topic, msg):
    global message  # Use nonlocal to refer to the location variable in the outer function
    print(f"topic {topic} received message {msg}")
    message = msg.decode().split()  # Update the entire location list
    print(message)


## Receive positioning from MQTT
def receive_positions():
    global updown
    global message  # Use nonlocal to refer to the location variable in the outer function

    target = []
    magnet = []
    locked = [False, False]
    retreived = False

    while True:
        fred.set_callback(whenCalled)
        fred.subscribe(topic_pub)
        fred.check_msg()

        magnet = []

        if not retreived:
            # update data
            if len(message) == 4:  # target and magnet
                print(message[0], message[1])
                target = [int(message[0]), int(message[1])]
                magnet = [int(message[2]), int(message[3])]
            elif len(message) == 3:  # just magnet
                magnet = [int(message[1]), int(message[2])]
            elif len(message) == 2:  # just target
                target = [int(message[0]), int(message[1])]
            else:
                print("Bad message / no data")
                continue

            print("Target: ", target, " Magnet: ", magnet)

            # check availability of data to proceed with motor control
            # BUG vulnerable to glitch in target data
            # ie if camera vision detects blue somewhere else for a split second
            if len(target) == 0:  # no target position received ever
                continue
            elif len(magnet) == 0:  # no magnet position received in last message
                continue
            else:
                if abs(target[0] - magnet[0]) > 5:  # X margin of error
                    locked[0] = False
                    arm.move(
                        arm.xPos + unitStep(target[0], magnet[0], 1, 0.5), arm.yPos, 8
                    )
                else:
                    locked[0] = True
                    print("X Coordinate is Locked")
                if abs(target[1] - magnet[1]) > 5:  # Y margin of error
                    locked[1] = False
                    arm.move(
                        arm.yPos + unitStep(target[1], magnet[1], 0.1, 0.05),
                        arm.yPos,
                        8,
                    )
                else:
                    locked[0] = True
                    print("Y Coordinate is Locked")

            if locked[0] and locked[1]:
                print("Retreiving Target")
                arm.move(arm.xPos, arm.yPos, 0)
                time.sleep(0.5)
                arm.move(arm.xPos, arm.yPos, 8)
                time.sleep(0.5)
                arm.move(0, 13, 8)
                retreived = True
        elif checkTarget(target, retreived):
            print("Target Succesfully Retreived !!!")
            break
        else:
            print("Retrieval Attempt Not Succesful :(")


receive_positions()
