# Import libraries
from as5048b import as5048b
import time
import socket

host, port = "192.168.1.12", 25001

# Create instance of as5048b class
encoder = as5048b()
print("Encoder object instantiated")

# Initialize TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))
print('Socket Connected')

# Data string template
data_template = "{}, {}, {}"

try:
    print('Try reached')

    # Continually read angular position data
    angle = 0

    while (True):
        angle = encoder.read_angle()
        print(angle)

        # Check if angle is None before proceeding
        if angle is None:
            print("Error: angle is None")
            data = 0
            # Handle the error appropriately, maybe continue to the next iteration or exit
        else:
            data = "0, 0, {:.2f}".format(angle)
            print(data)

    
        sock.sendall(data.encode("utf-8"))
        #response = sock.recv(1024).decode("utf-8")
        #print (response)

        time.sleep(0.05)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    sock.close()