# Gesture-to-speech Assistive Device
A wrist worn assistive communication device for mute individuals.
It converts hand gestures into spoken words using ESP32S3 N16R8 + MPU6050 + 1D CNN

##Demo pipeline

Button press=> IMU capture (100Hz) => Wifi UDP => 1D CNN => TTS audio output

## Hardware
| Component | Purpose |
|---|---|
| ESP32-S3 DevKit | Main MCU + WiFi |
| MPU6050 (GY-521) | 6-axis IMU (accel + gyro) |
| LiPo 500mAh | Power |
| Push button | Gesture trigger |

## Wiring
| ESP32-S3 | MPU6050 |
|---|---|
| 3.3V | VCC |
| GND | GND |
| GPIO8 | SDA |
| GPIO9 | SCL |
| GND | AD0 |

## Project Structure
gesture-to-speech/
├── firmware/              # ESP32-S3 Arduino firmware
├── data_collection/       # UDP data collection script
├── training/              # Kaggle training notebook
├── inference/             # Real-time inference + TTS server
├── models/                # Model files (see models/README.md)
└── README.md

## Workflow
### 1. Flash Firmware
- open 'firmware/gesture_firmware.ino' in arduino IDE
- update SSID, password and hostIP with your details.
- Flash to ESP32S3

### 2.  Collect Gesture Data
'''bash
pip install numpy
python data_collection/collect_data.py
'''
- Data saves to 'raw_data/<gesture_name>/' as '.npy' files
- Default: 40 samples per gesture

### 3. Train Model
- upload 'raw_data/' to kaggle as a dataset.
- Run 'training/gesture_training.ipynb' on kaggle (CPU).
- Download output: 'gesture_model.onnx', 'label_map.json', 'gesture_model.onnx.data'
- Place all four  files in 'models/'

### 4. Run inference Server
'''bash
pip install onnxruntime numpy
python inference/inference_server.py
'''
- Press button on wrist device
- Predicted word is spoken aloud via TTS
## Current vocabulary
'yes', 'no'

## Model Performance
| Classes | Samples/class | Val Accuracy |
|---|---|---|
| 2 (yes, no) | 40 | 100% |
| 6 | 15 | 94% |

## We will expand vocabulary to 30-40 words in future.

## Known Limitations
- Single MPU6050 captures wrist motion only - No finger position data.
- Per-user Calibration not yet implemented (Model trained on single user).
- WiFi dependant.


## tech Stack
- **Firmware:** Arduino C++(ESP32 framework).
- **Data Collection:** Python, Numpy, UDP sockets
- **Training:** PyTorch, 1D-CNN, Kaggle
- **Inference:** ONNX Runtime,  Python
- **TTS:** Windows Speech Synthesis  (Powershell)
