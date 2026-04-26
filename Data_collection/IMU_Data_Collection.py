import socket
import numpy as np
import os

UDP_IP = "0.0.0.0"
UDP_PORT = 5005
WINDOW_SIZE = 200
CHUNK_SIZE = 25
NUM_CHUNKS = WINDOW_SIZE // CHUNK_SIZE  # 8

def receive_full_window(sock) -> np.ndarray:
    chunks = {}

    while len(chunks) < NUM_CHUNKS:
        data, _ = sock.recvfrom(65535)
        text = data.decode('utf-8').strip()

        # Guard against stale/malformed packets without '|'
        if '|' not in text:
            print(f"  Skipping malformed packet (no '|'): {text[:60]}")
            continue

        idx_str, payload = text.split('|', 1)

        try:
            idx = int(idx_str)
        except ValueError:
            print(f"  Bad chunk index '{idx_str}', skipping packet")
            continue

        samples = payload.strip().split(';')
        arr = []
        for s in samples:
            if not s.strip():
                continue
            parts = s.split(',')
            if len(parts) != 6:
                continue
            try:
                vals = list(map(float, parts))
                arr.append(vals)
            except ValueError:
                continue

        if len(arr) != CHUNK_SIZE:
            print(f"  Chunk {idx} malformed ({len(arr)} rows), discarding gesture.")
            print(f"  DEBUG tail: {payload[-80:]}")
            return None

        chunks[idx] = np.array(arr)  # (25, 6)

    window = np.vstack([chunks[i] for i in range(NUM_CHUNKS)])  # (200, 6)
    return window


def collect(label: str, n_samples: int = 40, save_dir: str = "raw_data"):
    os.makedirs(f"{save_dir}/{label}", exist_ok=True)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.settimeout(10)

    collected = 0
    print(f"\n[{label}] Collecting {n_samples} samples. Press button on device.")

    while collected < n_samples:
        try:
            window = receive_full_window(sock)

            if window is None:
                print("  Retrying — press button again.")
                continue

            if window.shape == (WINDOW_SIZE, 6):
                filename = f"{save_dir}/{label}/{label}_{collected:04d}.npy"
                np.save(filename, window)
                collected += 1
                print(f"  [{collected}/{n_samples}] saved: {filename}")
            else:
                print(f"  Bad shape: {window.shape}, skipping")

        except socket.timeout:
            print("  Timeout — did you press the button?")

    sock.close()
    print(f"[{label}] Done.\n")


if __name__ == "__main__":
    vocabulary = [ "yes", "no"]

    for word in vocabulary:
        input(f"\nReady to collect: '{word.upper()}'. Press ENTER to start...")
        collect(label=word, n_samples=40)