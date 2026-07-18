"""
Data preparation pipeline:
1. Parse filenames to extract map labels
2. (Optional) Blur text overlays using Tesseract OCR
3. Split into train/val/test with stratification
"""
import os
import re
import shutil
import random
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
from tqdm import tqdm

try:
    import pytesseract
    import os
    
    # FIX: Explicitly tell pytesseract where the executable is on Windows
    if os.name == 'nt':  # 'nt' means Windows
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️  pytesseract not installed. Text blurring will be skipped.")

from src.config import (
    RAW_DIR, PROCESSED_DIR, SPLITS_DIR, MAPS, MAP_TO_IDX,
    TRAIN_RATIO, VAL_RATIO, RANDOM_SEED
)


def parse_filename(filename: str) -> Tuple[str, str]:
    """
    Extract map name from filename like 'valorant_ASCENT Valorant_24.jpg'
    Returns: (map_name, original_filename)
    """
    # Pattern: valorant_{MAP} ...
    match = re.search(r"valorant_([A-Za-z]+)", filename, re.IGNORECASE)
    if not match:
        return None, filename
    
    map_name = match.group(1).upper()
    
    # Normalize map names (handle variations)
    map_aliases = {
        "ASCENT": "ASCENT", "BIND": "BIND", "BREEZE": "BREEZE",
        "FRACTURE": "FRACTURE", "HAVEN": "HAVEN", "ICEBOX": "ICEBOX",
        "LOTUS": "LOTUS", "PEARL": "PEARL", "SPLIT": "SPLIT",
        "SUNSET": "SUNSET", "ABYSS": "ABYSS"
    }
    
    map_name = map_aliases.get(map_name, map_name)
    return map_name, filename


def blur_text_in_image(img_path: Path, output_path: Path) -> bool:
    """
    Detect text in image using Tesseract and blur those regions.
    Returns True if text was found and blurred, False otherwise.
    """
    if not TESSERACT_AVAILABLE:
        return False
    
    img = cv2.imread(str(img_path))
    if img is None:
        return False
    
    # Get text bounding boxes using Tesseract
    # Using OSD (orientation and script detection) for box locations
    try:
        h, w = img.shape[:2]
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        
        blurred = False
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            conf = int(data['conf'][i])
            
            # Only blur if text is detected with reasonable confidence
            # and is not just a single character (likely noise)
            if text and len(text) > 1 and conf > 30:
                x, y, w_box, h_box = (
                    data['left'][i], data['top'][i],
                    data['width'][i], data['height'][i]
                )
                
                # Add padding around text region
                pad = 10
                x1 = max(0, x - pad)
                y1 = max(0, y - pad)
                x2 = min(w, x + w_box + pad)
                y2 = min(h, y + h_box + pad)
                
                # Apply Gaussian blur to the text region
                roi = img[y1:y2, x1:x2]
                blurred_roi = cv2.GaussianBlur(roi, (25, 25), 0)
                img[y1:y2, x1:x2] = blurred_roi
                blurred = True
        
        if blurred:
            cv2.imwrite(str(output_path), img)
            return True
        else:
            # No text found, just copy original
            shutil.copy(img_path, output_path)
            return False
            
    except Exception as e:
        print(f"Error processing {img_path}: {e}")
        shutil.copy(img_path, output_path)
        return False


def prepare_images(blur_text: bool = True) -> List[Tuple[Path, str]]:
    """
    Process all raw images:
    - Parse filenames for labels
    - Optionally blur text
    Returns list of (processed_image_path, map_name)
    """
    print("📂 Scanning raw images...")
    
    if not RAW_DIR.exists():
        raise FileNotFoundError(f"Raw data directory not found: {RAW_DIR}")
    
    image_files = [f for f in RAW_DIR.iterdir() 
                   if f.suffix.lower() in {'.jpg', '.jpeg', '.png'}]
    
    print(f"Found {len(image_files)} images")
    
    processed_data = []
    skipped_maps = set()
    
    for img_path in tqdm(image_files, desc="Processing images"):
        map_name, _ = parse_filename(img_path.name)
        
        if map_name is None:
            print(f"⚠️  Could not parse: {img_path.name}")
            continue
        
        if map_name not in MAPS:
            skipped_maps.add(map_name)
            continue
        
        output_path = PROCESSED_DIR / img_path.name
        
        if blur_text and TESSERACT_AVAILABLE:
            blur_text_in_image(img_path, output_path)
        else:
            if not output_path.exists():
                shutil.copy(img_path, output_path)
        
        processed_data.append((output_path, map_name))
    
    if skipped_maps:
        print(f"⚠️  Skipped unknown maps: {skipped_maps}")
    
    print(f"✅ Processed {len(processed_data)} images")
    return processed_data


def split_data(data: List[Tuple[Path, str]]) -> None:
    """
    Split data into train/val/test with stratification by map.
    Creates folder structure: splits/{train,val,test}/{MAP_NAME}/image.jpg
    """
    print("\n🔀 Splitting data...")
    
    # Group by map
    by_map = {m: [] for m in MAPS}
    for img_path, map_name in data:
        by_map[map_name].append(img_path)
    
    # Print class distribution
    print("\nClass distribution:")
    for m in MAPS:
        print(f"  {m:10s}: {len(by_map[m]):3d} images")
    
    # Clear splits directory
    if SPLITS_DIR.exists():
        shutil.rmtree(SPLITS_DIR)
    SPLITS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Split each class
    random.seed(RANDOM_SEED)
    
    for map_name, images in by_map.items():
        random.shuffle(images)
        n = len(images)
        n_train = int(n * TRAIN_RATIO)
        n_val = int(n * (TRAIN_RATIO + VAL_RATIO))
        
        splits = {
            'train': images[:n_train],
            'val': images[n_train:n_val],
            'test': images[n_val:]
        }
        
        for split_name, split_images in splits.items():
            split_dir = SPLITS_DIR / split_name / map_name
            split_dir.mkdir(parents=True, exist_ok=True)
            
            for img_path in split_images:
                dest = split_dir / img_path.name
                shutil.copy(img_path, dest)
    
    # Print split sizes
    print("\nSplit sizes:")
    for split_name in ['train', 'val', 'test']:
        split_dir = SPLITS_DIR / split_name
        total = sum(1 for _ in split_dir.rglob('*') if _.is_file())
        print(f"  {split_name:5s}: {total} images")


def main():
    print("=" * 60)
    print("Valorant Map Classifier - Data Preparation")
    print("=" * 60)
    
    # Step 1: Process images (with optional text blurring)
    data = prepare_images(blur_text=True)
    
    # Step 2: Split into train/val/test
    split_data(data)
    
    print("\n🎉 Data preparation complete!")
    print(f"📁 Processed images: {PROCESSED_DIR}")
    print(f"📁 Split data: {SPLITS_DIR}")


if __name__ == "__main__":
    main()
