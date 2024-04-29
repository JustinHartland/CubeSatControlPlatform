# Import libraries
from as5048b import as5048b
import time
import socket

host, port = "192.168.1.12", 25001

# Create instances of as5048b class
encoder_local_z1 = as5048b(282.78, address=0x41)  # Encoder for the first local Z-axis (yaw)

encoder_local_x = as5048b(66.42, address=0x40)   # Encoder for local X-axis (roll)

encoder_local_z2 = as5048b(0, address=0x42)  # Encoder for the second local Z-axis (yaw)
print("Encoder objects instantiated")

# Initialize TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))
print('Socket Connected')

# Data string template
data_template = "{}, {}, {}"

try:
    print('Try reached')

    # Continually read angular position data
    ring_angles = [0, 0, 0]

    while (True):
        ring_angles[0] = encoder_local_z1.get_angle()  # Angle around the first Z-axis (yaw) in degrees.
        ring_angles[1] = encoder_local_x.get_angle()      # Angle around the X-axis (roll) in degrees.
        ring_angles[2] = encoder_local_z2.get_angle()  # Angle around the second Z-axis (yaw) in degrees.
        
        # Print angles
        print(f"First Z (Yaw): {ring_angles[0]:.2f} deg, X (Roll): {ring_angles[1]:.2f} deg, Second Z (Yaw): {ring_angles[2]:.2f} deg\n")

        # Ensure that the check for None happens right after reading the angle
        if ring_angles is None:
            print("Error: angle is None")
            data = "0, 0, 0"
        else:
            data = f"{ring_angles[0]:.2f}, {ring_angles[1]:.2f}, {ring_angles[2]:.2f}"
            print(data)
        
        sock.sendall(data.encode("utf-8"))
        #response = sock.recv(1024).decode("utf-8")
        #print (response)

        time.sleep(0.05)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    sock.close()