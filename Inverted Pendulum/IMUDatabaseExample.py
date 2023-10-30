from InertialMeasurementUnit import InertialMeasurementUnit
import time

IMU1 = InertialMeasurementUnit()
while True:
    angle_x, angle_y, angle_z = IMU1.get_euler_angles()
    print(f"Roll: {angle_x:.2f}")
    time.sleep(0.01)