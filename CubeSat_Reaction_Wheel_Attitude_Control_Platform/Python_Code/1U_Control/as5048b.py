# Purpose: Report angular position detected by encoder sensor

# Import libraries
import smbus
import time

class as5048b:
    def __init__(self):
        """
        Initialize as5048b object
        """
        self.bus = smbus.SMBus(1)
        self.AS5048B_ADDR = 0x40 # AS5048B default address
        self.AS5048B_ANGLE_REG = 0xFE # AS5048B Register
        self.angle = 0 #Sensor angle

    def read_angle(self):
        '''
        Read angular position of motor shaft
        
        return: return: Adjusted angular position of motor shaft
        '''

        # Read data from the angle register
        data = self.bus.read_i2c_block_data(self.AS5048B_ADDR, self.AS5048B_ANGLE_REG, 2)

        # Convert the data
        angle_pre_conversion = data[0] * 256 + data[1]
        self.angle = (angle_pre_conversion / 16383.0) * 45.0

        #print(self.angle)
        return self.angle