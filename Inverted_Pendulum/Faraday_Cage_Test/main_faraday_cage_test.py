#Perform inverted pendulum PID control

import time
import threading
import can 
import struct
from InertialMeasurementUnit import InertialMeasurementUnit
from Faraday_Cage_Test_Threads import Faraday_Cage_Test_Threads
from Faraday_Cage_Test_Database import Faraday_Cage_Test_Database

# Define a shared variable or event that threads can check
running = threading.Event()
running.set()  # Set it to true initially

#Create instance of database:
faraday_cage_test_database = Faraday_Cage_Test_Database("Faraday_Cage_Test_Database.db")

#Add a new trial to the database
trial_id = faraday_cage_test_database.add_trial()
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
threads = Faraday_Cage_Test_Threads()

#Global variables
odrive_error_detected = False
initialTime = time.time()
velocity_setpoint = 5

#Threads
read_angle_thread = threading.Thread(target=threads.read_angle_thread, args=(IMU1, running, ))
set_velocity_thread = threading.Thread(target = threads.set_vel_thread, args=(node_id, bus, velocity_setpoint, running, ))
#get_encoder_vel_thread = threading.Thread(target = threads.get_vel_thread, args=(node_id, bus, running, ))
add_data_to_database = threading.Thread(target=threads.add_data_to_database, args=(IMU1, 'Faraday_Cage_Test_Database.db', initialTime, trial_id, velocity_setpoint, running, ))

#Initiate threads
print("\Test Active")
read_angle_thread.start()
set_velocity_thread.start()
#get_encoder_vel_thread.start()
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
    read_angle_thread.join()
    set_velocity_thread.join()
    #get_encoder_vel_thread.join()
    add_data_to_database.join()

    bus.send(can.Message(arbitration_id=(node_id << 5 | 0x0d), data=struct.pack('<ff', float(0), 0.0), is_extended_id=False))
    print(f"Successfully set ODrive {node_id} to 0 [rev/s]")

    # Shutdown the bus in the finally block to ensure it's always executed
    bus.shutdown()
    print("\nProgram terminated gracefully.")
