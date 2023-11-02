#Purpose: Update euler angles [x, y, z] of IMU

import time
import math
import board
import busio
import adafruit_lsm9ds1

class InertialMeasurementUnit:
    def __init__(self):
        i2c = board.I2C()
        self.lsm = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)
        self.accel_range = adafruit_lsm9ds1.ACCELRANGE_2G
        self.gyro_scale = adafruit_lsm9ds1.GYROSCALE_245DPS

        self.prev_time = time.monotonic()

        #Euler angles
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0

        # Gyro offsets
        self.gyro_offset_x = 0
        self.gyro_offset_y = 0
        self.gyro_offset_z = 0

        # Gyro frequency
        self.imu_rate_time = time.monotonic()
        self.imu_read_count = 0
        self.imu_read_rate = 0

        # Filter coefficient for complementary filter
        self.alpha = 0.9

        #Calibrate gyro
        self.calibrate_gyro()

        #IMU data array to be appended to InvPendDatabase
        self.rawGyroArray = []
        self.rawAccelArray = []
        self.eulerAngleArray = []

    def get_accel_angle(self):
        ax, ay, az = self.lsm.acceleration
        self.rawAccelArray = [ax, ay, az]

        # Calculate roll and pitch angles from accelerometer data
        accel_angle_x = math.atan2(ay, az) * 180 / math.pi
        accel_angle_y = math.atan2(ax, math.sqrt(ay**2 + az**2)) * 180 / math.pi

        return accel_angle_x, accel_angle_y

    def get_gyro_angle(self):
        gx, gy, gz = self.lsm.gyro
        self.rawGyroArray = [gx, gy, gz]

        gx -= self.gyro_offset_x
        gy -= self.gyro_offset_y
        gz -= self.gyro_offset_z

        curr_time = time.monotonic()
        dt = curr_time - self.prev_time
        self.prev_time = curr_time
        self.gyro_angle_x = self.angle_x + gx * dt
        self.gyro_angle_y = self.angle_y + gy * dt
        self.gyro_angle_z = self.angle_z + gz * dt
        return self.gyro_angle_x, self.gyro_angle_y, self.gyro_angle_z
    
    def calibrate_gyro(self, samples=1000):
        print("Calibrating gyro. Please keep the sensor stationary...")
        
        sum_gx = 0
        sum_gy = 0
        sum_gz = 0
        
        for _ in range(samples):
            gx, gy, gz = self.lsm.gyro
            sum_gx += gx
            sum_gy += gy
            sum_gz += gz

            time.sleep(0.01)
        
        # Calculate average
        self.gyro_offset_x = sum_gx / samples
        self.gyro_offset_y = sum_gy / samples
        self.gyro_offset_z = sum_gz / samples
        
        print("Gyro calibration done!")


    def complementary_filter(self, accel_angle, gyro_angle):
        return self.alpha * (gyro_angle) + (1.0 - self.alpha) * accel_angle

    def get_euler_angles(self):
        #Get raw accel and gyro data from IMU
        accel_angle_x, accel_angle_y = self.get_accel_angle()
        gyro_angle_x, gyro_angle_y, gyro_angle_z = self.get_gyro_angle()

        # Apply complementary filter
        self.angle_x = self.complementary_filter(accel_angle_x, gyro_angle_x)
        self.angle_y = self.complementary_filter(accel_angle_y, gyro_angle_y)
        self.angle_z = gyro_angle_z  # Yaw is only from gyro as magnetometer is not used here