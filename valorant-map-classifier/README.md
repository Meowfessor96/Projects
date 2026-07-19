# Valorant Map Classifier

Classify Valorant images using EfficientNet-B0 and transfer learning

## Setup

1. Install Tesseract OCR (needed for text blurring during preprocessing):

   - Windows: https://github.com/UB-Mannheim/tesseract/wiki
   - Mac: `brew install tesseract`
   - Linux: `sudo apt install tesseract-ocr`

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Prepare data

Place your raw screenshots in `data/raw/`. Images should follow the naming pattern:

```
valorant_ASCENT Valorant_0.jpg
valorant_BIND Valorant_44.jpg
...
```

Then run:

```bash
python -m src.prepare_data
```

This will:
- Parse filenames to extract map labels
- Optionally blur text overlays using Tesseract OCR
- Split data into `data/splits/{train,val,test}/` stratified by map

### 2. Train

```bash
python -m src.train
```

- Uses EfficientNet-B0 with ImageNet pretrained weights
- AdamW optimizer + CosineAnnealingLR
- Early stopping (patience=7) on validation accuracy
- Logs to Weights & Biases (set `USE_WANDB = False` in `src/config.py` to disable)

Best model saves to `models/best_model.pth`.

### 3. Evaluate on test set

```bash
python -m src.test
```

### 4. Run inference

```bash
python -m src.inference "data/splits/test/ASCENT/valorant_ASCENT Valorant_0.jpg"
```

Optional flags:
- `--model path/to/model.pth` — use a custom checkpoint
- `--top-k 5` — show top-5 predictions
- `--cpu` — force CPU

Note: Wrap the image path in quotes if it contains spaces.

### 5. Collect feedback on hard examples

```bash
python -m src.collect_feedback
```

An interactive prompt will show the model's top-3 predictions. Press Enter if correct, or type the right map name to save it as feedback.

### 6. Fine-tune on feedback

```bash
python -m src.fine_tune
```

Trains for 10 epochs on the collected feedback images and saves to `models/fine_tuned_model.pth`.

### 7. Compare models

```bash
python -m src.compare_models
```

Compares `best_model.pth` vs `fine_tuned_model.pth` on the test set.

### 8. Benchmark

```bash
python -m src.benchmark
```

Shows model size, average latency (ms), and throughput (FPS).

## Supported Maps

ASCENT, BIND, BREEZE, FRACTURE, HAVEN, ICEBOX, LOTUS, PEARL, SPLIT, SUNSET

## Configuration

Edit `src/config.py` to change:

| Variable | Default | Description |
|----------|---------|-------------|
| `MAPS` | 10 Valorant maps | Supported maps (order defines class index) |
| `MODEL_NAME` | `efficientnet_b0` | Backbone (`efficientnet_b0` or `resnet50`) |
| `IMAGE_SIZE` | 224 | Input resolution |
| `BATCH_SIZE` | 8 | Training batch size |
| `NUM_EPOCHS` | 30 | Max training epochs |
| `LEARNING_RATE` | 1e-4 | Initial learning rate |
| `WEIGHT_DECAY` | 1e-4 | AdamW weight decay |
| `EARLY_STOP_PATIENCE` | 7 | Epochs to wait before stopping |

## Results  
<img width="1330" height="817" alt="Image" src="https://github.com/user-attachments/assets/74fb995b-9851-40ab-bcfd-1c43ec330478" />

## Notes

- `models/`, `data/raw/`, `data/processed/`, `wandb/` are gitignored — add your own data locally
- On Windows, Tesseract defaults to `C:\Program Files\Tesseract-OCR\tesseract.exe`
- Feedback images are stored in `data/feedback/{MAP_NAME}/feedback_{N}.jpg`
