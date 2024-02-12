import csv
from statistics import variance
from unittest.mock import DEFAULT
import rospy
import numpy as np
from geometry_msgs.msg import WrenchStamped
from trajectory_msgs.msg import JointTrajectory
from std_msgs.msg import String
import numpy as np
import matplotlib.pyplot as plt

class FTrecording():
  def __init__(self):
    
    self.start_time = 0
    self.start_recording = False
    self.force_torque_stamped_datas = []
    self.force_torque = []
    self.force_torque_cache = []

    self.offset = []
    self.force_torque_avg = []
    self.fr_list = []
    
    # Sensor subscribers 
    rospy.Subscriber(
        '/NordboLRS6_node/wrench', WrenchStamped, self.cb_force_torque)
    # Robot Controller
    self.pos_controller = rospy.Publisher('/scaled_pos_joint_traj_controller/command',
                                          JointTrajectory, queue_size=20)
    self.pub = rospy.Publisher('mode', String, queue_size=10)
    
  def flush_data(self):
    """ Clear the stored data. """
    self.start_time = 0
    self.start_recording = False
    self.force_torque_stamped_datas = []
    self.fr_list = []

  def cb_force_torque(self, msg):
    """ Force Torque data callback. """
    
    self.force_torque = [msg.wrench.force.x, msg.wrench.force.y, msg.wrench.force.z,
                  msg.wrench.torque.x, msg.wrench.torque.y, msg.wrench.torque.z]
    if self.offset != []:
      for i in range(6):
        self.force_torque[i] = self.force_torque[i] - self.offset[i]
      
    self.force_torque_cache.append(self.force_torque)
    if len(self.force_torque_cache) > 500:
      self.force_torque_cache = self.force_torque_cache[-500:]
    self.force_torque_avg = np.mean(self.force_torque_cache, axis=0)
        
    if not self.start_recording:
      return

    self.force_x = msg.wrench.force.x
    
    time = msg.header.stamp.secs + 1e-9 * msg.header.stamp.nsecs
    
    self.force_torque_stamped_datas.append(
        (time, self.force_torque))

    self.fr_list.append(np.sqrt(self.force_torque[0]**2 + self.force_torque[1]**2))

  def tare(self):
    if self.offset == []:
      self.offset = self.force_torque_avg
    else:
      for i in range(6):
        self.offset[i] = self.force_torque_avg[i] + self.offset[i]

  def save_csv(self, file_path="zzzzz"):
      """ Triggered at exit, save time-to-file in csv. """
      # Save the force torque csv data
      force_torque_csv_path = f'{file_path}_force_torque.csv'
      with open(force_torque_csv_path, mode='w') as f:
        writer = csv.DictWriter(f, fieldnames = [
            'time', 'fx', 'fy', 'fz', 'tx', 'ty', 'tz'], delimiter=' ')
        writer.writeheader()
        for time, force_torque in self.force_torque_stamped_datas:
          writer.writerow({'time': time - self.start_time, 'fx': force_torque[0],
                          'fy': force_torque[1], 'fz': force_torque[2],
                          'tx': force_torque[3], 'ty': force_torque[4],
                          'tz': force_torque[5]})
  
  def record_force_torque(self, time=2, file_path="zzzzz"):
    print("Initializing...")
    rospy.sleep(2)
    self.flush_data()
    self.tare()
    print("Start recording...")
    self.start_recording = True
    rospy.sleep(time)
    self.start_recording = False
    self.save_csv(file_path)
    print(f'File saved to {file_path}_force_torque.csv')
    self.draw()

  def draw(self):
     # Extract the data
    times = [data[0] for data in self.force_torque_stamped_datas]
    forces_and_torques = [data[1] for data in self.force_torque_stamped_datas]
    # Transpose the forces_and_torques list for easier plotting
    forces_and_torques = np.array(forces_and_torques).T
    # Multiple figures
    # Create a figure and subplots (6 subplots arranged in 2 rows and 3 columns)
    fig, axs = plt.subplots(2, 3, figsize=(12, 8))
    # Define colors and labels for each curve
    colors = ['b', 'g', 'r', 'c', 'm', 'y']
    labels = ['Force X', 'Force Y', 'Force Z', 'Torque X', 'Torque Y', 'Torque Z']
    # Plot each curve with a different color and label in the corresponding subplot
    for i in range(6):
        row = i // 3  # Determine the row for the current subplot (0 or 1)
        col = i % 3   # Determine the column for the current subplot (0, 1, or 2)
        axs[row, col].plot(times, forces_and_torques[i], color=colors[i], label=labels[i])
        axs[row, col].set_xlabel('Time')
        axs[row, col].set_ylabel('Values')
        axs[row, col].set_title(labels[i])
    axs[0, 0].legend(loc='upper right')
    plt.tight_layout()
    plt.savefig('plots/force_torque_subplots.png')
    plt.show()

if __name__ == '__main__':
  rospy.init_node("record_custom_stirring", anonymous=True)
  ft = FTrecording()
  ft.record_force_torque(2, "test")