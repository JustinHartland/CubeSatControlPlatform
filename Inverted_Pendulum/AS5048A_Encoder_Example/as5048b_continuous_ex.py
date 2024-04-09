import smbus
import time

# Create an SMBus instance
bus = smbus.SMBus(1)

# AS5048A default address
AS5048A_ADDR = 0x40

# AS5048A Register
AS5048A_ANGLE_REG = 0xFE

# Function to read raw angle from the encoder
def read_raw_angle():
    data = bus.read_i2c_block_data(AS5048A_ADDR, AS5048A_ANGLE_REG, 2)
    return data[0] * 256 + data[1]

# Function to convert raw angle to degrees
def raw_to_degrees(raw_angle):
    return (raw_angle / 16383.0) * 90

# Initialize the last angle and the total rotations
last_angle_raw = read_raw_angle()
total_rotations = 0

def read_angle():
    global last_angle_raw, total_rotations
    
    # Read the current raw angle
    current_angle_raw = read_raw_angle()
    
    # Convert to degrees
    current_angle = raw_to_degrees(current_angle_raw)
    
    # Calculate change in angle
    change_in_angle_raw = current_angle_raw - last_angle_raw
    
    # Update the last angle
    last_angle_raw = current_angle_raw
    
    # Check for wrap around (if the encoder passes through 0)
    if change_in_angle_raw > 8191:  # more than half of 16383
        total_rotations -= 1
    elif change_in_angle_raw < -8191:
        total_rotations += 1
    
    # Calculate the total angle considering the rotations
    total_angle = total_rotations * 360 + current_angle
    
    return total_angle
    
# Main script
try:
    while True:
        angle = read_angle()
        print("Angle: {:.2f} degrees".format(angle))
        time.sleep(0.05)

except KeyboardInterrupt:
    print("Measurement stopped by user")
    bus.close()