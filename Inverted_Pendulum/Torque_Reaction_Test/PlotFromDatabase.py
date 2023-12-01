import matplotlib.pyplot as plt
import sqlite3

def fetch_imu_data_for_trial(database_name, trial_id):
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    
    cur.execute("SELECT time, torque_setpoint, torque_estimate FROM data WHERE trial_id=?", (trial_id,))
    data = cur.fetchall()
    
    conn.close()
    
    return data

def get_last_trial_id(database_name):
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    
    cur.execute("SELECT MAX(trial_id) FROM imu_data")
    last_trial_id = cur.fetchone()[0]
    
    conn.close()
    
    return last_trial_id

def plot_imu_data(data):
    # Splitting data into columns for plotting
    times, torque_setpoint, torque_estimate = zip(*data)
    
    plt.figure(figsize=(10, 8))

    plt.plot(times, torque_setpoint, label='Torque Setpoint')
    plt.plot(times, torque_estimate, label='Torque Setpoint')

    # Setting y-axis limits and adding grid lines for y-axis
    plt.ylim(-180, 180)
    plt.yticks(range(-180, 181, 30))  # Setting y-ticks every 30 degrees

    # Adding grid lines for x-axis
    x_ticks_interval = (max(times) - min(times)) / 10
    plt.xticks([min(times) + i * x_ticks_interval for i in range(11)])

    # Adding grid
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    plt.title("IMU Angles over Time")
    plt.xlabel("Time")
    plt.ylabel("Angle (degrees)")
    plt.legend()

    plt.show()

# Ask the user for the trial to plot
trial_id = int(input("Please enter the trial ID you want to plot (Enter '0' for the last trial): "))

if trial_id == 0:
    trial_id = get_last_trial_id("InvPendIMUatabase.db")

# Fetch and plot data for the selected trial
dataToPlot = fetch_imu_data_for_trial("InvPendIMUatabase.db", trial_id)
plot_imu_data(dataToPlot)