# Programmer: Justin Hartland
# Purpose: Acquire angular position of electric motor using AS5048A ams encoder

import smbus
import time

# Create an SMBus instance
bus = smbus.SMBus(1)

# AS5048A default address
AS5048A_ADDR = 0x40

# AS5048A Register
AS5048A_ANGLE_REG = 0xFE

def read_angle():
    '''
    Read angular position of motor shaft
    
    return: angular position of motor shaft
    '''
    # Read data from the angle register
    data = bus.read_i2c_block_data(AS5048A_ADDR, AS5048A_ANGLE_REG, 2)

    # Convert the data
    angle = data[0] * 256 + data[1]

    # Full range of the sensor is 0 to 16383
    # Convert to degrees (0 to 360)
    angle = (angle / 16383.0) * 90.0

    return angle
    
#Main script
try:
    while True:
        angle = read_angle()
        print("Angle: {:.2f} degrees".format(angle))
        time.sleep(0.05)

except KeyboardInterrupt:
    print("Measurement stopped by user")
    bus.close()