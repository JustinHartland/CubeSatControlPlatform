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
            
            start_time = time.time()
            while (time.time() - start_time) < 1:
                msg = bus.recv(timeout = 1 - (time.time() - start_time))  # Adjust timeout for recv
                if msg is None:
                    print("Timeout occurred, no message received.")
                    break

                if msg.arbitration_id == (node_id << 5 | 0x1C):  # 0x1C: Get_Torques
                    torque_target, torque_estimate = struct.unpack('<ff', bytes(msg.data))
                    print(f"O-Drive {node_id} - Torque Target: {torque_target:.3f} [Nm], Torque Estimate: {torque_estimate:.3f} [Nm]")
                    break
            else:
                print(f"No torque message received for O-Drive {node_id} within the timeout period.")

            time.sleep(0.001) 


    def add_data_to_database(self, db_path, initial_time, trial_id, running):
        while running.is_set():
            #Inside this loop, a new connection is created on each iteration
            with sqlite3.connect(db_path) as conn:
                data = [time.time() - initial_time, self.torque_setpoint, self.torque_estimate]

                print('Data added to db: torque_setpoint = %.2f\n' % self.torque_setpoint)

                sql = ''' INSERT INTO data(trial_id, time, torque_setpoint, torque_estimate)
                  VALUES(?, ?, ?, ?) '''
                cursor = conn.cursor()
                cursor.execute(sql, (trial_id, *data))
                conn.commit()

                time.sleep(0.001)