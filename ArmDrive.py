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
