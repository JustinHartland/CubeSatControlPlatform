import numpy as np
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def clear_terminal():
    """Clear the terminal screen."""
    # Windows
    if os.name == 'nt':
        os.system('cls')
    # Mac and Linux
    else:
        os.system('clear')

def get_cube_vertices(center, size):
    """Generate vertices for a cube centered at 'center' with side length 'size'."""
    c = np.array(center)
    s = size / 2
    return np.array([c + np.array([x, y, z]) for x in [-s, s] for y in [-s, s] for z in [-s, s]])

def apply_rotation(vertices, rotation_matrix):
    """Apply a rotation matrix to a set of vertices."""
    return np.dot(vertices - np.mean(vertices, axis=0), rotation_matrix.T)

def dcm_from_angles(theta, phi):
    """
    Generate the Direction Cosine Matrix (DCM) based on the given angles.

    Args:
    - theta (float): Angle in radians, e.g., roll.
    - phi (float): Angle in radians, e.g., pitch.

    Returns:
    - numpy.ndarray: The DCM matrix.
    """
    theta_rad, phi_rad = np.radians(theta), np.radians(phi)

    Rz = np.array([[np.cos(theta_rad), -np.sin(theta_rad), 0],
                   [np.sin(theta_rad), np.cos(theta_rad), 0],
                   [0, 0, 1]])
    Ry = np.array([[np.cos(phi_rad), 0, np.sin(phi_rad)],
                   [0, 1, 0],
                   [-np.sin(phi_rad), 0, np.cos(phi_rad)]])
    return np.dot(Rz, Ry)

    """ # Replace this DCM with the correct one for your application
    dcm = np.array([
        [cos_theta * cos_phi,   sin_theta * cos_phi,    -sin_phi    ],
        [-sin_theta,            cos_theta,              0           ],
        [cos_theta * sin_phi,   sin_theta * sin_phi,    cos_phi     ]
    ]) """


def plot_cube_and_axes(vertices, dcm, size):
    """Plot a cube given its vertices."""
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # List of sides' polygons
    verts = [[vertices[0], vertices[1], vertices[3], vertices[2]],
             [vertices[4], vertices[5], vertices[7], vertices[6]], 
             [vertices[0], vertices[1], vertices[5], vertices[4]], 
             [vertices[2], vertices[3], vertices[7], vertices[6]], 
             [vertices[1], vertices[3], vertices[7], vertices[5]], 
             [vertices[0], vertices[2], vertices[6], vertices[4]]]
    ax.add_collection3d(Poly3DCollection(verts, facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))

    # Inertial frame (global axes)
    axes_length = 1.5 * size  # Length of the axes
    axes_vectors = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])  # X, Y, Z
    axes_colors = ['r', 'g', 'b']  # Red for X, Green for Y, Blue for Z

    for axis, color in zip(axes_vectors, axes_colors):
        start_point = np.zeros(3)
        end_point = axis * axes_length
        ax.quiver(start_point[0], start_point[1], start_point[2], 
                end_point[0], end_point[1], end_point[2], 
                color=color, arrow_length_ratio=0.05)
        
    # Plot local axes of the cube
    axes_length = 1.5 * size/2
    local_axes = np.array([[axes_length, 0, 0], [0, axes_length, 0], [0, 0, axes_length]])
    rotated_axes = np.dot(local_axes, dcm.T)
    origin = np.mean(vertices, axis=0)
    for i, color in zip(range(3), ['magenta', 'limegreen', 'cyan']):  # RGB for XYZ axes
        ax.quiver(origin[0], origin[1], origin[2], 
                  rotated_axes[i, 0], rotated_axes[i, 1], rotated_axes[i, 2], 
                  color=color, arrow_length_ratio=0.05)
        
    # Set the view angle for a different perspective
    ax.view_init(elev=20, azim=40)
        
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.auto_scale_xyz([-1, 1], [-1, 1], [-1, 1])
    plt.show()

def main():
    # Clear the terminal screen
    clear_terminal()

    # User input
    theta_user = input("Theta: ")
    phi_user = input("Phi: ")

    theta_float = float(theta_user)
    phi_float = float(phi_user)

    # Get the DCM
    dcm = dcm_from_angles(theta_float, phi_float)

    print("Direction Cosine Matrix (DCM):")
    print(dcm)

    # Example usage: converting a vector in the body frame to the inertial frame
    vector_body_frame = np.array([1, 0, 0])  # Example vector
    vector_inertial_frame = dcm.dot(vector_body_frame)

    print("Vector in body frame:", vector_body_frame)
    print("Vector in inertial frame:", vector_inertial_frame)

    # Plotting new orientation

    # Parameters
    center = [0, 0, 0]  # Center of the cube
    size = 1            # Side length of the cube

    # Generate cube vertices and apply rotations
    vertices = get_cube_vertices(center, size)
    rotated_vertices = apply_rotation(vertices, dcm)

    # Plot the rotated cube
    plot_cube_and_axes(rotated_vertices, dcm, 1)

if __name__ == "__main__":
    main()
