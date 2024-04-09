import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib import rc

def euler_to_dcm(phi, theta, psi):
    # Rotation matrix for phi about Z-axis
    R1 = np.array([[np.cos(phi), np.sin(phi), 0],
                   [-np.sin(phi), np.cos(phi), 0],
                   [0, 0, 1]])

    # Rotation matrix for theta about X-axis
    R2 = np.array([[1, 0, 0],
                   [0, np.cos(theta), np.sin(theta)],
                   [0, -np.sin(theta), np.cos(theta)]])

    # Rotation matrix for psi about Z-axis
    R3 = np.array([[np.cos(psi), np.sin(psi), 0],
                   [-np.sin(psi), np.cos(psi), 0],
                   [0, 0, 1]])

    # DCM is the product of the three rotations
    dcm = R3 @ R2 @ R1
    return dcm

# Example encoder angle data (in radians)
phi = np.linspace(0, 2*np.pi, 100)  # Simulated angle data
theta = np.sin(phi / -2 / np.pi) * 2 * np.pi
psi = np.log(phi+1) * 2 * np.pi / np.log(2 * np.pi + 1)
time = np.linspace(0, 10, 100)  # Simulate time array (for example, 10 seconds)

# Create a plot for the Euler angles vs. time
plt.figure(figsize=(10, 6))

plt.plot(time, phi, label='Phi')
plt.plot(time, theta, label='Theta')
plt.plot(time, psi, label='Psi')

plt.title('Euler Angles vs Time')
plt.xlabel('Time [s]')
plt.ylabel('Angle [rad]')
plt.legend()

plt.show()

# Fixed vector in body frame
body_vector = np.array([1, 0, 0])  # Example vector along the x-axis

# Cube vertices
vertices = np.array([[-1, -1, -1],
                     [1, -1, -1],
                     [1, 1, -1],
                     [-1, 1, -1],
                     [-1, -1, 1],
                     [1, -1, 1],
                     [1, 1, 1],
                     [-1, 1, 1]])

# Edges of the cube
edges = [[vertices[j] for j in [0, 1, 2, 3, 0, 4, 5, 6, 7, 4, 5, 1, 2, 6, 7, 3]]]

# Body-fixed axes
axes = np.array([[2, 0, 0],  # x-axis
                 [0, 2, 0],  # y-axis
                 [0, 0, 2]]) # z-axis

# Set the font to Times New Roman
rc('font', family='serif')
rc('font', serif='Times New Roman')

def animate(i):
    ax.clear()
    dcm = euler_to_dcm(phi[i], theta[i], psi[i])
    rotated_vertices = np.dot(vertices, dcm.T)
    rotated_axes = np.dot(axes, dcm.T)

    # Draw the cube
    poly = Poly3DCollection([rotated_vertices[[0, 1, 2, 3]], 
                             rotated_vertices[[4, 5, 6, 7]], 
                             rotated_vertices[[0, 1, 5, 4]], 
                             rotated_vertices[[2, 3, 7, 6]], 
                             rotated_vertices[[1, 2, 6, 5]], 
                             rotated_vertices[[4, 7, 3, 0]]], 
                            facecolors='cyan', linewidths=1, edgecolors='r', alpha=0.25)
    ax.add_collection3d(poly)

    # Draw body-fixed axes
    origin = [0, 0, 0]
    for axis, color in zip(rotated_axes, ['red', 'green', 'blue']):
        ax.quiver(*origin, *axis, color=color, arrow_length_ratio=0.1)

    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_zlim(-3, 3)
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    ax.set_title('CubeSat-Fixed Reference Frame Rotating')

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
ax.set_box_aspect([1, 1, 1])  # Equal aspect ratio

ani = animation.FuncAnimation(fig, animate, frames=len(phi), interval=50)

plt.show()