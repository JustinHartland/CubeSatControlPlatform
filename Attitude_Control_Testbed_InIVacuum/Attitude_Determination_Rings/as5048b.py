#Purpose: Update attitude of 1 DoF CubeSat

import smbus
import time

class as5048b:
    def __init__(self, address):
        self.bus = smbus.SMBus(1)
        self.AS5048B_ADDR = address # AS5048B default address
        self.AS5048B_ANGLE_REG = 0xFE # AS5048B Register
        self.angle = 0 #Sensor angle
        self.offset_angle = 0 #Offset angle to calibrate

    def calibrate_encoder(self):
        print('Ensure CoM is below pivot\n\nCalibration beginning in:\n\n')
        time_remaining = 3

        while (time_remaining != 0):
            print(f"{time_remaining} s")
            time_remaining = time_remaining - 1
            time.sleep(1)

        #Determine offset
        data = self.bus.read_i2c_block_data(self.AS5048B_ADDR, self.AS5048B_ANGLE_REG, 2)
        angle_pre_conversion = data[0] * 256 + data[1]
        resting_angle = (angle_pre_conversion / 16383.0) * 45

        self.offset_angle = resting_angle  # Here we simply store the resting angle as the offset

    def get_angle(self):
        # Read data from the angle register
        data = self.bus.read_i2c_block_data(self.AS5048B_ADDR, self.AS5048B_ANGLE_REG, 2)

        # Convert the data
        angle_pre_conversion = data[0] * 256 + data[1]

        # Full range of the sensor is 0 to 16383
        # Convert to degrees (0 to 360)
        self.angle = (angle_pre_conversion / 16383.0) * 90.0

 # Example run
""" def main():
    # Create two instances of as5048b for each encoder
    encoder_local_z = as5048b(address=0x10)
    encoder_local_z.calibrate_encoder()

    encoder_local_x = as5048b()
    encoder_local_x.calibrate_encoder(address=0x10)

    # Get angular positions in degrees
    theta = encoder_local_z.get_angle()
    phi = encoder_local_x.get_angle() """



