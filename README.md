# IoT-Based AI Jaywalking Detection System

### Smart Pedestrian Safety Monitoring Using YOLOv8, OpenCV, IR Sensors, and IoT

An intelligent road safety monitoring prototype that uses **Artificial Intelligence, Computer Vision, and Internet of Things (IoT)** technologies to identify pedestrians crossing outside designated zebra crossings.

The system combines YOLOv8 pedestrian detection, OpenCV-based zebra crossing recognition, an Arduino-connected infrared (IR) sensor, and event reporting to a remote server.

## Project Overview

Pedestrian safety is an important challenge in urban transportation. Traditional road surveillance systems often rely on manual observation, which makes continuous monitoring difficult.

This project explores an automated approach to identifying potentially unsafe pedestrian crossing behavior.

The prototype detects pedestrian movement, identifies a zebra crossing within a camera frame, and determines whether a detected person is within the estimated crossing region.

When an event is detected, the system can save an image, generate event information, and send it to a remote server.

## Key Features

- **Real-Time Pedestrian Detection:** Uses YOLOv8 to identify people in camera footage.
- **Zebra Crossing Recognition:** Uses OpenCV image-processing techniques to detect zebra crossing stripes.
- **Safe Crossing vs. Jaywalking Classification:** Compares a detected person's bounding-box position with the identified crossing region.
- **IR Sensor Integration:** Uses motion signals received from an Arduino-connected IR sensor.
- **Camera Activation:** Activates the camera in response to motion and can stop it after a period of inactivity.
- **Event Logging:** Creates timestamped records and saves captured images.
- **Remote Event Reporting:** Sends event information and encoded images to a configured server endpoint.
- **Event Cooldown:** Reduces repeated event submissions within a short interval.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main application development |
| YOLOv8 (Ultralytics) | Real-time pedestrian detection |
| OpenCV | Camera capture, image processing, motion detection |
| NumPy | Image and numerical operations |
| Arduino | Hardware-side sensor communication |
| IR Sensor | Motion detection input |
| PySerial | Serial communication between Arduino and Python |
| Requests | HTTP communication with server |
| JSON | Event data representation |
| Base64 | Encoding captured images for transmission |
| AWS-hosted endpoint | Remote event-reporting integration |

## System Workflow

```text
IR Sensor Detects Motion
          |
          v
Arduino Sends Motion Signal
          |
          v
Python Activates USB Camera
          |
          v
OpenCV Captures Video Frame
          |
          v
Zebra Crossing Detection
          |
          v
Motion Detection
          |
          v
YOLOv8 Detects Pedestrian
          |
          v
Compare Pedestrian Position
With Zebra Crossing Region
          |
      +---+---+
      |       |
      v       v
    SAFE   JAYWALKING
      |       |
      +---+---+
          |
          v
Generate Event + Timestamp
          |
          v
Save Image Locally
          |
          v
Send Event to Remote Server
```

## How the Detection Works

### 1. Motion Sensing

An IR sensor provides a motion signal through Arduino serial communication.

The Python application reads `MOTION` and `NO_MOTION` messages and uses these signals to control camera operation.

If the serial sensor is unavailable, the current prototype falls back to keeping camera monitoring active.

### 2. Camera Capture

OpenCV captures frames from a connected USB camera at a configured resolution of 640 × 480.

The camera can be stopped after a period without detected IR motion to reduce unnecessary continuous operation.

### 3. Zebra Crossing Detection

The system uses OpenCV to identify white crossing stripes through:

- Grayscale conversion
- Gaussian blur
- Thresholding
- Morphological operations
- Contour detection
- Stripe size and area filtering

When at least two qualifying stripes are detected, an estimated zebra crossing region is calculated.

### 4. Pedestrian Detection

YOLOv8 processes camera frames to identify pedestrians.

A background subtraction model is used to detect motion before running pedestrian inference, reducing unnecessary model execution when the scene is relatively inactive.

### 5. Crossing Classification

The prototype calculates the vertical center of each detected pedestrian's bounding box.

- **Safe Crossing:** The pedestrian center lies within the estimated zebra crossing region.
- **Jaywalking:** The pedestrian center lies outside that region.

This is a simplified spatial classification method designed for a controlled prototype environment. It does not independently establish whether someone has violated actual traffic rules.

### 6. Event Generation

The system generates event information containing:

- Event type
- Timestamp
- Camera location identifier
- Zebra crossing detection status
- Number of detected pedestrians
- Captured image path

The event image is saved locally and can be transmitted to a configured remote endpoint.

## Dataset and Model Training

The project includes code for preparing and training a YOLOv8 pedestrian detection model.

**Dataset:** Penn-Fudan Pedestrian Dataset

The `convert_pennfudan_to_yolo.py` script converts pedestrian segmentation masks into YOLO-compatible bounding-box annotations.

The training script uses the YOLOv8 Nano architecture with the following configuration:

| Parameter | Value |
|---|---|
| Architecture | YOLOv8 Nano |
| Detection class | Person |
| Training epochs | 50 |
| Image size | 640 |
| Batch size | 8 |
| Annotation format | YOLO bounding boxes |

The current `data.yaml` references the same image directory for training and validation. A separate validation and test split is necessary before reporting reliable generalization metrics.

## Project Structure

```text
IoT-AI-Jaywalking-Detection/
|
|-- Camera_test.py
|-- convert_pennfudan_to_yolo.py
|-- data.yaml
|-- ir_sensor.py
|-- main_detector.py
|-- spare.py
|-- test.py
|-- train_yolo.py
|-- zebra_detector.py
|-- zebra_yolo_jaywalking.py
|-- .gitignore
|-- README.md
```

The local development environment also contains training datasets, model weights, event images, and generated training outputs. These files are excluded from the public source-code repository.

## Installation and Setup

### Prerequisites

- Python 3.10 or a compatible version
- USB webcam
- Arduino and compatible IR sensor for hardware-triggered operation
- A trained YOLO model or compatible pretrained weights
- Internet access for the optional remote event-reporting feature

### 1. Clone the Repository

```bash
git clone https://github.com/Nailahzel/IoT-AI-Jaywalking-Detection.git
cd IoT-AI-Jaywalking-Detection
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Required Libraries

```bash
pip install ultralytics opencv-python numpy pyserial requests tqdm
```

### 4. Prepare Model Weights

The main detector uses a locally trained YOLO model.

Configure `YOLO_MODEL_PATH` in `main_detector.py` to point to your available weights file, such as:

```python
YOLO_MODEL_PATH = "runs/detect/train2/weights/best.pt"
```

The trained weights are not included in the GitHub repository. A new installation must provide compatible weights or train a model using the supplied scripts.

### 5. Configure the Camera and IR Sensor

Update these values in `main_detector.py` as required:

```python
IR_COM_PORT = "COM3"
IR_BAUDRATE = 9600
CAMERA_INDEX = 2
```

The Arduino should send `MOTION` or `NO_MOTION` through the serial connection.

### 6. Configure Server Reporting

The original prototype includes a hardcoded server URL. Replace this with a valid endpoint under your control before running network event reporting.

Use HTTPS and appropriate authentication if transmitting images outside the local system.

### 7. Run the Detector

```bash
python main_detector.py
```

Press `Q` in the video window to stop monitoring.

Running the full application requires the configured model weights, camera, and any required sensor hardware. A fresh installation may require additional environment-specific configuration.

## Key Challenges and Solutions

### Challenge 1: Accurate Pedestrian Detection

**Problem:** Detecting people reliably from video frames requires handling changing positions, backgrounds, and lighting.

**Approach:** Integrated YOLOv8 object detection and used a custom training workflow for pedestrian recognition.

### Challenge 2: Identifying Zebra Crossings

**Problem:** Zebra crossings contain multiple parallel stripes that may appear differently depending on camera angle and lighting.

**Approach:** Used grayscale conversion, image thresholding, morphological filtering, and contour analysis to identify likely stripe regions.

### Challenge 3: Distinguishing Safe and Unsafe Crossings

**Problem:** Detecting a pedestrian does not automatically indicate whether the crossing is safe.

**Approach:** Implemented a spatial comparison between the pedestrian's bounding-box center and the estimated zebra crossing region.

### Challenge 4: Integrating Sensors With Computer Vision

**Problem:** Hardware sensor readings and video processing operate through different interfaces.

**Approach:** Used PySerial to receive motion events from Arduino and integrated these signals into the camera-processing workflow.

### Challenge 5: Reducing Unnecessary Processing

**Problem:** Continuously processing video with an object detection model can consume substantial computing resources.

**Approach:** Added IR-triggered camera activation and background-subtraction-based motion detection to limit unnecessary processing.

### Challenge 6: Recording and Transmitting Events

**Problem:** Detection results need to be stored in a structured format for later review.

**Approach:** Created timestamped JSON event records, captured image evidence, and implemented HTTP-based server reporting.

## Limitations

- The crossing classification relies on a simplified vertical-position comparison.
- The zebra crossing detector is tuned for a controlled, cardboard-based prototype environment.
- Different camera angles and road conditions may affect accuracy.
- The current training configuration does not use an independent validation dataset.
- Real-world detection accuracy and reliability have not been independently established.
- The original code contains machine-specific camera, serial-port, model-path, and server configurations.
- Remote event reporting requires a suitable server implementation and privacy safeguards.
- This project is a prototype, not a certified traffic enforcement system.

## Future Improvements

- Improve pedestrian tracking across consecutive frames.
- Use perspective-aware crossing boundaries.
- Detect crossing events based on movement trajectories.
- Train and evaluate on larger real-road datasets.
- Add automatic notifications and a monitoring dashboard.
- Implement secure cloud storage and event authentication.
- Support multiple cameras and monitoring locations.
- Optimize inference for low-power edge devices such as Raspberry Pi or NVIDIA Jetson.

## Potential Applications

This approach may be explored for smart city research, pedestrian safety monitoring, intelligent transportation systems, traffic analysis, and IoT-based computer vision demonstrations.

