# ArmDrive.py
# class to drive a 2dof arm with rotating base
from machine import Pin, PWM, I2C
import Servo
import time
import math
from math import sqrt, acos, atan2, pi,
class ArmDrive:
    def __init__(self, pinA, pinB, pinM, pinStep, pinDir, lenA=60, lenB=60):
        self.lenA = lenA
        self.lenB = lenB
        self.armA = Servo.PositionServo(pin_number=pinA)
        self.armB = Servo.PositionServo(pin_number=pinB)
        self.armM = Servo.PositionServo(pin_number=pinM)
        self.step = Pin(pinStep, Pin.OUT)
        self.dir = Pin(pinDir, Pin.OUT)
        self.xPos = 0
        self.yPos =13
    # function to precisely move the arm in y, z plane
    def move(self, x, y, z):
        self.yPos = y
        # solve for angles
        print("moving stepper: ", self.xPos, "->",x)
        while x != self.xPos:
            if x > self.xPos:
                self.stepLeft()
            elif x < self.xPos:
                self.stepRight()
        try:
            z = -z
            a2 = self.lenA
            a4 = self.lenB
            r1 = sqrt(y**2+z**2)  # eqn 1
            phi_1 = acos((a4**2-a2**2-r1**2)/(-2*a2*r1))  # eqn 2
            phi_2 = atan2(z, y)  # eqn 3
            theta_1 = abs((phi_2-phi_1) * 180/math.pi)  # eqn 4 converted to degrees
            phi_3 = acos((r1**2-a2**2-a4**2)/(-2*a2*a4))
            theta_2 = 180-(phi_3)*180/math.pi
            theta_1 = int(round(theta_1))
            theta_2 = int(round(theta_2))
            if (theta_1 == theta_2 and theta_1 == 0):
                theta_m = 90
            else:
                theta_m = 270 - theta_1 - ((phi_3)*180/math.pi)
            self.armA.set_position(int(theta_1))
            self.armB.set_position(int(theta_2))
            self.armM.set_position(int(theta_m))
            print(theta_1, theta_2, theta_m)
            # update servos
            self.armA.set_position(int(theta_1))
            self.armB.set_position(int(theta_2))
            return 100
        except Exception as e:
            return e
    def moveRaw(self, aAng, bAng, mAng):
        self.armA.set_position(aAng)
        self.armB.set_position(bAng)
        self.armM.set_position(mAng)
    # function to efficiently put the arm into home position
    def getOut(self):
        self.move(self, self.homeY, self.homeT)
    # function to efficiently put the arm into working position
    def goForward(self):
        self.move(self.workX, self.workY, self.workT)
    def stepLeft(self):
        if (self.xPos < 260):
            self.dir.value(1)
            self.step.value(1)
            time.sleep(.003)
            self.step.value(0)
            time.sleep(.003)
            self.xPos += 1
    def stepRight(self):
        if (self.xPos > 0):
            self.dir.value(0)
            self.step.value(1)
            time.sleep(.003)
            self.step.value(0)
            time.sleep(.003)
            self.xPos -= 1


Jordan Berke
  11:01 PM
# ArmDrive.py
# class to drive a 2dof arm with rotating base
from machine import Pin, PWM, I2C
import Servo
import time
import math
from math import sqrt, acos, atan2, pi,
class ArmDrive:
    def __init__(self, pinA, pinB, pinM, pinStep, pinDir, lenA=60, lenB=60):
        self.lenA = lenA
        self.lenB = lenB
        self.armA = Servo.PositionServo(pin_number=pinA)
        self.armB = Servo.PositionServo(pin_number=pinB)
        self.armM = Servo.PositionServo(pin_number=pinM)
        self.step = Pin(pinStep, Pin.OUT)
        self.dir = Pin(pinDir, Pin.OUT)
        self.xPos = 0
        self.yPos = 130
    # function to precisely move the arm in y, z plane
    def move(self, x, y, z):
        #print("moving arm: ", self.yPos, "->",y)
        self.yPos = y
        # solve for angles
#         print("moving stepper: ", self.xPos, "->",x)
        while x != self.xPos:
            if x > self.xPos:
                self.stepLeft()
            elif x < self.xPos:
                self.stepRight()
        try:
            if y >= 0 and y < 190:
                z = -z
                a2 = self.lenA
                a4 = self.lenB
                r1 = sqrt(y**2+z**2)  # eqn 1
                phi_1 = acos((a4**2-a2**2-r1**2)/(-2*a2*r1))  # eqn 2
                phi_2 = atan2(z, y)  # eqn 3
                theta_1 = abs((phi_2-phi_1) * 180/math.pi)  # eqn 4 converted to degrees
                phi_3 = acos((r1**2-a2**2-a4**2)/(-2*a2*a4))
                theta_2 = 180-(phi_3)*180/math.pi
                theta_1 = int(round(theta_1))
                theta_2 = int(round(theta_2))
                if (theta_1 == theta_2 and theta_1 == 0):
                    theta_m = 90
                else:
                    theta_m = 270 - theta_1 - ((phi_3)*180/math.pi)
                self.armA.set_position(int(theta_1))
                self.armB.set_position(int(theta_2))
                self.armM.set_position(int(theta_m))
                print(theta_1, theta_2, theta_m)
                # update servos
                self.armA.set_position(int(theta_1))
                self.armB.set_position(int(theta_2))
                return 100
        except Exception as e:
            return e
    def moveRaw(self, aAng, bAng, mAng):
        self.armA.set_position(aAng)
        self.armB.set_position(bAng)
        self.armM.set_position(mAng)
    # function to efficiently put the arm into home position
    def getOut(self):
        self.move(self, self.homeY, self.homeT)
    # function to efficiently put the arm into working position
    def goForward(self):
        self.move(self.workX, self.workY, self.workT)
    def stepLeft(self):
        if (self.xPos < 270):
            self.dir.value(1)
            self.step.value(1)
            time.sleep(.003)
            self.step.value(0)
            time.sleep(.003)
            self.xPos += 1
    def stepRight(self):
        if (self.xPos > 0):
            self.dir.value(0)
            self.step.value(1)
            time.sleep(.003)
            self.step.value(0)
            time.sleep(.003)
            self.xPos -= 1
11:01
import mqtt
import ArmDrive
import Servo
import time
import network
import myWifi
import asyncio
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
arm = ArmDrive.ArmDrive(
    pinA=15, pinB=12, pinM=13, pinStep=9, pinDir=8, lenA=100, lenB=100
)
location = ""
message = []
targetHistoryX = []
targetHistoryY = []
def unitStep(target, magnet, p):
    difference = abs(magnet - target)
    p = difference * p
    unit = (magnet - target) / difference
    if round(unit * p) < 1:
        return unit*1
    else:
        return round(unit * p)
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
    global message
# Use nonlocal to refer to the location variable in the outer function
    message = msg.decode().split()  # Update the entire location list
    print("Got Message")
## Main Function
async def receive_positions():
    arm.move(0,100,100)
    # continuous variables outside of loop
    target = []
    magnet = []
    locked = [False, False]
    retreived = False
    # Main Loop
    # Should only exit after target is retreived
    while True:
        # check for messages
        #time.sleep(0.75)
        # reset magnet position
        magnet = []
        # loop while target has not been retrieved
        if not retreived:
            # update data depending on what is received
            if len(message) == 4:  # target and magnet
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
            # print target and magnet data
            # target should always be available because it is not reset
            # magnet might not be if it was not included in last packet
            print("Target: ", target, " Magnet: ", magnet)
            # check availability of data to proceed with motor control
            # BUG vulnerable to glitch in target data
            # ie if camera vision detects blue somewhere else for a split second
            if len(target) == 0 or len(magnet) == 0:
                continue  # no target or magnet position available
                await asyncio.sleep_ms(2)
            else:  # proceed with positioning control
                if abs(target[0] - magnet[0]) > 20:  # outside X margin of error
                    locked[0] = False
                    #print("moving x: ", str(arm.xPos + unitStep(target[0], magnet[0], 0.05)))
                    arm.move(
                        arm.xPos + unitStep(target[0], magnet[0], 0.1), arm.yPos, 80
                    )
                    await asyncio.sleep_ms(2)
                else:  # inside X margin of error
                    locked[0] = True
                    print("X Coordinate is Locked")
                    await asyncio.sleep_ms(2)
                if abs(target[1] - magnet[1]) > 30:  # outside Y margin of error
                    locked[1] = False
                    #print("moving y: ", arm.yPos + unitStep(target[1], magnet[1], 0.0005))
                    arm.move(
                        arm.xPos ,
                        arm.yPos + unitStep(target[1], magnet[1], 0.0005),
                        80,
                    )
                    await asyncio.sleep_ms(2)
                else:  # inside Y margin of error
                    locked[1] = True
                    print("Y Coordinate is Locked")
                await asyncio.sleep_ms(2)
            # proceed with retrieval if both X and Y are locked
            if locked[0] and locked[1]:
                print("Retreiving Target")
                arm.move(arm.xPos, arm.yPos, -30)  # down
                time.sleep(0.5)
                arm.move(arm.xPos, arm.yPos, 80)  # up
                time.sleep(0.5)
                arm.move(0, 130, 80)  # get out of cameras way
                retreived = True
                await asyncio.sleep_ms(2)
        # check if motor retreival sequence has occured
        if retreived:
            # check if camera can verify target has been removed
            if checkTarget(target, retreived):
                retreived = True
                print("Target Succesfully Retreived !!!")
                await asyncio.sleep_ms(2)
                break
            # if target has not been removed continue with loop
            else:
                retreived = False
                print("Retrieval Attempt Not Succesful :(")
                await asyncio.sleep_ms(2)
        await asyncio.sleep_ms(2)
async def message_check():
    fred.set_callback(whenCalled)
    fred.subscribe(topic_pub)
    while True:
        # MQTT initiation
        receiving = fred.check_msg()
        await asyncio.sleep_ms(2)
# start program
async def main():
    van = asyncio.get_event_loop()
    van.create_task(receive_positions()) # start first task
    van.create_task(message_check())
    van.run_forever()
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Interrupted')
finally:
    asyncio.new_event_loop()
    print('you are done, clear state')
