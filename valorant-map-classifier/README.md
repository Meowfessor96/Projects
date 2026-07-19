# Valorant Map Classifier

A deep learning model that classifies Valorant map screenshots using computer vision with EfficientNet-B0 and transfer learning.

## Setup

1. Install Tesseract OCR (for text blurring during preprocessing):

   - Windows: https://github.com/UB-Mannheim/tesseract/wiki
   - Mac: `brew install tesseract`
   - Linux: `sudo apt install tesseract-ocr`

2. Clone the repo and install dependencies:

   ```bash
   git clone https://github.com/<your-username>/valorant-map-classifier.git
   cd valorant-map-classifier
   pip install -r requirements.txt
   ```

3. Add your raw screenshots to `data/raw/` (images should follow the naming pattern `valorant_{MAP} ...`)

4. Prepare the dataset:

   ```bash
   python -m src.prepare_data
   ```

## Project Structure

```
valorant-map-classifier/
├── src/
│   ├── config.py          # Centralized config (paths, hyperparameters, maps)
│   ├── prepare_data.py    # Parse filenames, blur text, stratified split
│   ├── dataset.py         # PyTorch Dataset + Albumentations transforms
│   ├── model.py           # EfficientNet-B0 / ResNet50 builder
│   ├── train.py           # Training loop with W&B logging
│   ├── fine_tune.py       # Fine-tune on feedback data
│   ├── inference.py       # Predict on new images
│   ├── test.py            # Evaluate on held-out test set
│   ├── benchmark.py       # Measure latency + model size
│   ├── compare_models.py  # Compare original vs fine-tuned
│   └── collect_feedback.py # Interactive hard-example collector
├── data/
│   ├── raw/               # Put your original screenshots here
│   ├── processed/         # Blurred copies
│   └── splits/            # Auto-generated train/val/test folders
├── models/                # Saved .pth checkpoints
├── requirements.txt
├── .gitignore
└── README.md
```

## Usage

### 1. Prepare data

```bash
python -m src.prepare_data
```

Creates `data/splits/{train,val,test}/` with stratified splits.

### 2. Train

```bash
python -m src.train
```

- Uses EfficientNet-B0 with ImageNet pretrained weights
- Cosine annealing LR schedule + AdamW
- Early stopping (patience=7) on validation accuracy
- Logs to W&B (set `USE_WANDB = True` in `src/config.py`)

### 3. Evaluate

```bash
python -m src.test
```

Prints overall + per-map accuracy on the test set.

### 4. Inference

```bash
python -m src.inference "data/splits/test/ASCENT/valorant_ASCENT Valorant_0.jpg"
```

Optional flags:
- `--model path/to/model.pth` — use a custom checkpoint
- `--top-k 5` — show top-5 predictions
- `--cpu` — force CPU inference

### 5. Fine-tune on feedback

Collect hard examples:

```bash
python -m src.collect_feedback
```

Then fine-tune:

```bash
python -m src.fine_tune
```

### 6. Compare models

```bash
python -m src.compare_models
```

Compares original `best_model.pth` vs `fine_tuned_model.pth` on the test set.

### 7. Benchmark

```bash
python -m src.benchmark
```

Shows model size, avg latency (ms), and throughput (FPS).

## Configuration

Edit `src/config.py` to change:

| Variable | Default | Description |
|----------|---------|-------------|
| `MAPS` | 10 Valorant maps | Supported maps (order defines class index) |
| `MODEL_NAME` | `efficientnet_b0` | Backbone (`efficientnet_b0` or `resnet50`) |
| `IMAGE_SIZE` | 224 | Input resolution |
| `BATCH_SIZE` | 8 | Training batch size |
| `NUM_EPOCHS` | 30 | Max training epochs |
| `LEARNING_RATE` | 1e-4 | Initial LR |
| `TESSERACT_CMD` | env var | Override Tesseract executable path |

## W&B Logging

Training logs to Weights & Biases automatically. View runs at:

[Valorant Map Classifier — W&B](https://wandb.ai/thequietkid106-iit-hyderabad/valorant-map-classifier/runs/e368p570?nw=nwuserthequietkid106)

## Notes

- `models/`, `data/raw/`, `data/processed/`, `wandb/` are gitignored — add your own data locally
- For Windows, Tesseract defaults to `C:\Program Files\Tesseract-OCR\tesseract.exe` (override via `TESSERACT_CMD` env var)
- Fine-tuned models save to `models/fine_tuned_model.pth`