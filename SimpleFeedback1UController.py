import time
import board
import busio
import adafruit_lsm9ds1
import math

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize LSM9DS1 sensor
sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)

while True:
    # Read accelerometer, gyroscope, and magnetometer data
    accel_x, accel_y, accel_z = sensor.acceleration
    gyro_x, gyro_y, gyro_z = sensor.gyro
    mag_x, mag_y, mag_z = sensor.magnetic

    # Calculate Euler angles
    roll = math.atan2(gyro_y, gyro_z)

    gyro_z2 = gyro_y * math.sin(roll) + gyro_z * math.cos(roll)
    pitch = math.atan(-1 * gyro_x / gyro_z2)

    mag_y2 = mag_z * math.sin(roll) - mag_y * math.cos(roll)
    mag_z2 = mag_y * math.sin(roll) + mag_z * math.cos(roll)
    mag_x3 = mag_x * math.cos(pitch) + mag_z2 * math.sin(pitch)
    yaw = math.atan2(mag_y2, mag_x3)

    # Print the Euler angles
    print("\nRoll: {:.2f} degrees".format(roll * 180 / math.pi))
    print("Pitch: {:.2f} degrees".format(pitch * 180 / math.pi))
    print("Yaw: {:.2f} degrees".format(yaw * 180/ math.pi))

    # Delay for a short time before the next reading
    time.sleep(0.5)
