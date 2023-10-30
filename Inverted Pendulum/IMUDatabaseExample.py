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
    imuEulerAngles = IMU1.get_euler_angles()
    imuData = [initialTime-time.time(), *imuEulerAngles]
    imuDatabase.add_imu_data(imuData)

    print("Angle X: %.3f deg", imuEulerAngles(0))
    
    time.sleep(0.01)