# Import libraries
import as5048b
import time
import socket

host, port = "192.168.1.12", 25001

# Create instance of as5048b class
encoder = as5048b()

# Initialize TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

# Data string template
data_template = "{}, {}, {}"

try:
    # Continually read angular position data
    angle = 0

    #Connect to server
    sock.connect((host, port))

    while (True):
        angle = encoder.read_angle()
        print(angle)

        data = data_template.format(0, 0, angle)

        sock.sendall(data.encode("utf-8"))
        response = sock.recv(1024).decode("utf-8")
        print (response)

        time.sleep(0.05)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    sock.close()