import time
import board
import busio
import adafruit_lsm9ds1
import math

# Setup I2C connection
i2c = board.I2C()
sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)

# Calibration parameters
num_samples = 1000
delay_time = 0.01

print("Starting Calibration...")

# Initialize sums for each sensor reading
sum_accel = [0, 0, 0]
sum_gyro = [0, 0, 0]
sum_magnet = [0, 0, 0]

for i in range(num_samples):
    # Read sensor values
    ax, ay, az = sensor.acceleration
    gx, gy, gz = sensor.gyro
    mx, my, mz = sensor.magnetic

    # Accumulate readings
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

# Compute average values for each sensor
avg_accel = [val/num_samples for val in sum_accel]
avg_gyro = [val/num_samples for val in sum_gyro]
avg_magnet = [val/num_samples for val in sum_magnet]

print("Calibration Complete!")

print(f"Accelerometer Bias: {avg_accel}")
print(f"Gyroscope Bias: {avg_gyro}")
print(f"Magnetometer Bias: {avg_magnet}")

print("\nStore these bias values for your application to offset your sensor readings.")


""" def compute_angles(ax, ay, az, mx, my, mz):
    # Calculate the roll angle (rotation around the y-axis)
    roll = math.atan2(ay, math.sqrt(ax**2 + az**2))
    
    # Calculate the pitch angle (rotation around the x-axis)
    pitch = math.atan2(-ax, math.sqrt(ay**2 + az**2))
    
    # Calculate the yaw angle (rotation around the z-axis)
    yaw = math.atan2(my * math.cos(roll) - mz * math.sin(roll),
                     mx * math.cos(pitch) + my * math.sin(pitch) * math.sin(roll) + mz * math.sin(pitch) * math.cos(roll))
    
    # Convert from radians to degrees
    roll = math.degrees(roll)
    pitch = math.degrees(pitch)
    yaw = math.degrees(yaw)  # Convert yaw to degrees
    
    return roll, pitch, yaw

while True:
    # Get accelerometer, magnetometer data
    ax, ay, az = sensor.acceleration
    mx, my, mz = sensor.magnetic
    
    # Compute roll, pitch, and yaw from the sensor data
    roll, pitch, yaw = compute_angles(ax, ay, az, mx, my, mz)

    print(f"Roll: {roll:.2f}, Pitch: {pitch:.2f}, Yaw: {yaw:.2f}")
    
    time.sleep(0.01)  # Adjust as needed
 """