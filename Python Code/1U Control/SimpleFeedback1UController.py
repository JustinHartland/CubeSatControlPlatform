import time
import board
import busio
import adafruit_lsm9ds1
import math

# Setup I2C connection
i2c = board.I2C()
sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)

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

def compute_angles(ax, ay, az, mx, my, mz):
    roll = math.atan2(ay, az)
    pitch = math.atan2(-ax, math.sqrt(ay**2 + az**2))
    yaw = math.atan2(my * math.cos(roll) - mz * math.sin(roll),
                     mx * math.cos(pitch) + my * math.sin(pitch) * math.sin(roll) + mz * math.sin(pitch) * math.cos(roll))
    return math.degrees(roll), math.degrees(pitch), math.degrees(yaw)

# Perform calibration
accel_bias, gyro_bias, magnet_bias = calibrate()

while True:
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

    roll, pitch, yaw = compute_angles(ax, ay, az, mx, my, mz)
    print(f"Roll: {roll:.2f}, Pitch: {pitch:.2f}, Yaw: {yaw:.2f}")
    
    time.sleep(0.01)  # Adjust as needed
