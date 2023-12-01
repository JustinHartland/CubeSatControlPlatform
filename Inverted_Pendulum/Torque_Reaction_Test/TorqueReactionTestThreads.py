#Purpose: define threads needed to test torque reaction times

import struct
import time
import can
import sqlite3

class TorqueReactionTestThreads:
    def __init__(self):
        self.encoder_position = 0
        self.encoder_velocity = 0

    #Thread to set motor velocity, CHANGE TO TORQUE CONTROL
    def set_vel_thread(self, node_id, bus, velocity, running):
        while running.is_set():
            bus.send(can.Message(arbitration_id=(node_id << 5 | 0x0d), data=struct.pack('<ff', float(velocity), 0.0), is_extended_id=False))

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
            if (time.time() - initial_time) >= 5:
                bus.send(can.Message(
                    arbitration_id=(node_id << 5 | 0x0E),  # 0x0E: Set_Input_Torque
                    data=struct.pack('<f', torque_setpoint),
                    is_extended_id=False
            ))
                
            time.sleep(0.001)

    #Reports encoder position
    def get_pos_thread(self, node_id, bus, running):
        while running.is_set():
            message = bus.recv()  # Blocking call
            if message.arbitration_id == (node_id << 5 | 0x09):  # Replace with the correct response ID
                # Parse the data to get encoder estimates
                position, velocity = message.data
                self.encoder_position = position
                #self.encoder_velocity = velocity

            time.sleep(0.001) 

    def add_data_to_database(self, db_path, initial_time, torque_setpoint, trial_id, running):
        while running.is_set():
            #Inside this loop, a new connection is created on each iteration
            with sqlite3.connect(db_path) as conn:
                imuData = [time.time() - initial_time, torque_setpoint, self.encoder_position]
                sql = ''' INSERT INTO imu_data(trial_id, time, torque_setpoint, encoder_position)
                  VALUES(?, ?, ?, ?, ?, ?, ?, ?, ? ,?, ?) '''
                cursor = conn.cursor()
                cursor.execute(sql, (trial_id, *imuData))
                conn.commit()

                time.sleep(0.001)