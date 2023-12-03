#Purpose: define threads needed to test torque reaction times

import struct
import time
import can
import sqlite3

class TorqueReactionTestThreads:
    def __init__(self):
        self.torque_setpoint = 0
        self.torque_estimate = 0

        self.torque_setpoint_array = []
        self.torque_estimate_array = []
        self.time_array = []

    # Function to set torque for a specific O-Drive
    def set_torque_thread(self, node_id, bus, torque_setpoint, initial_time, running):
        while running.is_set():

            #Set torque = 0 for first 5 seconds
            if (time.time() - initial_time) < 5:
                bus.send(can.Message(
                    arbitration_id=(node_id << 5 | 0x0E),  # 0x0E: Set_Input_Torque
                    data=struct.pack('<f', 0),
                    is_extended_id=False
                ))

            #Set torque = torque_setpoint after 5 seconds
            if (time.time() - initial_time) >= 5 and (time.time() - initial_time) < 7:
                bus.send(can.Message(
                    arbitration_id=(node_id << 5 | 0x0E),  # 0x0E: Set_Input_Torque
                    data=struct.pack('<f', torque_setpoint),
                    is_extended_id=False
                ))
                
            if (time.time() - initial_time) >= 7:
                bus.send(can.Message(
                    arbitration_id=(node_id << 5 | 0x0E),  # 0x0E: Set_Input_Torque
                    data=struct.pack('<f', 0),
                    is_extended_id=False
                ))

            time.sleep(0.001)

    #Reports encoder position
    def get_system_torque_thread(self, node_id, bus, initial_time, running):
        while running.is_set():
            
            start_time = time.time()
            while (time.time() - start_time) < 1:
                msg = bus.recv(timeout = 1 - (time.time() - start_time))  # Adjust timeout for recv
                if msg is None:
                    print("Timeout occurred, no message received.")
                    break

                if msg.arbitration_id == (node_id << 5 | 0x1C):  # 0x1C: Get_Torques
                    self.torque_setpoint, self.torque_estimate = struct.unpack('<ff', bytes(msg.data))
                    print(f"O-Drive {node_id} - Torque Target: {self.torque_setpoint:.3f} [Nm], Torque Estimate: {self.torque_estimate:.3f} [Nm]")

                    self.time_array.append(time.time() - initial_time)
                    self.torque_setpoint_array.append(self.torque_setpoint)
                    self.torque_estimate_array.append(self.torque_estimate)

                    break
            else:
                print(f"No torque message received for O-Drive {node_id} within the timeout period.")

            time.sleep(0.001) 