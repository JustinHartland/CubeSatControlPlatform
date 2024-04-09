# Examples of utilizing as5048b class

# Import libraries
import as5048b
import time

# Create instance of as5048b class
encoder = as5048b()

# Continually read angular position data
angle = 0
while (True):
    angle = encoder.read_angle()

    print(angle)

    time.sleep(0.05)