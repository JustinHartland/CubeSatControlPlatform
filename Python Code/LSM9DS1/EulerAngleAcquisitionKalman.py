import time
import board
import busio
import adafruit_lsm9ds1

i2c = board.I2C()
sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)

class KalmanFilter:
    def __init__(self):
        self.angle = 0.0  # Initial estimate
        self.bias = 0.0  # Gyro bias
        self.estimate_err = 0.03  # Initial estimate error
        self.gyro_err = 0.03  # Gyro noise
        self.estimate_drift = 0.01  # Drift in the estimate
        self.measurement_err = 0.03  # Measurement error

    def update(self, measurement, rate, dt):
        # Prediction
        rate_unbiased = rate - self.bias
        angle_pred = self.angle + dt * rate_unbiased
        estimate_err_pred = self.estimate_err + dt * (self.estimate_drift + self.gyro_err)

        # Update
        kalman_gain = estimate_err_pred / (estimate_err_pred + self.measurement_err)
        self.angle = angle_pred + kalman_gain * (measurement - angle_pred)
        self.bias = self.bias + kalman_gain * rate_unbiased
        self.estimate_err = (1.0 - kalman_gain) * estimate_err_pred

        return self.angle