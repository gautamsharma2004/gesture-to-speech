import numpy as np
import os
import matplotlib.pyplot as plt

data_dir = "raw_data"
gestures = sorted(os.listdir(data_dir))

plt.figure(figsize=(14, 5))

for gesture in gestures:
    path = os.path.join(data_dir, gesture)
    samples = [np.load(os.path.join(path, f)) for f in os.listdir(path)]
    stacked = np.stack(samples)  # (N, 200, 6)

    # Signal magnitude vector (accel only)
    smv = np.sqrt((stacked[:, :, :3] ** 2).sum(axis=2))  # (N, 200)
    mean_smv = smv.mean(axis=0)  # (200,)

    plt.plot(mean_smv, label=gesture)

plt.title("Average Signal Magnitude per Gesture")
plt.xlabel("Sample (timestep)")
plt.ylabel("Magnitude (g)")
plt.legend()
plt.tight_layout()
plt.savefig("gesture_distinctiveness.png", dpi=150)
plt.show()