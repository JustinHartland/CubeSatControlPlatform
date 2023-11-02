#Perform inverted pendulum PID control

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
from InvertedPendulumPID import InvertedPendulumPID
from InvPendDatabase import InvPendDatabase
import sqlite3

#Create instance of database:
invPendPIDDatabase = InvPendDatabase("InvPendIMUatabase.db")

#Add a new trial to the database
trial_id = invPendPIDDatabase.add_trial()
print(f"Added Trial with ID: {trial_id}")

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

#Initialize instance of InvertedPendulumPID
p_constant = 1
i_constant = 0
d_constant = 0
pid_upper_limit = 50
pid_lower_limit = -50

target_angle = 0

PID = InvertedPendulumPID(p_constant, i_constant, d_constant, target_angle, pid_lower_limit, pid_upper_limit)

#Global variables
running = True
odrive_error_detected = False

#Threads
read_angle_thread = threading.Thread(target=PID.read_angle_thread, args=(IMU1,))
set_motor_velocity_thread = threading.Thread(target=PID.set_vel_thread, args=(IMU1.angle_x, node_id, bus,))
print_thread = threading.Thread(target=PID.get_pos_vel_thread, args=(IMU1,))

#Initiate threads
read_angle_thread.start()
set_motor_velocity_thread.start()
print_thread.start()

try:
    while True:
        time.sleep(0.001)

except KeyboardInterrupt:
    running = False
    bus.shutdown()
    print("\nProgram terminated gracefully.")