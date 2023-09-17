import math
import time
import board
import busio
import scipy
import numpy
from adafruit_lsm9ds1 import LSM9DS1
from pyquaternion import Quaternion

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize LSM9DS1 sensor
sensor = LSM9DS1(i2c)

while True:
    # Read accelerometer, gyroscope, and magnetometer data
    accel_x, accel_y, accel_z = sensor.acceleration
    gyro_x, gyro_y, gyro_z = sensor.gyro
    mag_x, mag_y, mag_z = sensor.magnetic

    # Calculate pitch and roll angles using accelerometer data
    pitch = math.degrees(math.atan2(accel_x, math.sqrt(accel_y**2 + accel_z**2)))
    roll = math.degrees(math.atan2(accel_y, math.sqrt(accel_x**2 + accel_z**2)))

    # Create a quaternion using the calculated pitch and roll
    quaternion_data = Quaternion(axis=[1, 0, 0], angle=math.radians(roll)) * \
                     Quaternion(axis=[0, 1, 0], angle=math.radians(pitch))

    # Calculate yaw angle using magnetometer data (if needed)
    # Replace this part if you have a specific yaw calculation method

    # Convert quaternion to Euler angles (roll, pitch, yaw)
    euler_angles = quaternion_data.to_euler_angles(degrees=True)

    # Extract Euler angles
    roll, pitch, yaw = euler_angles

    # Print the Euler angles
    print("Roll: {:.2f} degrees".format(roll))
    print("Pitch: {:.2f} degrees".format(pitch))
    print("Yaw: {:.2f} degrees".format(yaw))

    # Delay for a short time before the next reading
    time.sleep(0.1)
