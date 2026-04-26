# inference_server.py
import socket
import numpy as np
import onnxruntime as ort
import json
import subprocess
import threading

# ─── CONFIG ───────────────────────────────────────────
UDP_IP   = "0.0.0.0"
UDP_PORT = 5005
WINDOW_SIZE  = 200
CHUNK_SIZE   = 25
NUM_CHUNKS   = WINDOW_SIZE // CHUNK_SIZE  # 8
CONFIDENCE_THRESHOLD = 0.65
MODEL_PATH = "gesture_model.onnx"
LABEL_PATH = "label_map.json"

# ─── LOAD MODEL ───────────────────────────────────────
session    = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
input_name = session.get_inputs()[0].name

with open(LABEL_PATH) as f:
    label_map = {int(k): v for k, v in json.load(f).items()}

print(f"Label map: {label_map}")
print(f"Model loaded. Classes: {list(label_map.values())}")

# ─── RECEIVE ──────────────────────────────────────────
def receive_full_window(sock) -> np.ndarray:
    chunks = {}
    while len(chunks) < NUM_CHUNKS:
        data, _ = sock.recvfrom(65535)
        text = data.decode('utf-8').strip()

        if '|' not in text:
            print(f"  Skipping malformed packet: {text[:40]}")
            continue

        idx_str, payload = text.split('|', 1)
        try:
            idx = int(idx_str)
        except ValueError:
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
                arr.append(list(map(float, parts)))
            except ValueError:
                continue

        if len(arr) != CHUNK_SIZE:
            print(f"  Chunk {idx} bad ({len(arr)} rows), discarding gesture.")
            return None

        chunks[idx] = np.array(arr)

    return np.vstack([chunks[i] for i in range(NUM_CHUNKS)])  # (200, 6)

# ─── PREPROCESS ───────────────────────────────────────
def preprocess(window: np.ndarray) -> np.ndarray:
    # No normalization — model was trained on raw data
    return window.T[np.newaxis, :, :].astype(np.float32)  # (1, 6, 200)

# ─── CLASSIFY ─────────────────────────────────────────
def classify(window: np.ndarray):
    inp    = preprocess(window)
    logits = session.run(None, {input_name: inp})[0]

    # Debug prints
    print(f"  Input stats   — min: {inp.min():.3f}, max: {inp.max():.3f}, mean: {inp.mean():.3f}")
    print(f"  Raw logits    — {logits}")

    e     = np.exp(logits - logits.max())
    probs = e / e.sum()
    print(f"  Probabilities — {dict(zip(label_map.values(), probs[0].round(3)))}")

    idx  = int(np.argmax(probs))
    conf = float(probs[0, idx])
    return label_map[idx], conf

# ─── TTS ──────────────────────────────────────────────
def speak(text: str):
    print(f"  >> Speaking: '{text}'")
    try:
        subprocess.run([
            "powershell", "-Command",
            f"Add-Type -AssemblyName System.Speech; "
            f"$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$s.Speak('{text}')"
        ], check=True)
    except Exception as e:
        print(f"  TTS error: {e}")

# ─── MAIN ─────────────────────────────────────────────
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.settimeout(15)
    print(f"Listening on UDP port {UDP_PORT}...")
    print("Press button on device to classify gesture.\n")

    while True:
        try:
            window = receive_full_window(sock)

            if window is None:
                print("  Bad capture, press button again.")
                continue

            label, conf = classify(window)
            print(f"Prediction: '{label}' (confidence: {conf:.2%})\n")

            if conf >= CONFIDENCE_THRESHOLD:
                threading.Thread(target=speak, args=(label,), daemon=True).start()
            else:
                print(f"  Confidence too low ({conf:.2%}), ignoring.\n")

        except socket.timeout:
            print("  Waiting for gesture...")

if __name__ == "__main__":
    main()
