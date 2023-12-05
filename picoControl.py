import mqtt
import ArmDrive
import Servo
import time
import network
import myWifi
import asyncio

CONTROL_THRESHOLD = 20

# Network Information
broker = "10.243.65.201"  # change this as needed
ssid = "Tufts_Wireless"
password = ""
topic_pub = "hello"  # publishing to this topic

# Connect to Wifi
myWifi.connect(myWifi.TUFTS)

# Initialize MQTT Connection
fred = mqtt.MQTTClient("itspico", broker, keepalive=600)
fred.connect()
print("Connected and Subscribed")

# global variables / classes
arm = ArmDrive.ArmDrive(
    pinA=15, pinB=12, pinM=13, pinStep=9, pinDir=8, lenA=10, lenB=10
)
message = []
targetHistoryY = []


# function to convert pixel distance to physical step
# uses proportional controller constant p
def unitStep(target, magnet, p):
    difference = abs(magnet - target)
    p = difference * p
    print("Differnce: ", difference)
    if difference > CONTROL_THRESHOLD:
        unit = (magnet - target) / difference
        print("in unitstep", unit)
        if round(unit * p) < 1:
            return 1
        else:
            return round(unit * p)
    else:
        return 0


# verifies that target has been removed from original position
def checkTarget(target, retrieved):
    global targetHistoryY

    if not retrieved:  # add target value to historical set
        targetHistoryY.append(target[1])
    else:  # find average from historical set
        avgTargetY = sum(targetHistoryY) / len(targetHistoryY)
    # compare current target position to historical average
    if abs(target[1] - avgTargetY) < 30:
        # reset historical target data in case it was moved
        targetHistoryY = []
        return False
    else:
        return True


# mqtt callback
def whenCalled(topic, msg):
    global message
    # Use nonlocal to refer to the location variable in the outer function
    message = msg.decode().split()  # Update the entire location list
    print("Got Message")


## Main loop
async def receive_positions():
    # continuous variables outside of loop
    target = []
    magnet = []
    locked = [False, False]
    retrieved = False

    # Main Loop
    # Should only exit after target is retrieved
    while True:
        # reset magnet position
        magnet = []

        # loop while target has not been retrieved
        if not retrieved:
            # update data depending on what is received
            if len(message) == 4:  # target and magnet
                print("x,y target = ", message[0], message[1])
                target = [int(message[0]), int(message[1])]
                magnet = [int(message[2]), int(message[3])]
                await asyncio.sleep_ms(2)
            elif len(message) == 3:  # just magnet
                magnet = [int(message[1]), int(message[2])]
                await asyncio.sleep_ms(2)
            elif len(message) == 2:  # just target
                target = [int(message[0]), int(message[1])]
                await asyncio.sleep_ms(2)
            else:  # no data
                print("Bad message / no data")
                await asyncio.sleep_ms(2)
                continue

            # check if data is available
            if len(target) == 0 or len(magnet) == 0:
                continue  # no target or magnet position available
                await asyncio.sleep_ms(2)
            else:  # proceed with positioning control
                if (
                    abs(target[0] - magnet[0]) > CONTROL_THRESHOLD
                ):  # outside X margin of error
                    locked[0] = False
                    print(
                        "moving x: ",
                        str(arm.xPos + unitStep(target[0], magnet[0], 0.01)),
                    )
                    arm.move(
                        arm.xPos + unitStep(target[0], magnet[0], 0.1), arm.yPos, 8
                    )
                    await asyncio.sleep_ms(2)
                else:  # inside X margin of error
                    locked[0] = True
                    print("X Coordinate is Locked")
                if (
                    abs(target[1] - magnet[1]) > CONTROL_THRESHOLD
                ):  # outside Y margin of error
                    locked[1] = False
                    print("moving y")
                    arm.move(
                        arm.yPos,
                        arm.yPos + unitStep(target[1], magnet[1], 0.05),
                        8,
                    )
                else:  # inside Y margin of error
                    locked[0] = True
                    print("Y Coordinate is Locked")
                await asyncio.sleep_ms(2)

            # proceed with retrieval if both X and Y are locked
            if locked[0] and locked[1]:
                print("Retrieving Target")
                arm.move(arm.xPos, arm.yPos, 0)  # down
                time.sleep(0.5)
                arm.move(arm.xPos, arm.yPos, 8)  # up
                time.sleep(0.5)
                arm.move(0, 13, 8)  # get out of cameras way
                retrieved = True
                await asyncio.sleep_ms(2)

        # check if motor retrieval sequence has occured
        if retrieved:
            # check if camera can verify target has been removed
            if checkTarget(target, retrieved):
                retrieved = True
                print("Target Succesfully Retrieved !!!")
                await asyncio.sleep_ms(2)
                break
            # if target has not been removed continue with loop
            else:
                retrieved = False
                print("Retrieval Attempt Not Succesful :(")
                await asyncio.sleep_ms(2)
        await asyncio.sleep_ms(2)


# constantly check for messages
async def message_check():
    fred.set_callback(whenCalled)
    fred.subscribe(topic_pub)
    while True:
        # MQTT initiation
        receiving = fred.check_msg()
        print("received message is ", receiving)
        await asyncio.sleep_ms(1)


# start program
async def main():
    van = asyncio.get_event_loop()
    van.create_task(receive_positions())  # start first task
    van.create_task(message_check())
    van.run_forever()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Interrupted")
finally:
    asyncio.new_event_loop()
    print("you are done, clear state")
