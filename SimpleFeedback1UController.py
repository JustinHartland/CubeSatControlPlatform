import time
import board
import busio
import adafruit_lsm9ds1

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
    roll = 180 * (accel_x / 9.81)  # Convert acceleration to degrees
    pitch = 180 * (accel_y / 9.81)  # Convert acceleration to degrees
    yaw = 180 * (gyro_z / 32767.0)  # Convert gyroscope data to degrees

    # Print the Euler angles
    #print("Roll: {:.2f} degrees".format(roll))
    #print("Pitch: {:.2f} degrees".format(pitch))
    print("Yaw: {:.2f} degrees".format(yaw))

    # Delay for a short time before the next reading
    time.sleep(0.1)
