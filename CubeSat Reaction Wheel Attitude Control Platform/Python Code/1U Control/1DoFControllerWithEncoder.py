#Programmer: Justin Hartland
#Purpose: Produce a P controller between encoder angle data and reaction wheel motor

import threading 
import can
import time
import struct
from as5048b import as5048b
from motor_controller import motor_controller

# Define a shared variable or event that threads can check
running = threading.Event()
running.set()  # Set it to true initially

#---------------------------------------------------------------------------------------
#ODrive Setup
#---------------------------------------------------------------------------------------

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

#---------------------------------------------------------------------------------------
#Attitude Determination Setup
#---------------------------------------------------------------------------------------
        
#Initialize instance of as5048b
encoder = as5048b()

#---------------------------------------------------------------------------------------
#PID Controller Setup
#---------------------------------------------------------------------------------------

#Initialize PID parameters
p = 0.5
i = 0
d = 0

#Initialize upper and lower torque output limits
torque_upper_limit = 0.63
torque_lower_limit = -0.63

#Initialize angle setpoint
angle_setpoint = 0

#Create instance of motor_controller
pid = motor_controller(p, i, d, angle_setpoint,  torque_lower_limit, torque_upper_limit)

#---------------------------------------------------------------------------------------
#Controller Start
#---------------------------------------------------------------------------------------

print('Controller beginning in:\n\n')
time_remaining = 5

while (time_remaining != 0):
    print(f"{time_remaining} s")
    time_remaining = time_remaining - 1
    time.sleep(1)

#Defining threads
read_angle_thread = threading.Thread(target=encoder.read_angle, args=())
set_motor_torque_thread = threading.Thread(target=pid.set_torque, args=(encoder, node_id, bus, running))

#Initiate threads
print("\nPID Active")
read_angle_thread.start()
set_motor_torque_thread.start()

#---------------------------------------------------------------------------------------
#Controller Shutdown
#---------------------------------------------------------------------------------------

#Shutdown can bus upon ctrl+c
try:
    while True:
        time.sleep(0.001)

except KeyboardInterrupt:
    # Signal threads to stop
    running.clear()

    print("\nThreads cleared!")

finally:
    # Wait for the threads to stop
    read_angle_thread.join()
    set_motor_torque_thread.join()

    bus.send(can.Message(arbitration_id=(node_id << 5 | 0x0E), data=struct.pack('<f', 0.0), is_extended_id=False))
    print(f"Successfully set ODrive {node_id} to 0 [Nm]")

    # Shutdown the bus in the finally block to ensure it's always executed
    bus.shutdown()
    print("\nProgram terminated gracefully.")