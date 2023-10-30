from InertialMeasurementUnit import InertialMeasurementUnit
from InvPendDatabase import InvPendDatabase
import time

#Create instance of InertialMeasurementUnit:
imuDatabase = InvPendDatabase("imu_data.db")

#Create instance of InvPendDatabase:
IMU1 = InertialMeasurementUnit()

#Create array to hold most recent euler angles reported by .get_euler_angles()
#[angle_x, angle_y, angle_z]
imuData = []

initialTime = time.time()

while True:
    imuData = [initialTime-time.time(), *IMU1.get_euler_angles()]
    imuDatabase.add_imu_data(imuData)
    print(imuDatabase.get_column_data("imu_data", "angle_x"))
    time.sleep(0.01)