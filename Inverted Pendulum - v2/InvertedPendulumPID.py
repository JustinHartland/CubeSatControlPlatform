#Purpose: define threads needed to operate inverted pendulum

from simple_pid import PID
import struct
import time
import can
from InertialMeasurementUnit import InertialMeasurementUnit

class InvertedPendulumPID:
    def __init__(self, p, i, d, target_angle, lower_limit, upper_limit):
        
        #Setting PID constants
        self.p_parameter = p
        self.i_parameter = i
        self.d_parameter = d

        #Setup PID controller
        self.pid = PID(p, i, d, setpoint=target_angle)
        self.pid.output_limits = (lower_limit, upper_limit) #RPS bounds on motor

    #Thread to set motor velocity
    def set_vel_thread(self, current_angle, node_id, bus):
        global running
        while running:
            velocity = self.pid(current_angle)
            bus.send(can.Message(arbitration_id=(node_id << 5 | 0x0d), data=struct.pack('<ff', float(velocity), 0.0), is_extended_id=False))
            time.sleep(0.01)

    #Thread to read in orientation angle from IMU
    def read_angle_thread(imu_obj):
        global running
        while running:
            imu_obj.get_euler_angles()
            time.sleep(0.01)

    #Prints arm angle and motor velocity
    def get_pos_vel_thread(imu_obj, node_id, bus):
        global running
        while running:
            for msg in bus:
                if msg.arbitration_id == (node_id << 5 | 0x09):
                    pos, vel = struct.unpack('<ff', bytes(msg.data))
                    print(f"Roll: {imu_obj.angle_x:.2f} degrees, vel: {vel:.3f} [turns/s]")
            time.sleep(0.01)