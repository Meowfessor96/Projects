# 🎯 Valorant Real-Time Object Detection using YOLOv8



#### Pre-requisites :

install dependencies

```Python
pip install -r requirements.txt
```

## 📌 Overview

This project implements a high-performance, real-time object detection system tailored for Valorant gameplay footage. Using the **YOLOv8s** architecture, the model accurately detects in-game entities such as **enemies, teammates, dropped spikes, and planted spikes**. The system is optimized for low-latency inference, making it highly suitable for real-time gameplay analysis and AI-assisted applications.

## 🚀 Features

- **High Accuracy**: Achieved **99.5% mAP@50** and **99.5% Precision** on the unseen test set.
- **Real-Time Inference**: Processes frames at **~11ms per frame (~90 FPS)** on an NVIDIA RTX 3050 GPU.
- **Multi-Class Detection**: Accurately identifies 4 distinct classes: `enemy`, `teammate`, `dropped spike`, and `planted spike`.
- **Custom Dataset**: Trained on a custom dataset of 8,900+ annotated frames downloaded and augmented via Roboflow.
- **Data Augmentation**: Utilized Mosaic, HSV adjustments, and flips to ensure robust model generalization and zero overfitting.

## 🛠️ Tech Stack

- **Deep Learning**: PyTorch, Ultralytics YOLOv8
- **Computer Vision**: OpenCV
- **Data Management**: Roboflow API, Pandas
- **Visualization**: Matplotlib
- **Hardware**: NVIDIA RTX 3050 Laptop GPU (CUDA 12.1)

## 📊 Dataset

The dataset was sourced and annotated using **Roboflow**. It consists of diverse gameplay frames featuring:

- **Classes**: `dropped spike`, `enemy`, `planted spike`, `teammate`
- **Train Set**: 6,927 images
- **Validation Set**: 1,983 images
- **Test Set**: 988 images

## 📈 Results & Evaluation

| Metric              | Validation Set | Test Set (Unseen) |
| :------------------ | :------------: | :---------------: |
| **mAP@50**    |     0.994     |  **0.995**  |
| **mAP@50-95** |     0.756     |  **0.767**  |
| **Precision** |     0.996     |  **0.995**  |
| **Recall**    |     0.994     |  **0.993**  |

*The model demonstrates excellent generalization, with test set performance matching and slightly exceeding validation metrics, indicating zero overfitting.*
