# autonomousOperation
<h1>Autonomous Operation Robot</h1>
<h2>Project Overview</h2>
This project involves the creation of a robotic system capable of playing the game Operation. The robot is equipped with three degrees of freedom controlled by a combination of a stepper motor and two servos. The system operates autonomously using computer vision with the OpenCV library. The project is divided into several files, each of which are described below.

<h2>File Descriptions</h2>
1. godsBrain.py
This file contains a collection of functions responsible for image processing. It is a crucial component as it processes visual data obtained by the robot's camera to identify and analyze the game board, specifically targeting the end effector and the game piece that needs to be removed.

Functions Include:

findTarget(img)
findRobot(img)
imageGUI(img, target, robot)

2. godsEye.py
This file initiates the camera system and facilitates the communication of image processing data to a Raspberry Pi Pico using MQTT (Message Queuing Telemetry Transport). It serves as the bridge between the visual perception (godsBrain.py) and the motor control logic on the Pico.

3. ArmDrive.py
This file, residing on the Raspberry Pi Pico, encapsulates the motor and servo control logic. It contains a class that coordinates the movements of the robotic arm's three degrees of freedom based on the input received from godsEye.py. The class utilizes the stepper motor for linear movement and two servos for 2-DOF arm control. It also adjusts the end effector so it is always vertical.

Class features:

ArmDrive.init(pinA, pinB, pinM, pinStep, pinDir, lenA, lenB)
ArmDrive.move(x,y,z)
ArmDrive.moveRaw(angA, angB, angM)

4. picoControl.py
This file on the Raspberry Pi Pico receives data from godsEye.py over MQTT and implements a proportional controller along with logic to determine the optimal movements for the robotic arm. It acts as the brain of the system, making decisions based on the visual input to successfully execute the task of removing and verifying the removal of the game piece. The logic is based on a state machine and uses Asyncio to check for new MQTT messages while the arm is in movement.

Key functionalities:

MQTT data reception from godsEye.py
Proportional controller implementation
Decision-making logic for optimal arm movements
Verification of game piece removal
