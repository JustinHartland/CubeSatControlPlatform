import time
import math
import board
import busio
import adafruit_lsm9ds1

class InertialMeasurementUnit:
    def __init__(self):
        i2c = board.I2C()
        self.lsm = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)

        # Previous time for integration
        self.prev_time = time.time()

        # Previous angles from gyroscope
        self.gyro_angle_x = 0
        self.gyro_angle_y = 0
        self.gyro_angle_z = 0

        # Gyro offsets
        self.gyro_offset_x = 0
        self.gyro_offset_y = 0
        self.gyro_offset_z = 0

        # Filter coefficient for complementary filter
        self.alpha = 0.98

    def get_accel_angle(self):
        ax, ay, az = self.lsm.acceleration
        # Calculate roll and pitch angles from accelerometer data
        accel_angle_x = math.atan2(ay, math.sqrt(ax**2 + az**2)) * 180 / math.pi
        accel_angle_y = math.atan2(-ax, math.sqrt(ay**2 + az**2)) * 180 / math.pi
        return accel_angle_x, accel_angle_y

    def get_gyro_angle(self):
        gx, gy, gz = self.lsm.gyro
        gx -= self.gyro_offset_x
        gy -= self.gyro_offset_y
        gz -= self.gyro_offset_z

        curr_time = time.time()
        dt = curr_time - self.prev_time
        self.prev_time = curr_time
        self.gyro_angle_x += gx * dt
        self.gyro_angle_y += gy * dt
        self.gyro_angle_z += gz * dt
        return self.gyro_angle_x, self.gyro_angle_y, self.gyro_angle_z
    
    def calibrate_gyro(self, samples=500):
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
        accel_angle_x, accel_angle_y = self.get_accel_angle()
        gyro_angle_x, gyro_angle_y, gyro_angle_z = self.get_gyro_angle()

        # Apply complementary filter
        roll = self.complementary_filter(accel_angle_x, gyro_angle_x)
        pitch = self.complementary_filter(accel_angle_y, gyro_angle_y)
        yaw = gyro_angle_z  # Yaw is only from gyro as magnetometer is not used here

        return roll, pitch, yaw

#Example implementation code
if __name__ == "__main__":
    IMU1 = InertialMeasurementUnit()
    IMU1.calibrate_gyro()
    while True:
        roll, pitch, yaw = IMU1.get_euler_angles()
        print(f"Roll: {roll*180/math.pi:.2f}, Pitch: {pitch*180/math.pi:.2f}, Yaw: {yaw*180/math.pi:.2f}")
        time.sleep(0.1)