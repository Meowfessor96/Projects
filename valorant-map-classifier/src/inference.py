"""
Inference script: load trained model and predict on new images.
"""
import argparse
from pathlib import Path

import cv2
import torch
import numpy as np

from src.config import MAPS, BEST_MODEL_PATH, IMAGE_SIZE
from src.dataset import get_val_transforms


def load_model(model_path: Path = BEST_MODEL_PATH, device: str = "cuda"):
    """Load trained model from checkpoint."""
    from src.model import build_model
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    checkpoint = torch.load(model_path, map_location=device, weights_only=False)
    
    model = build_model(pretrained=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    print(f"✅ Loaded model from {model_path}")
    
    # Handle both training checkpoints and fine-tuned checkpoints
    if 'epoch' in checkpoint and 'val_acc' in checkpoint:
        print(f"   Trained at epoch {checkpoint['epoch']} with val_acc {checkpoint['val_acc']:.2f}%")
    else:
        print(f"   Fine-tuned model loaded successfully")
    
    return model, checkpoint.get('maps', MAPS)
def predict_image(model, image_path: Path, device: str = "cuda", top_k: int = 3):
    """
    Predict map for a single image.
    Returns: list of (map_name, confidence) tuples
    """
    # Load and preprocess
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    transforms = get_val_transforms()
    augmented = transforms(image=img)
    img_tensor = augmented['image'].unsqueeze(0).to(device)
    
    # Predict
    with torch.no_grad():
        outputs = model(img_tensor)
        probs = torch.softmax(outputs, dim=1)[0]
        top_probs, top_indices = probs.topk(top_k)
    
    results = []
    for prob, idx in zip(top_probs, top_indices):
        results.append((MAPS[idx.item()], prob.item() * 100))
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Predict Valorant map from image")
    parser.add_argument("image", type=Path, help="Path to image file")
    parser.add_argument("--model", type=Path, default=BEST_MODEL_PATH, help="Model path")
    parser.add_argument("--top-k", type=int, default=3, help="Number of top predictions")
    parser.add_argument("--cpu", action="store_true", help="Force CPU")
    args = parser.parse_args()
    
    device = "cpu" if args.cpu else ("cuda" if torch.cuda.is_available() else "cpu")
    
    model, maps = load_model(args.model, device)
    predictions = predict_image(model, args.image, device, args.top_k)
    
    print(f"\n🎯 Predictions for: {args.image.name}")
    print("-" * 40)
    for i, (map_name, conf) in enumerate(predictions, 1):
        bar = "█" * int(conf / 2)
        print(f"  {i}. {map_name:10s} {conf:5.2f}% {bar}")


if __name__ == "__main__":
    main()
