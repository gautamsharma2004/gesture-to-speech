import numpy as np
import os

data_dir = "raw_data"

for gesture in sorted(os.listdir(data_dir)):
    gesture_path = os.path.join(data_dir, gesture)
    files = os.listdir(gesture_path)
    samples = []
    corrupt = []

    for f in files:
        arr = np.load(os.path.join(gesture_path, f))
        if arr.shape == (200, 6):
            samples.append(arr)
        else:
            corrupt.append(f)

    print(f"\n[{gesture}]")
    print(f"  Total files : {len(files)}")
    print(f"  Valid shapes: {len(samples)}")
    print(f"  Corrupt     : {corrupt}")

    if samples:
        stacked = np.stack(samples)  # (N, 200, 6)
        print(f"  Accel range : {stacked[:,:,:3].min():.3f} to {stacked[:,:,:3].max():.3f} g")
        print(f"  Gyro range  : {stacked[:,:,3:].min():.3f} to {stacked[:,:,3:].max():.3f} deg/s")