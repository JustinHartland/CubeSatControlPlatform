#Purpose: define threads needed to test torque reaction times

import struct
import time
import can
import sqlite3

class TorqueReactionTestThreads:
    def __init__(self):
        self.torque_setpoint = 0
        self.torque_estimate = 0

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
            if (time.time() - initial_time) >= 5 and (time.time() - initial_time) < 10:
                bus.send(can.Message(
                    arbitration_id=(node_id << 5 | 0x0E),  # 0x0E: Set_Input_Torque
                    data=struct.pack('<f', torque_setpoint),
                    is_extended_id=False
                ))
                
            if (time.time() - initial_time) >= 10:
                bus.send(can.Message(
                    arbitration_id=(node_id << 5 | 0x0E),  # 0x0E: Set_Input_Torque
                    data=struct.pack('<f', 0),
                    is_extended_id=False
                ))

            time.sleep(0.001)

    #Reports encoder position
    def get_system_torque_thread(self, node_id, bus, running):
        while running.is_set():
            message = bus.recv()  # Blocking call
            if message.arbitration_id == (node_id << 5 | 0x1c):  # Replace with the correct response ID
                # Parse the data to get encoder estimates

                torque_setpoint, torque_estimate = message.data

                self.torque_setpoint = torque_setpoint
                self.torque_estimate = torque_estimate

            time.sleep(0.001) 

    def add_data_to_database(self, db_path, initial_time, trial_id, running):
        while running.is_set():
            #Inside this loop, a new connection is created on each iteration
            with sqlite3.connect(db_path) as conn:
                data = [time.time() - initial_time, self.torque_setpoint, self.torque_estimate]
                sql = ''' INSERT INTO data(trial_id, time, torque_setpoint, torque_estimate)
                  VALUES(?, ?, ?, ?) '''
                cursor = conn.cursor()
                cursor.execute(sql, (trial_id, *data))
                conn.commit()

                time.sleep(0.001)