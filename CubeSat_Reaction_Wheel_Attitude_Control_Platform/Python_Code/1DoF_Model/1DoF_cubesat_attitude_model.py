import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Initialize the figure and 3D axis
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Limits and labels for axes
ax.set_xlim([-2, 2])
ax.set_ylim([-2, 2])
ax.set_zlim([-2, 2])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
5
# Define the size of the gimbal ring
ring_size = 1.5

# Initial setup for the gimbal ring, represented as a line
gimbal, = ax.plot([], [], [], 'r-', linewidth=2)
# Add lines for rotational axes
axis_x = ax.plot([-2, 2], [0, 0], [0, 0], 'k--', label='Gimbal Axis (X)')[0]
axis_y_prime = ax.plot([], [], [], 'g--', label="Cube's Rotational Axis (Y')")[0]

# Function to define cube faces
def cube_faces(vertices):
    return [[vertices[0], vertices[1], vertices[2], vertices[3]],
            [vertices[4], vertices[5], vertices[6], vertices[7]], 
            [vertices[0], vertices[1], vertices[5], vertices[4]], 
            [vertices[2], vertices[3], vertices[7], vertices[6]], 
            [vertices[1], vertices[2], vertices[6], vertices[5]],
            [vertices[4], vertices[7], vertices[3], vertices[0]]]

# Function to update the positions of the cube, gimbal ring, and rotation axes
def update(frame):
    # Remove existing cube faces
    for col in ax.collections[::-1]:
        col.remove()

    # Gimbal rotation about the X-axis
    theta = np.radians(frame)

    # Cube rotation about the local Y'-axis (after gimbal rotation)
    phi = np.radians(frame * 2)

    # Rotation matrix for the gimbal ring about the X axis
    R_gimbal = np.array([[1, 0, 0],
                         [0, np.cos(theta), -np.sin(theta)],
                         [0, np.sin(theta), np.cos(theta)]])

    # Rotation matrix for the cube about the local Y' axis
    R_cube_local_y = np.array([[np.cos(phi), 0, np.sin(phi)],
                               [0, 1, 0],
                               [-np.sin(phi), 0, np.cos(phi)]])

    # Combined rotation
    R_total = np.dot(R_cube_local_y, R_gimbal)

    # Gimbal ring definition
    gimbal_theta = np.linspace(0, 2 * np.pi, 100)
    gimbal_x = ring_size * np.cos(gimbal_theta)
    gimbal_y = ring_size * np.sin(gimbal_theta)
    gimbal_z = np.zeros_like(gimbal_theta)
    gimbal_points = np.vstack([gimbal_x, gimbal_y, gimbal_z])
    rotated_gimbal_points = np.dot(R_gimbal, gimbal_points)

    # Update gimbal ring line
    gimbal.set_data(rotated_gimbal_points[0, :], rotated_gimbal_points[1, :])
    gimbal.set_3d_properties(rotated_gimbal_points[2, :])

    # Update the cube's local Y' axis representation
    y_prime_start = np.dot(R_gimbal, [0, -2, 0])
    y_prime_end = np.dot(R_gimbal, [0, 2, 0])
    axis_y_prime.set_data([y_prime_start[0], y_prime_end[0]], [y_prime_start[1], y_prime_end[1]])
    axis_y_prime.set_3d_properties([y_prime_start[2], y_prime_end[2]])

    # Define cube vertices and apply total rotation
    cube_size = 0.5
    cube_vertices = np.array([[-cube_size, -cube_size, -cube_size],
                              [cube_size, -cube_size, -cube_size],
                              [cube_size, cube_size, -cube_size],
                              [-cube_size, cube_size, -cube_size],
                              [-cube_size, -cube_size, cube_size],
                              [cube_size, -cube_size, cube_size],
                              [cube_size, cube_size, cube_size],
                              [-cube_size, cube_size, cube_size]])
    rotated_cube_vertices = np.dot(R_total, cube_vertices.T).T

    # Define and draw cube faces
    faces = cube_faces(rotated_cube_vertices)
    cube_poly = Poly3DCollection(faces, facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25)
    ax.add_collection3d(cube_poly)

    return gimbal, axis_x, axis_y_prime,

# Create the animation
ani = FuncAnimation(fig, update, frames=np.arange(0, 360, 2), blit=False, interval=50)

# Show the plot
plt.show()
