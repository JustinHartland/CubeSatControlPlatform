#Perform inverted pendulum PID control

import time
import threading
import can 
import struct
from TorqueReactionTestThreads import TorqueReactionTestThreads
from TorqueReactionTestDatabase import TorqueReactionTestDatabase

# Define a shared variable or event that threads can check
running = threading.Event()
running.set()  # Set it to true initially

#Create instance of database:
torque_reaction_test_database = TorqueReactionTestDatabase("TorqueReactionTestDatabase.db")

#Add a new trial to the database
trial_id = torque_reaction_test_database.add_trial()
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

#Global variables
odrive_error_detected = False
initialTime = time.time()
torque_setpoint = 0.05


#Request encoder position from ODrive
msg = can.Message(arbitration_id=node_id, data=[0x1C], is_extended_id=False)
bus.send(msg)

#setup threads
threads = TorqueReactionTestThreads()

#Threads
set_motor_torque_thread = threading.Thread(target=threads.set_torque_thread, args=(node_id, bus, torque_setpoint, initialTime, running))
get_torque_estimate = threading.Thread(target=threads.get_system_torque_thread, args=(node_id, bus, running))
add_data_to_database = threading.Thread(target=threads.add_data_to_database, args=('TorqueReactionTestDatabase.db', initialTime, trial_id, running))

#Initiate threads
print("\nTest Active")
set_motor_torque_thread.start()
get_torque_estimate.start()
add_data_to_database.start()

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
    set_motor_torque_thread.join()
    get_torque_estimate.join()
    add_data_to_database.join()

    bus.send(can.Message(arbitration_id=(node_id << 5 | 0x0E), data=struct.pack('<f', 0.0), is_extended_id=False))
    print(f"Successfully set ODrive {node_id} to 0 [Nm]")

    # Shutdown the bus in the finally block to ensure it's always executed
    bus.shutdown()
    print("\nProgram terminated gracefully.")
