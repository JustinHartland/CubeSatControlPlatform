import time
import board
import busio
import adafruit_lsm9ds1

# Initialize I2C bus and sensor
i2c = board.I2C()
sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)

# Initial angular positions
angle_x, angle_y, angle_z = 0.0, 0.0, 0.0

# Time initialization
prev_time = time.time()

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
    print(f'Angle X: {angle_x:.2f}, Angle Y: {angle_y:.2f}, Angle Z: {angle_z:.2f}')

    # Update the previous time for the next iteration
    prev_time = curr_time

    # Sleep for a while to reduce the update rate
    time.sleep(0.01)
