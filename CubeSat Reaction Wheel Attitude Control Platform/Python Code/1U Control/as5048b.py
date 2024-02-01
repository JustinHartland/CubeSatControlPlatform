#Purpose: Update attitude of 1 DoF CubeSat

import smbus
import time

class as5048b:
    def __init__(self):
        self.bus = smbus.SMBus(1)

        # AS5048A default address
        self.AS5048A_ADDR = 0x40

        # AS5048A Register
        self.AS5048A_ANGLE_REG = 0xFE

        #Sensor angle
        self.angle = 0

    def read_angle(self):
        '''
        Read angular position of motor shaft
        
        return: angular position of motor shaft
        '''
        # Read data from the angle register
        data = self.bus.read_i2c_block_data(self.AS5048A_ADDR, self.AS5048A_ANGLE_REG, 2)

        # Convert the data
        angle_pre_conversion = data[0] * 256 + data[1]

        # Full range of the sensor is 0 to 16383
        # Convert to degrees (0 to 360)
        self.angle = (angle_pre_conversion / 16383.0) * 90.0

        return self.angle