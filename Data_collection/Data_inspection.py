import matplotlib.pyplot as plt
import numpy as np
import os

data_dir = "raw_data"
gestures = sorted(os.listdir(data_dir))

fig, axes = plt.subplots(len(gestures), 2, figsize=(14, 3 * len(gestures)))
axis_labels = ['ax', 'ay', 'az', 'gx', 'gy', 'gz']

for row, gesture in enumerate(gestures):
    path = os.path.join(data_dir, gesture)
    sample = np.load(os.path.join(path, os.listdir(path)[0]))  # first sample

    # Accel plot
    axes[row, 0].plot(sample[:, :3])
    axes[row, 0].set_title(f"{gesture} — Accelerometer")
    axes[row, 0].legend(['ax', 'ay', 'az'])
    axes[row, 0].set_ylabel("g")

    # Gyro plot
    axes[row, 1].plot(sample[:, 3:])
    axes[row, 1].set_title(f"{gesture} — Gyroscope")
    axes[row, 1].legend(['gx', 'gy', 'gz'])
    axes[row, 1].set_ylabel("deg/s")

plt.tight_layout()
plt.savefig("data_inspection.png", dpi=150)
plt.show()
print("Saved: data_inspection.png")