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
targetx = 0
targety = 0
message = []


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


## Receive positioning from MQTT
def receive_positions():
    global updown
    global targetx
    global targety
    global message  # Use nonlocal to refer to the location variable in the outer function

    def whenCalled(topic, msg):
        global message  # Use nonlocal to refer to the location variable in the outer function
        print(f"topic {topic} received message {msg}")
        message = msg.decode().split()  # Update the entire location list
        print(message)

    while True:
        fred.set_callback(whenCalled)
        fred.subscribe(topic_pub)
        fred.check_msg()

        # Do something with the location list if needed
        print("Current location:", message)
        print(len(message))
        if len(message) != 0:
            print("attempting to move")

            if len(message) == 4 and updown == False:
                print("befroe")
                print(
                    str(arm.xPos + unitStep(targetx, int(message[2]), 1, 50)),
                    str(arm.yPos + unitStep(targety, int(message[3]), 0.2, 5)),
                    str(8),
                )
                arm.move(
                    arm.xPos + unitStep(targetx, int(message[2]), 1, 50),
                    arm.yPos + unitStep(targety, int(message[3]), 0.2, 5),
                    8,
                )
                print("after")
            elif len(message) == 4 and updown == True:
                arm.move(0, 13, 8)

            elif len(message) == 3 and updown == False:
                if abs(targetx - int(message[1])) > 5:
                    arm.move(
                        arm.xPos + unitStep(targetx, int(message[1]), 1, 0.5),
                        arm.yPos,
                        8,
                    )

                if abs(targety - int(message[2])) > 5:
                    arm.move(
                        arm.xpos,
                        arm.yPos + unitStep(targety, int(message[2]), 0.2, 0.05),
                        8,
                    )

                if (abs(targetx - int(message[1])) <= 5) and (
                    abs(targety - int(message[2])) <= 5
                ):
                    arm.move(
                        arm.xPos,
                        arm.yPos + unitStep(targety, int(message[2]), 0.2, 0.05),
                        0,
                    )
                    time.sleep(0.5)
                    updown = True

            elif len(message) == 3 and updown == True:
                arm.move(0, 13, 8)

            elif len(message) == 2:
                print("we here")
                targetx = int(message[0])
                targety = int(message[1])
                arm.move(0, 13, 8)

            elif message[0] == "help":
                arm.move(220, 14, -5)
                time.sleep(0.75)
                arm.move(arm.xPos, 10, 10)
                time.sleep(0.75)
                arm.move(0, 0, 20)

        else:
            print("Fuck were here")

    return location


while True:
    receive_positions()
