#Purpose: define threads needed to operate inverted pendulum

from simple_pid import PID
import struct
import time
import can
import sqlite3

class Faraday_Cage_Test_Threads:
    def __init__(self):
        self.encoder_position = 0
        self.encoder_velocity = 0

    #Thread to set motor velocity, CHANGE TO TORQUE CONTROL
    def set_vel_thread(self, node_id, bus, velocity, initialTime, running):
        while running.is_set():
            # if (time.time() - initialTime) >= 5 and (time.time() - initialTime) < 10:
            #     velocity = 5
            # if (time.time() - initialTime) >= 10:
            #     velocity = 10
            bus.send(can.Message(arbitration_id=(node_id << 5 | 0x0d), data=struct.pack('<ff', float(velocity), 0.0), is_extended_id=False))
            time.sleep(0.001)

    #Thread to read in orientation angle from IMU
    def read_angle_thread(self, imu_obj, running):
        while running.is_set():
            imu_obj.get_euler_angles()
            time.sleep(0.001)
            
        #Reports encoder position
    def get_vel_thread(self, node_id, bus, running):
        while running.is_set():
            message = bus.recv()  # Blocking call
            if message.arbitration_id == (node_id << 5 | 0x09):  # Replace with the correct response ID
                # Parse the data to get encoder estimates
                position, velocity = struct.unpack('<ff', message.data)
                self.encoder_position = position
                self.encoder_velocity = velocity

            time.sleep(0.001) 

    def add_data_to_database(self, imu_obj, db_path, initial_time, trial_id, velocity_setpoint, running):
        while running.is_set():
            #Inside this loop, a new connection is created on each iteration
            with sqlite3.connect(db_path) as conn:
                imuData = [time.time() - initial_time, imu_obj.angle_x, imu_obj.angle_y, imu_obj.angle_z, self.encoder_velocity, velocity_setpoint]
                sql = ''' INSERT INTO imu_data(trial_id, time, angle_x, angle_y, angle_z, encoder_velocity, velocity_setpoint)
                  VALUES(?, ?, ?, ?, ?, ?, ?) '''
                cursor = conn.cursor()
                cursor.execute(sql, (trial_id, *imuData))
                conn.commit()
                time.sleep(0.001)