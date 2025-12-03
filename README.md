# vehicle-capture-training

A simple tool for capturing images from a network-connected camera (e.g. RTSP) and building a dataset for training.

## ✅ What is this project?

This repository provides scripts to capture frames/images from a camera stream (RTSP or local network), manage datasets, and help train models.  
It is useful when building custom datasets from CCTV/IP cameras (e.g. for vehicle detection or other computer-vision tasks).

## 📦 Contents / Key Files

- `getimg.py` — capture images from a camera stream  
- `tapo_capture_dataset.py` — capture images from a Tapo or similar camera  
- `train.py` — train a model using the captured dataset  
- `test.py`, `aws_test.py`, `aws_send.py` — testing and AWS communication scripts  
- `dataset.yaml` — dataset configuration  
- `*.pt` — model weights (e.g. `yolo11n.pt`, `yolov8n.pt`)  
- `.gitignore` — ignore rules for sensitive or large files  

## 🛠️ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YourUsername/vehicle-capture-training.git
cd vehicle-capture-training
```

### 2. Install dependencies

Create a virtual environment (optional but recommended):

```bash
python -m venv venv
```

Windows:

```bash
.
env\Scripts ctivate
```

Mac/Linux:

```bash
source venv/bin/activate
```

Install dependencies (if you add a requirements file):

```bash
pip install -r requirements.txt
```

### 3. Configure your camera and dataset

Edit your camera URL inside the capture script:

```python
# Inside getimg.py or tapo_capture_dataset.py
camera_url = "rtsp://YOUR_CAMERA_URL"
```

Modify `dataset.yaml` if needed.

### 4. Capture images

```bash
python getimg.py
```

(or use `tapo_capture_dataset.py` depending on your device)

### 5. Train the model

```bash
python train.py
```

### 6. Test the model

```bash
python test.py
```

If using AWS-related features:

```bash
python aws_test.py
python aws_send.py
```

## 🎯 Intended Use Cases

- Building custom datasets from IP cameras  
- Training vehicle-detection or object-detection models  
- Rapid machine-learning prototyping with custom captured data  
- Automated data-capture → train → test pipelines  
