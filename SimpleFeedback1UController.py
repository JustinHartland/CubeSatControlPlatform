import math
import time
import board
import busio
import adafruit_lsm9ds1
import numpy as np
from scipy.spatial.transform import Rotation as R

# Initialize I2C bus
i2c = board.I2C()

# Initialize LSM9DS1 sensor
sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)

while True:
    # Read accelerometer, gyroscope, and magnetometer data
    accel_x, accel_y, accel_z = sensor.acceleration
    gyro_x, gyro_y, gyro_z = sensor.gyro
    mag_x, mag_y, mag_z = sensor.magnetic

    # Calculate pitch and roll angles using accelerometer data
    pitch = math.degrees(math.atan2(accel_x, math.sqrt(accel_y**2 + accel_z**2)))
    roll = math.degrees(math.atan2(accel_y, math.sqrt(accel_x**2 + accel_z**2)))
    yaw = math.degrees(math.atan2(mag_y, mag_x))

    # Create a rotation matrix using the calculated pitch and roll
    rotation_matrix = R.from_euler('zyx', [yaw, pitch, roll], degrees=True).as_matrix()

    # Extract Euler angles from the rotation matrix
    yaw, pitch, roll = R.from_matrix(rotation_matrix).as_euler('zyx', degrees=True)

    # Print the Euler angles
    print("Roll: {:.2f} degrees".format(roll))
    print("Pitch: {:.2f} degrees".format(pitch))
    print("Yaw: {:.2f} degrees".format(yaw))

    # Delay for a short time before the next reading
    time.sleep(0.5)
