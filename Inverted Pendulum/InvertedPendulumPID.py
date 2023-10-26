import time
import board
import adafruit_lsm9ds1
import odrive
import math
import threading
import can 
import struct
from simple_pid import PID
from InertialMeasurementUnit import InertialMeasurementUnit

#Set motor to v = velocity
def set_vel():
    global running
    while running:
        velocity = pid(IMU1.angle_x)
        bus.send(can.Message(arbitration_id=(node_id << 5 | 0x0d), data=struct.pack('<ff', float(velocity), 0.0), is_extended_id=False))
        time.sleep(0.01)

def read_angle(imu_obj):
    global running
    while running:
        imu_obj.get_euler_angles()
        time.sleep(0.01)

def get_pos_vel(imu_obj):
    while running:
        for msg in bus:
            if msg.arbitration_id == (node_id << 5 | 0x09):
                pos, vel = struct.unpack('<ff', bytes(msg.data))
                print(f"Roll: {imu_obj.angle_x:.2f} degrees, vel: {vel:.3f} [turns/s]")

def monitor_odrive_status():
    global running, odrive_error_detected

    # Replace with the appropriate CAN ID for requesting status
    STATUS_REQUEST_ID = (node_id << 5 | 0x03) 

    # Replace with the appropriate CAN ID for receiving status
    STATUS_REPLY_ID = (node_id << 5 | 0x03) 

    while running:
        # Send a status request to the ODrive
        bus.send(can.Message(arbitration_id=STATUS_REQUEST_ID, is_extended_id=False))

        # Wait for a reply
        start_time = time.time()
        timeout = 1  # Adjust timeout as needed
        while time.time() - start_time < timeout:
            msg = bus.recv(timeout=timeout)
            if msg and msg.arbitration_id == STATUS_REPLY_ID:
                # Decode the status message. This is a placeholder. You'll need to update the unpacking logic.
                status = struct.unpack('<I', bytes(msg.data[:4]))[0]

                # Check for an error (replace with actual error check logic)
                if status != 0:  # assuming non-zero means error
                    print(f"ODrive error detected: {status}")
                    odrive_error_detected = True
                    running = False
                    break

        time.sleep(1)  # Adjust the sleep duration as needed

# Function to set the maximum RPM of the ODrive
def set_max_rpm(rps):
    # Replace with the correct CAN ID for setting max RPM
    MAX_RPS_SET_ID = (node_id << 5 | 0x0f) 

    # Send a command to set the max RPM
    # This is a placeholder. You'll need to update the packing logic.
    data = struct.pack('<I', int(rps * 60))  # Converting RPS to RPM
    bus.send(can.Message(arbitration_id=MAX_RPS_SET_ID, data=data, is_extended_id=False))


#CAN initialization
node_id = 0
bus = can.interface.Bus("can0", bustype="socketcan")

while not (bus.recv(timeout=0) is None): pass
bus.send(can.Message(arbitration_id=(node_id << 5 | 0x07), data=struct.pack('<I', 8), is_extended_id=False))

start_time = time.time()
timeout = 10  # seconds

for msg in bus:
    if time.time() - start_time > timeout:
        print("Timeout waiting for the expected CAN message.")
        break

    if msg.arbitration_id == (node_id << 5 | 0x01):
        error, state, result, traj_done = struct.unpack('<IBBB', bytes(msg.data[:7]))
        if state == 8:
            break

#Initialize instance of InertialMeasurementUnit
IMU1 = InertialMeasurementUnit()

#Setup PID controller
set_point = 0 #Pendulum upright
pid = PID(0.5, 0, 0, setpoint=set_point)
pid.output_limits = (-50, 50) #RPS bounds on motor

#Global variables
running = True
odrive_error_detected = False

# Set the maximum RPM of the ODrive to 50 RPS (3000 RPM)
set_max_rpm(50)

# Threads
imu_thread = threading.Thread(target=read_angle, args=(IMU1,))
motor_thread = threading.Thread(target=set_vel)
pos_thread = threading.Thread(target=get_pos_vel, args=(IMU1,))
status_thread = threading.Thread(target=monitor_odrive_status)

imu_thread.start()
motor_thread.start()
pos_thread.start()
status_thread.start()

try:
    while True:
        time.sleep(0.001)

except KeyboardInterrupt:
    running = False
    bus.shutdown()
    print("\nProgram terminated gracefully.")