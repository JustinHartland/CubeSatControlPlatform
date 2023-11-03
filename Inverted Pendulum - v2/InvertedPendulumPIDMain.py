#Perform inverted pendulum PID control

import time
import threading
import can 
import struct
from simple_pid import PID
from InertialMeasurementUnit import InertialMeasurementUnit
from InvertedPendulumPID import InvertedPendulumPID
from InvPendDatabase import InvPendDatabase

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
p_constant = -0.5
i_constant = 0
d_constant = 0

#Torque upper and lower limits (50% of O-Drive)
pid_upper_limit = 0.63
pid_lower_limit = -0.63
target_angle = 0

pid = InvertedPendulumPID(p_constant, i_constant, d_constant, target_angle, pid_lower_limit, pid_upper_limit)

#Global variables
odrive_error_detected = False
running = True

#Threads
read_angle_thread = threading.Thread(target=pid.read_angle_thread, args=(IMU1, running, ))
set_motor_torque_thread = threading.Thread(target=pid.set_torque_thread, args=(IMU1, node_id, bus, running, ))
#print_thread = threading.Thread(target=pid.get_pos_vel_thread, args=(IMU1, node_id, bus, running, ))

#Initiate threads
read_angle_thread.start()
set_motor_torque_thread.start()
#print_thread.start()

#Shutdown can bus upon ctrl+c
try:
    while True:
        time.sleep(0.001)

except KeyboardInterrupt:
    running = False
    bus.shutdown()
    print("\nProgram terminated gracefully.")