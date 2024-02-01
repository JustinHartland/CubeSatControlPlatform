from simple_pid import PID
import struct
import time
import can
from as5048b import as5048b

class motor_controller:
    def __init__(self, p, i, d, setpoint, lower_limit, upper_limit):
        #Setting PID constraints
        self.p_parameter = p
        self.i_parameter = i
        self.d_parameter = d

        #Setup PID controller
        self.pid = PID(p, i, d, setpoint)
        self.pid.output_limits = (lower_limit, upper_limit)

    # Function to set torque for a specific O-Drive
    def set_torque(self, encoder_obj, node_id, bus, running):
        while running.is_set():
            torque = self.pid(encoder_obj.angle)
            bus.send(can.Message(
                arbitration_id=(node_id << 5 | 0x0E),  # 0x0E: Set_Input_Torque
                data=struct.pack('<f', torque),
                is_extended_id=False
            ))
            #print(f"Successfully set ODrive {node_id} to {torque} [Nm]")
            time.sleep(0.001)
