#Purpose: define threads needed to operate inverted pendulum

from simple_pid import PID
import struct
import time
import can
from InvPendFaradayTestDatabase import InvPendFaradayTestDatabase
import sqlite3

class FaradayTestingThreads:
    def __init__(self):
        self.encoder_position = 0
        self.encoder_velocity = 0

    # Function to set torque for a specific O-Drive
    def set_torque_thread(self, node_id, bus, torque_setpoint, initiation_time, running):
        while running.is_set():

            #Switch sign of torque after 5 seconds
            if (time.time() - initiation_time) > 5:
                torque_setpoint = torque_setpoint * -1

            bus.send(can.Message(
                arbitration_id=(node_id << 5 | 0x0E),  # 0x0E: Set_Input_Torque
                data=struct.pack('<f', torque_setpoint),
                is_extended_id=False
            ))
            #print(f"Successfully set ODrive {node_id} to {torque} [Nm]")
            time.sleep(0.001)

    #Prints arm angle and motor velocity
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