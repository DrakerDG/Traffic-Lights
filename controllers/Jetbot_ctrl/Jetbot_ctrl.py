# Jetbot_ctrl controller
# V2.0
#        ____             __             ____  ______
#       / __ \_________ _/ /_____  _____/ __ \/ ____/
#      / / / / ___/ __ `/ //_/ _ \/ ___/ / / / / __  
#     / /_/ / /  / /_/ / ,< /  __/ /  / /_/ / /_/ /  
#    /_____/_/   \__,_/_/|_|\___/_/  /_____/\____/   
#                                                    

# You need to have OpenCV installed in Python; 
# you can use the following command:
# python3 -m pip3 install opencv-python

import cv2                           #  to load the OpenCV library in Python
import numpy as np                   #  to load the NumPy library and assigning it the alias np
from controller import Supervisor    #  to import the Supervisor class

# create the Robot instance
robot = Supervisor()

# Initialize variable to identify the default robot
init = 1
if robot.getName() == 'JetBot 1':
    init = 0                         # default robot

# Get self as robot node
robotNode = robot.getSelf()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# cv2 windows preview --> 1
preview = 1

#  PID keys
Kp = 0.04      # for 20-25 rad/s Max Speed
Ki = 0.08 #0.00004   # for 20-25 rad/s Max Speed
Kd = 0.00004   # for 20-25 rad/s Max Speed

# Initialize PID
I = 0              # Integral Error
D = 0              # Derivative Error 
oldP = 0           # Old Proportional Error

# Initialize max speed motors and velocity robot
maxS = 20          # Max Speed rad/s
maxV = 0           # Max Velocity m/s

# Initialize motors
left_motor = robot.getDevice('left_wheel_hinge')
left_motor.setPosition(float('inf'))
left_motor.setVelocity(0)

right_motor = robot.getDevice('right_wheel_hinge')
right_motor.setPosition(float('inf'))
right_motor.setVelocity(0)

# Initialize camera
camera = robot.getDevice('camera')
camera.enable(timestep)

# Initialize display
main_display = robot.getDevice('main_display')
main_display.attachCamera(camera)
main_display.setColor(0x00FF00)
scale = 2

# Initialize speaker
speaker = robot.getDevice('speaker')
speak = True

# Robot status
RUN = 0
STOP = 1

# Initialize state
state = RUN

# Status and color arrays
status = ["Run", "Stop"]
colors = [(0, 255, 0), (0, 0, 255)]

# Text variables to write to cv2 windows
pos = (55, 50)
font = cv2.FONT_HERSHEY_SIMPLEX
size = 0.8
thickness = 2
line_type = cv2.LINE_AA

# Initialize cv2 windows
if preview == 1:
    cv2.startWindowThread()
    cv2.namedWindow("RGB image", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Road Mask", cv2.WINDOW_NORMAL)
    cv2.moveWindow("RGB image", init*1520, 440)
    cv2.moveWindow("Road Mask", init*1520, 800)

# hour:minutes:seconds.thousandths
def hms(sec):
    h = int(sec // 3600)
    m = int(sec % 3600 // 60)
    s = int(sec % 3600 % 60)
    c = (sec - int(sec)) * 1000
    tm = f'{h:02d}:{m:02d}:{s:02d}.{int(c):03d}'
    return tm

# Video processing to detect the center of the road and the status of the traffic light
def cv2_detect(act_error):
    global state
    global speak
    
    # Capturing a frame from the camera
    screenshot = np.frombuffer(camera.getImage(), dtype=np.uint8).reshape((camera.getHeight(), camera.getWidth(), 4))
    
    # Adjusting the frame size to 160 x 100 pixels
    base_image = cv2.resize(screenshot, (160, 100), fx=0, fy= 0, interpolation = cv2.INTER_CUBIC)
    
    # Obtaining the width and height of the test frame image
    h = base_image.shape[0]
    w = base_image.shape[1]

    # Determining the central reference point xy
    xSet = int(w /2)
    ySet = 84
    
    # Create h x w pixel masks for frame processing
    road_mask = np.zeros((h, w), dtype=np.uint8)
    tral_mask = np.zeros((h, w), dtype=np.uint8)
    all_masks = np.zeros((h, w), dtype=np.uint8)
    
    # Road area of ​​interest
    road_area = np.array([[[  0, 80], [160, 80], [160, 88], [  0, 88]]])
    
    # Traffic light area of ​​interest
    tral_area = np.array([[[ 50,  0], [110,  0], [110, 10], [ 50, 10]]])
    
    # Connecting the two areas of interest (road and traffic light)
    all_areas = np.array([road_area, tral_area])
    
    # Applying the road's area of ​​interest to the road mask
    cv2.fillPoly(road_mask, road_area, 255)
    
    # Applying the area of ​​interest of the traffic light to the traffic light mask
    cv2.fillPoly(tral_mask, tral_area, 255)
    
    # Applying all areas of interest to the consolidated mask
    cv2.fillPoly(all_masks, all_areas, 255)
    
    # Applying the road interest mask to the frame
    road_zone = cv2.bitwise_and(base_image, base_image, mask=road_mask)
    
    # Applying the traffic light interest mask to the frame
    tral_zone = cv2.bitwise_and(base_image, base_image, mask=tral_mask)

    # Applying the compound interest mask to the frame
    all_zones = cv2.bitwise_and(base_image, base_image, mask=all_masks)
    
    # Transforming the masked road frame to HSV format
    road_hsv = cv2.cvtColor(road_zone, cv2.COLOR_BGR2HSV)
    
    # Transforming the masked traffic light frame to HSV format
    tral_hsv = cv2.cvtColor(tral_zone, cv2.COLOR_BGR2HSV)

    # HSV vectors of road brightness and darkness
    road_dark = np.array([110,   0,  20])
    road_bght = np.array([120, 100, 100])
    
    # HSV vectors of brightness and darkness of the red traffic light color
    reds_dark = np.array([174, 125,  20])
    reds_bght = np.array([179, 246, 255])

    # Generating a 6 x 6 filter (kernel) for noise removal processing of the road image of interest
    road_knel = np.ones((6, 6), np.uint8)
    
    # Generating a 10 x 10 filter (kernel) for noise removal processing of the image of interest of the red color of the traffic light
    reds_knel = np.ones((10, 10), np.uint8)
    
    # Processing the target image of the road to remove noise
    road_target = cv2.inRange(road_hsv, road_dark, road_bght)                 # Filtering the road color in HSV format
    road_target = cv2.morphologyEx(road_target, cv2.MORPH_CLOSE, road_knel)   # Applying dilation followed by erosion
    road_target = cv2.morphologyEx(road_target, cv2.MORPH_OPEN, road_knel)    # Applying erosion followed by dilation
    
    # Image processing target of the red traffic light color to remove noise.
    tral_target = cv2.inRange(tral_hsv, reds_dark, reds_bght)                 # # Filtering the red traffic light color in HSV format
    tral_target = cv2.morphologyEx(tral_target, cv2.MORPH_CLOSE, reds_knel)   # Applying dilation followed by erosion
    tral_target = cv2.morphologyEx(tral_target, cv2.MORPH_OPEN, reds_knel)    # Applying erosion followed by dilation

    # Create a copy of the target image of the road
    all_target = road_target.copy()

    try:
        # Search for contours in the previously processed target image of the red traffic light color
        contours0, _ = cv2.findContours(tral_target, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    except:
        # # If it does not detect any red traffic light outline, it sets the status to RUN
        state = RUN
        speak = True
    else:
        try:
            # Determine which is the largest contour detected (if there is more than one)
            largest_contour = max(contours0, key=cv2.contourArea)
        except:
            # If it does not detect any red traffic light outline, it sets the status to RUN
            state = RUN
            if not speak:
                # He speaks, indicating that he continues running.
                speaker.speak('Running again', 1)
                speak = True            
        else:
            # If it detects the red outline of the traffic light, it sets the status to STOP
            state = STOP
            if speak:
                # He speaks, indicating that the light is red and that he is stopping.
                speaker.speak('Red light! I stop', 1)
                speak = False

    # If the status is STOP, draw the outline of the red traffic light color on the consolidated target image
    if state == STOP:
        cv2.drawContours(all_target, contours0, -1, (255, 255, 255), -1)
    
    # Write the status (text) on the image of all areas of interest
    cv2.putText(all_zones, status[state], pos, font, size, colors[state], thickness, line_type)
    
    # Write the status (text) on the consolidated target image
    cv2.putText(all_target, status[state], pos, font, size, (255, 255, 255), thickness, line_type)
        
    # If the preview option is set to 1, it displays the cv2 windows.
    if preview == 1:
        cv2.imshow("RGB image", all_zones)
        cv2.imshow("Road Mask", all_target)
        cv2.waitKey(1)
        
    try:
        # Search for contours in the previously processed target image of the road color
        contours, _ = cv2.findContours(road_target, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    except:
        # If it does not detect any contour, it returns the last detected error value.
        return act_error
    else:
        try:
            # Determine which is the largest contour detected (if there is more than one)
            largest_contour = max(contours, key=cv2.contourArea)
        except:
             # If it does not detect any contour, it returns the last detected error value.
            return act_error
        else:
            try:
                # Determine the location and dimensions of the largest detected outline
                x,y,w,h = cv2.boundingRect(largest_contour)
                
                # Calculate the center of the detected contour
                center_x = int(x + w / 2)
                
                # Clean the display to update the indicators
                main_display.setAlpha(0.0)
                main_display.fillRectangle(0, 0, main_display.width, main_display.height)
                main_display.setAlpha(1.0)
                
                # Convert the 160 x 100 scale to the display scale to draw the indicators
                x0 = int(center_x * scale)
                y0 = int(ySet * scale)
                
                # Draw the road's target icon
                main_display.drawLine(x0 - 15, y0, x0 + 15, y0)
                main_display.drawLine(x0, y0 - 15, x0, y0 + 15)
                main_display.drawOval(x0, y0, 6, 6)
                
                # Draw the target rectangle of the traffic light
                main_display.drawRectangle(100,   0, 120, 20)
                
                # Draw the target rectangle of the road
                main_display.drawRectangle(  0, 160, 320, 16)
                
            except:
                # If it does not detect any contour, it returns the last detected error value.
                return act_error
            else:
                # If it detects a target contour in the target area of ​​the road, 
                # it determines the error by subtracting the center of the contour from the center of the image (shift).
                return xSet - center_x


# Driving robot Module
def drivingModule():
    global I
    global D
    global oldP

    # Calculating the values ​​of P, I, and D
    P = cv2_detect(oldP)
    I = I * (2 / 3) + P * timestep / 1000
    D = D * 0.5 + (P - oldP) / timestep * 1000
    
    # Calculating PID
    PID = Kp * P + Ki * I + Kd * D
    
    # Save the error P
    oldP = P

    # Returns the value of PID
    return PID

# UI Status Print Module
def printStatus():
    global maxV
    
    # Obtaining the robot's velocity vector
    velo = robotNode.getVelocity()
    
    # Calculating the robot's speed
    speed = (velo[0]**2 + velo[1]**2 + velo[2]**2)**0.5
    
    # Update the robot's maximum speed
    if speed > maxV:
        maxV = (speed + maxV) / 2

    # If it is the default robot (JetBot 1), write the timer on the screen (init = 0)
    if init == 0:
        tmr = robot.getTime()
        strP = hms(tmr)
        strP = f'Timer:   {strP:s}'
        robot.setLabel(0, strP, 0, 0.89, 0.06, 0x00FFFF, 0, 'Lucida Console')

    # Calculate the Delta shift for the robot JetBot 2 (init = 1)
    delta = init*0.5
    
    # Write the robot's name and status on the screen
    strP = f'Robot:   {robot.getName():s}   Status: {status[state]:s}'
    robot.setLabel(1, strP, delta, 0.93, 0.06, 0x00FFFF, 0, 'Lucida Console')
    
    # Display the robot's current speed and its maximum speed on the screen
    strP = f'Speed: {speed:7.3f} m/s   Max: {maxV:5.3f} m/s'
    robot.setLabel(2, strP, delta, 0.97, 0.06, 0x00FFFF, 0, 'Lucida Console')

# Main loop:
while robot.step(timestep) != -1:

    # It obtains the error value through the driving module
    error = drivingModule()
   
    # Determine the average speed
    aveS = maxS - abs(error)

    # Determine the angular velocity of the left motor
    left_speed = int(aveS - error)
    
    # Determine the angular velocity of the right motor
    right_speed = int(aveS + error)
    
    # If the status is STOP, set the motor speeds to their corresponding speeds
    if state == RUN:
        left_motor.setVelocity(left_speed)
        right_motor.setVelocity(right_speed)
    
    # If the status is STOP, set the motor speeds to zero
    elif state == STOP:
        left_motor.setVelocity(0)
        right_motor.setVelocity(0)
        
    # Print the status
    printStatus()
    
    pass
