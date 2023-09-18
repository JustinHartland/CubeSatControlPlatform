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

currentSample = 0
sample = 10000
Q = np.tile([1., 0., 0., 0.], (sample, 1)) # Allocate for quaternions
Q[0] = [1, 0, 0, 0]

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

def quaternion_to_euler(w, x, y, z):
    """
    Convert a quaternion into euler angles (roll, pitch, yaw)
    roll is rotation around x in radians (counterclockwise)
    pitch is rotation around y in radians (counterclockwise)
    yaw is rotation around z in radians (counterclockwise)
    """
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = math.atan2(t0, t1)
    
    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = math.asin(t2)
    
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.atan2(t3, t4)

    return roll_x, pitch_y, yaw_z  # in radian


# Perform calibration
accel_bias, gyro_bias, magnet_bias = calibrate()

while True:
    currentSample += 1

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
    Q[currentSample] = madgwick_filter.updateIMU(Q[currentSample-1], [gx, gy, gz], [ax, ay, az])

    # Get the Euler angles from the quaternion
    roll, pitch, yaw = quaternion_to_euler(Q[currentSample])

    print(f"Roll: {roll:.2f}, Pitch: {pitch:.2f}, Yaw: {yaw:.2f}")
    
    time.sleep(0.01)  # Adjust as needed
