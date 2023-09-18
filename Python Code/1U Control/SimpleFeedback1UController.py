import time
import board
import busio
import adafruit_lsm9ds1
import math

# Setup I2C connection
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)

def compute_angles(ax, ay, az, mx, my, mz):
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
