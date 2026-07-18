"""
PyTorch Dataset with Albumentations augmentations.
"""
from pathlib import Path
from typing import Callable, Optional

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset
import albumentations as A
from albumentations.pytorch import ToTensorV2

from src.config import MAP_TO_IDX, IMAGE_SIZE, AUGMENTATION_PROB

def get_train_transforms() -> A.Compose:
    """Heavy augmentation pipeline for training."""
    return A.Compose([
        A.Resize(IMAGE_SIZE, IMAGE_SIZE),
        A.HorizontalFlip(p=0.5),
        # Updated to use Affine instead of deprecated ShiftScaleRotate
        A.Affine(
            translate_percent={"x": (-0.1, 0.1), "y": (-0.1, 0.1)},
            scale=(0.8, 1.2),
            rotate=(-15, 15),
            p=0.7
        ),
        A.OneOf([
            A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=1.0),
            A.CLAHE(clip_limit=4.0, p=1.0),
        ], p=0.5),
        A.HueSaturationValue(
            hue_shift_limit=15, sat_shift_limit=20, val_shift_limit=20, p=0.5
        ),
        # Updated CoarseDropout arguments for newer Albumentations versions
        A.CoarseDropout(
            num_holes_range=(2, 8),
            hole_height_range=(5, 20),
            hole_width_range=(5, 20),
            fill=0,
            p=0.3
        ),
        # Removed var_limit to avoid warning, defaults work great
        A.GaussNoise(p=0.3),
        A.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
        ToTensorV2()
    ])
def get_val_transforms() -> A.Compose:
    """Minimal transforms for validation/test."""
    return A.Compose([
        A.Resize(IMAGE_SIZE, IMAGE_SIZE),
        A.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
        ToTensorV2()
    ])


class ValorantMapDataset(Dataset):
    """
    PyTorch Dataset for Valorant map images.
    Expects folder structure: root_dir/{map_name}/{image.jpg}
    """
    
    def __init__(
        self,
        root_dir: Path,
        transforms: Optional[A.Compose] = None,
        map_to_idx: dict = None
    ):
        self.root_dir = Path(root_dir)
        self.transforms = transforms
        self.map_to_idx = map_to_idx or MAP_TO_IDX
        
        # Collect all image paths and labels
        self.samples = []
        for map_name in self.map_to_idx.keys():
            map_dir = self.root_dir / map_name
            if not map_dir.exists():
                continue
            for img_path in map_dir.glob('*'):
                if img_path.suffix.lower() in {'.jpg', '.jpeg', '.png'}:
                    self.samples.append({
                        'path': img_path,
                        'label': self.map_to_idx[map_name],
                        'map_name': map_name
                    })
        
        if len(self.samples) == 0:
            raise ValueError(f"No images found in {root_dir}")
        
        print(f"Loaded {len(self.samples)} samples from {root_dir}")
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int):
        sample = self.samples[idx]
        
        # Load image (BGR)
        img = cv2.imread(str(sample['path']))
        if img is None:
            raise RuntimeError(f"Failed to load: {sample['path']}")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Apply transforms
        if self.transforms:
            augmented = self.transforms(image=img)
            img = augmented['image']
        else:
            img = torch.from_numpy(img).permute(2, 0, 1).float() / 255.0
        
        label = torch.tensor(sample['label'], dtype=torch.long)
        
        return img, label, sample['map_name']
