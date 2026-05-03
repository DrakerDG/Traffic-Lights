# traffic_ctrl controller
# V2.0
#        ____             __             ____  ______
#       / __ \_________ _/ /_____  _____/ __ \/ ____/
#      / / / / ___/ __ `/ //_/ _ \/ ___/ / / / / __  
#     / /_/ / /  / /_/ / ,< /  __/ /  / /_/ / /_/ /  
#    /_____/_/   \__,_/_/|_|\___/_/  /_____/\____/   
#                                                    

from controller import Supervisor    #  to import the Supervisor class

# create the Robot instance
robot = Supervisor()

# get the time step of the current world
timestep = int(robot.getBasicTimeStep())

# Initialize leds of traffic lights
red1    = robot.getDevice('led0')
yellow1 = robot.getDevice('led1')
green1  = robot.getDevice('led2')

red2    = robot.getDevice('led3')
yellow2 = robot.getDevice('led4')
green2  = robot.getDevice('led5')

# Initialize speaker
speaker = robot.getDevice('speaker')

# Traffic lights status
GREEN_1 = 0
YELLOW_1 = 1
ALL_RED_1 = 2
GREEN_2 = 3
YELLOW_2 = 4
ALL_RED_2 = 5

# Initial state
state = GREEN_1

# Initial time
state_start_time = robot.getTime()

# Durations in seconds
T_GREEN  = 6
T_YELLOW = 2
T_RED    = 1

# Set the status of the traffic light LEDs
def set_state(r1, y1, g1, r2, y2, g2):
    red1.set(r1); yellow1.set(y1); green1.set(g1)
    red2.set(r2); yellow2.set(y2); green2.set(g2)

# Sound player
def playSnd():
    speaker.playSound(speaker, speaker, 'sounds/beep.wav', 1.0, 1.0, 0.0, False)

# Main loop:
while robot.step(timestep) != -1:
    
    # Updating the timer
    current_time = robot.getTime()
    
    # Updating the elapsed time
    elapsed = current_time - state_start_time

    # If the status is GREEN_1, update the status of the traffic light LEDs
    if state == GREEN_1:
        set_state(0,0,1, 1,0,0)
        
        # If the elapsed time is greater than T_GREEN, it changes state
        if elapsed > T_GREEN:
            state = YELLOW_1
            
            # Update the startup timer
            state_start_time = current_time
            
            # Sound player
            playSnd()

    # If the status is YELLOW_1, update the status of the traffic light LEDs
    elif state == YELLOW_1:
        set_state(0,1,0, 1,0,0)
        
        # If the elapsed time is greater than T_YELLOW, it changes state
        if elapsed > T_YELLOW:
            state = ALL_RED_1
            
            # Update the startup timer
            state_start_time = current_time
            
            # Sound player
            playSnd()

    # If the status is ALL_RED_1, update the status of the traffic light LEDs
    elif state == ALL_RED_1:
        set_state(1,0,0, 1,0,0)
        
        # If the elapsed time is greater than T_RED, it changes state
        if elapsed > T_RED:
            state = GREEN_2
            
            # Update the startup timer
            state_start_time = current_time
            
            # Sound player
            playSnd()

    # If the status is GREEN_2, update the status of the traffic light LEDs
    elif state == GREEN_2:
        set_state(1,0,0, 0,0,1)
        
        # If the elapsed time is greater than T_GREEN, it changes state
        if elapsed > T_GREEN:
            state = YELLOW_2
            
            # Update the startup timer
            state_start_time = current_time
            
            # Sound player
            playSnd()

    # If the status is YELLOW_2, update the status of the traffic light LEDs
    elif state == YELLOW_2:
        set_state(1,0,0, 0,1,0)
        
        # If the elapsed time is greater than T_YELLOW, it changes state
        if elapsed > T_YELLOW:
            state = ALL_RED_2
            
            # Update the startup timer
            state_start_time = current_time
            
            # Sound player
            playSnd()

    # If the status is ALL_RED_2, update the status of the traffic light LEDs
    elif state == ALL_RED_2:
        set_state(1,0,0, 1,0,0)
        
        # If the elapsed time is greater than T_RED, it changes state
        if elapsed > T_RED:
            state = GREEN_1
            
            # Update the startup timer
            state_start_time = current_time
            
            # Sound player
            playSnd()

    #print(int(elapsed))   # <-- to debug
       
    pass
