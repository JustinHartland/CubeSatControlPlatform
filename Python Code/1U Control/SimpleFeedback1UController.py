import time
import board
import busio
import adafruit_lsm9ds1
import math
import numpy as np
from ahrs.filters import Madgwick

# Setup I2C connection
i2c = board.I2C()
sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)

#Initialize madgwick filter
madgwick_filter = Madgwick()

sample = 1
Q = np.tile([1., 0., 0., 0.], (sample, 1)) # Allocate for quaternions

def calibrate(num_samples=1000, delay_time=0.01):
    print("Starting Calibration...")
    sum_accel = [0, 0, 0]
    sum_gyro = [0, 0, 0]
    sum_magnet = [0, 0, 0]

    for i in range(num_samples):
        ax, ay, az = sensor.acceleration
        gx, gy, gz = sensor.gyro
        mx, my, mz = sensor.magnetic

        sum_accel[0] += ax
        sum_accel[1] += ay
        sum_accel[2] += az
        sum_gyro[0] += gx
        sum_gyro[1] += gy
        sum_gyro[2] += gz
        sum_magnet[0] += mx
        sum_magnet[1] += my
        sum_magnet[2] += mz

        time.sleep(delay_time)

    avg_accel = [val/num_samples for val in sum_accel]
    avg_gyro = [val/num_samples for val in sum_gyro]
    avg_magnet = [val/num_samples for val in sum_magnet]

    print("Calibration Complete!")
    return avg_accel, avg_gyro, avg_magnet

# Using the AHRS library, you can directly obtain Euler angles from the Madgwick filter output
def quaternion_to_euler(Q):
    return madgwick_filter.quaternion.to_euler()

# Perform calibration
accel_bias, gyro_bias, magnet_bias = calibrate()

while True:
    sample += 1

    ax, ay, az = sensor.acceleration
    gx, gy, gz = sensor.gyro
    mx, my, mz = sensor.magnetic

    # Offset the biases
    ax -= accel_bias[0]
    ay -= accel_bias[1]
    az -= accel_bias[2]
    
    gx -= gyro_bias[0]
    gy -= gyro_bias[1]
    gz -= gyro_bias[2]
    
    mx -= magnet_bias[0]
    my -= magnet_bias[1]
    mz -= magnet_bias[2]

    # Update Madgwick filter
    Q[sample] = madgwick_filter.updateIMU(Q[sample-1], [gx, gy, gz], [ax, ay, az])

    # Get the Euler angles from the quaternion
    roll, pitch, yaw = quaternion_to_euler(Q[sample])

    print(f"Roll: {roll:.2f}, Pitch: {pitch:.2f}, Yaw: {yaw:.2f}")
    
    time.sleep(0.01)  # Adjust as needed