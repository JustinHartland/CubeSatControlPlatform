import time
import board
import busio
import adafruit_lsm9ds1
import odrive
from odrive.enums import *

# Find a connected ODrive (this will block until you connect one)
print("finding an odrive...")
my_drive = odrive.find_any()
my_drive.axis0.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL

# Initialize I2C bus and sensor
i2c = board.I2C()
sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)

# Initial angular positions
angle_x, angle_y, angle_z = 0.0, 0.0, 0.0

# Time initialization
prev_time = time.time()

#Set target angle
targetAngle = 0

while True:
    # Get the current time and compute the elapsed time
    curr_time = time.time()
    dt = curr_time - prev_time

    # Read gyroscope values (assumed to be in degrees per second)
    gyro_x, gyro_y, gyro_z = sensor.gyro

    # Integrate gyro values to get angular positions
    angle_x += gyro_x * dt
    angle_y += gyro_y * dt
    angle_z += gyro_z * dt

    # Print angular positions
    print(f'Angle Z: {angle_z:.2f}')

    if angle_z < targetAngle:
        my_drive.axis0.controller.input_vel = -1
    elif angle_z > targetAngle:
        my_drive.axis0.controller.input_vel = 1
    else:
        my_drive.axis0.controller.input_vel = 0


    # Update the previous time for the next iteration
    prev_time = curr_time

    # Sleep for a while to reduce the update rate
    time.sleep(0.01)
