"""
Configuration file for the Valorant Map Classifier.
All paths, hyperparameters, and map names are centralized here.
"""
from pathlib import Path
import os

# ============ PATHS ============
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
SPLITS_DIR = DATA_DIR / "splits"
MODELS_DIR = PROJECT_ROOT / "models"

# Create directories if they don't exist
for d in [RAW_DIR, PROCESSED_DIR, SPLITS_DIR, MODELS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ============ MAPS ============
# Order matters - this becomes the class index mapping
MAPS = [
    "ASCENT", "BIND", "BREEZE", "FRACTURE", "HAVEN",
    "ICEBOX", "LOTUS", "PEARL", "SPLIT", "SUNSET"
]
MAP_TO_IDX = {m: i for i, m in enumerate(MAPS)}
IDX_TO_MAP = {i: m for i, m in enumerate(MAP_TO_IDX.items())}
NUM_CLASSES = len(MAPS)

# ============ DATA SPLITS ============
TRAIN_RATIO = 0.7
VAL_RATIO = 0.15
TEST_RATIO = 0.15
RANDOM_SEED = 42

# ============ MODEL ============
MODEL_NAME = "efficientnet_b0"
IMAGE_SIZE = 224  # EfficientNet-B0 input size
BATCH_SIZE = 8
NUM_WORKERS = 4

# ============ TRAINING ============
NUM_EPOCHS = 30
LEARNING_RATE = 1e-4
WEIGHT_DECAY = 1e-4
EARLY_STOP_PATIENCE = 7

# ============ AUGMENTATION ============
AUGMENTATION_PROB = 0.7  # Probability of applying each augmentation

# ============ WANDB ============
WANDB_PROJECT = "valorant-map-classifier"
WANDB_ENTITY = None  # Set to your W&B username/org, or None for default
USE_WANDB = True     # Set to False if you don't want W&B logging

# ============ INFERENCE ============
BEST_MODEL_PATH = MODELS_DIR / "best_model.pth"
