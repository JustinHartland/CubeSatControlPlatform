import time
import board
import busio
import adafruit_lsm9ds1
from ahrs.filters import Madgwick
import numpy as np

# Setup I2C connection
i2c = board.I2C()
sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)

# Create the Madgwick filter object
madgwick = Madgwick()

#Allocation for quaternions
Q = np.zeros((1, 4))
t = 1

#Initial attitude quaternion
Q[0] = [1, 0, 0, 0]

while True:
    t += 1

    # Get accelerometer, gyroscope, and magnetometer data
    ax, ay, az = sensor.acceleration
    gx, gy, gz = sensor.gyro
    mx, my, mz = sensor.magnetic

    # Update the filter with the new data
    madgwick = updateIMU(Q[t - 1], np.array([gx, gy, gz]), np.array([ax, ay, az]), np.array([mx, my, mz]))

    # The orientation is directly available as a quaternion
    q = madgwick.quaternion

    # Convert quaternion to Euler angles
    euler = q.to_euler(degrees=True)  # Convert to Euler angles in degrees

    print(f"Roll: {euler[0]:.2f}, Pitch: {euler[1]:.2f}, Yaw: {euler[2]:.2f}")

    time.sleep(0.01)  # Adjust as needed
