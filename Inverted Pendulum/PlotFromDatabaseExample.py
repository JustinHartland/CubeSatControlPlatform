import matplotlib.pyplot as plt
import sqlite3

def fetch_imu_data_for_trial(database_name, trial_id):
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    
    cur.execute("SELECT time, angle_x FROM imu_data WHERE trial_id=?", (trial_id,))
    data = cur.fetchall()
    
    conn.close()
    
    return data

def plot_imu_data(data):
    # Splitting data into columns for plotting
    times, angles_x = zip(*data)
    
    plt.figure(figsize=(10, 6))

    plt.plot(times, angles_x, label='Angle X')


    plt.title("IMU Angles over Time")
    plt.xlabel("Time")
    plt.ylabel("Angle (degrees)")
    plt.legend()

    plt.show()

#Plot data
dataToPlot = fetch_imu_data_for_trial("InvPendDatabase.db", 4)
plot_imu_data(dataToPlot)

