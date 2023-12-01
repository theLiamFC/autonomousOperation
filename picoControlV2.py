import mqtt
import ArmDrive
import Servo
import time
import network
import myWifi

# Network Information
broker = "10.243.65.201"  # change this as needed
ssid = "Tufts_Wireless"
password = ""
topic_pub = "hello"  # publishing to this topic

# Connect to Wifi
myWifi.connect(myWifi.TUFTS)

# Initialize MQTT Connection
fred = mqtt.MQTTClient("pico", broker, keepalive=600)
fred.connect()
print("Connected and Subscribed")

arm = ArmDrive.ArmDrive(
    pinA=15, pinB=12, pinM=13, pinStep=9, pinDir=8, lenA=10, lenB=10
)

location = ""
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
    global targetHistoryX
    global targetHistoryY

    # BUG if target has been received and is out of view
    # last received target position will be the OG position
    # resulting in false negative

    if not retreived:  # add target value to historical set
        targetHistoryX.append(target[0])
        targetHistoryY.append(target[1])
    else:  # find average from historical set
        avgTargetX = sum(targetHistoryX) / len(targetHistoryX)
        avgTargetY = sum(targetHistoryY) / len(targetHistoryY)

    # compare current target position to historical average
    if abs(target[0] - avgTargetX) < 30 and abs(target[1] - avgTargetY) < 30:
        # reset historical target data in case it was moved
        targetHistoryX = []
        targetHistoryY = []
        return False
    else:
        return True


def whenCalled(topic, msg):
    global message  # Use nonlocal to refer to the location variable in the outer function
    message = msg.decode().split()  # Update the entire location list
    print("Got Message")


## Main Function
def receive_positions():
    # MQTT initiation
    fred.set_callback(whenCalled)
    fred.subscribe(topic_pub)

    # continuous variables outside of loop
    target = []
    magnet = []
    locked = [False, False]
    retreived = False

    # Main Loop
    # Should only exit after target is retreived
    while True:
        # check for messages
        fred.check_msg()

        # reset magnet position
        magnet = []

        # loop while target has not been retrieved
        if not retreived:
            # update data depending on what is received
            if len(message) == 4:  # target and magnet
                print(message[0], message[1])
                target = [int(message[0]), int(message[1])]
                magnet = [int(message[2]), int(message[3])]
            elif len(message) == 3:  # just magnet
                magnet = [int(message[1]), int(message[2])]
            elif len(message) == 2:  # just target
                target = [int(message[0]), int(message[1])]
            else:  # no data
                print("Bad message / no data")
                continue

            # print target and magnet data
            # target should always be available because it is not reset
            # magnet might not be if it was not included in last packet
            print("Target: ", target, " Magnet: ", magnet)

            # check availability of data to proceed with motor control
            # BUG vulnerable to glitch in target data
            # ie if camera vision detects blue somewhere else for a split second
            if len(target) == 0 or len(magnet) == 0:
                continue  # no target or magnet position available
            else:  # proceed with positioning control
                if abs(target[0] - magnet[0]) > 5:  # outside X margin of error
                    locked[0] = False
                    arm.move(
                        arm.xPos + unitStep(target[0], magnet[0], 1, 0.1), arm.yPos, 8
                    )
                else:  # inside X margin of error
                    locked[0] = True
                    print("X Coordinate is Locked")
                if abs(target[1] - magnet[1]) > 5:  # outside Y margin of error
                    locked[1] = False
                    arm.move(
                        arm.yPos + unitStep(target[1], magnet[1], 0.1, 0.05),
                        arm.yPos,
                        8,
                    )
                else:  # inside Y margin of error
                    locked[0] = True
                    print("Y Coordinate is Locked")

            # proceed with retrieval if both X and Y are locked
            if locked[0] and locked[1]:
                print("Retreiving Target")
                arm.move(arm.xPos, arm.yPos, 0)  # down
                time.sleep(0.5)
                arm.move(arm.xPos, arm.yPos, 8)  # up
                time.sleep(0.5)
                arm.move(0, 13, 8)  # get out of cameras way
                retreived = True

        # check if motor retreival sequence has occured
        if retreived:
            # check if camera can verify target has been removed
            if checkTarget(target, retreived):
                retreived = True
                print("Target Succesfully Retreived !!!")
                break
            # if target has not been removed continue with loop
            else:
                retreived = False
                print("Retrieval Attempt Not Succesful :(")


# start program
receive_positions()
