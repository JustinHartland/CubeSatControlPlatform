from as5048b import as5048b  # Import the as5048b module for handling AS5048B magnetic rotary position sensor.
import numpy as np           # Import numpy for mathematical operations and matrix manipulation.
import time                  # Import time module to use sleep for timing control.

def get_body_axes_inertial(phi, theta, psi):
    # Convert angles from degrees to radians for mathematical operations.
    phi = np.radians(phi)
    theta = np.radians(theta)
    psi = np.radians(psi)

    # Define the rotation matrix for the first rotation around the Z-axis (yaw).
    R_3_1 = np.array([[np.cos(phi), -np.sin(phi), 0],
                      [np.sin(phi), np.cos(phi), 0],
                      [0, 0, 1]])

    # Define the rotation matrix for rotation around the X-axis (roll).
    R_1 = np.array([[1, 0, 0],
                    [0, np.cos(theta), -np.sin(theta)],
                    [0, np.sin(theta), np.cos(theta)]])

    # Define the rotation matrix for the second rotation around the Z-axis (yaw).
    R_3_2 = np.array([[np.cos(psi), -np.sin(psi), 0],
                      [np.sin(psi), np.cos(psi), 0],
                      [0, 0, 1]])

    # Compute the Direction Cosine Matrix (DCM) for transformation from inertial to body frame.
    inertial_to_body_DCM = R_3_2 @ R_1 @ R_3_1

    # Compute the DCM for transformation from body to inertial frame by transposing the above DCM.
    body_to_inertial_DCM = np.transpose(inertial_to_body_DCM)

    # Use the body-to-inertial DCM to transform the standard basis vectors to obtain body frame axes in inertial coordinates.
    body_x_inertial = body_to_inertial_DCM @ [1, 0, 0]
    body_y_inertial = body_to_inertial_DCM @ [0, 1, 0]
    body_z_inertial = body_to_inertial_DCM @ [0, 0, 1]

    # Group the transformed axes vectors into a single list for output.
    body_axes_inertial = [body_x_inertial, body_y_inertial, body_z_inertial]

    return body_axes_inertial

def main():
    # Initialize encoder instances for local Z1, X, and Z2 axes. These will read angular positions.
    encoder_local_z1 = as5048b(address=0x40)  # Encoder for the first local Z-axis (yaw)
    encoder_local_z1.calibrate_encoder()      # Calibrate the encoder

    encoder_local_x = as5048b(address=0x41)   # Encoder for local X-axis (roll)
    encoder_local_x.calibrate_encoder()       # Calibrate the encoder

    encoder_local_z2 = as5048b(address=0x42)  # Encoder for the second local Z-axis (yaw)
    encoder_local_z2.calibrate_encoder()      # Calibrate the encoder

    report_interval = 50  # How many loops to wait before reporting again.
    loop_counter = 0  # Counter to keep track of loop iterations.

    while(True):
        # Continuously read the angular positions from all three encoders.
        phi = encoder_local_z1.get_angle()  # Angle around the first Z-axis (yaw) in degrees.
        theta = encoder_local_x.get_angle()      # Angle around the X-axis (roll) in degrees.
        psi = encoder_local_z2.get_angle()  # Angle around the second Z-axis (yaw) in degrees.

        # Calculate the body frame axes with respect to the inertial frame based on encoder readings.
        body_axes_inertial = get_body_axes_inertial(phi, theta, psi)

        if loop_counter % report_interval == 0:
            #print(f"Body Axes Inertial Orientation: X-axis: {body_axes_inertial[0]}, Y-axis: {body_axes_inertial[1]}, Z-axis: {body_axes_inertial[2]}")
            print(f"First Z (Yaw): {phi} deg, X (Roll): {theta} deg, Second Z (Yaw): {psi} deg")
            print()
        
        loop_counter += 1  # Increment loop counter

        # Pause for a short duration before the next loop iteration to limit the rate of operation.
        time.sleep(0.05)

if __name__ == "__main__":
    main()
