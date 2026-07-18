"""
Evaluate the trained model on the held-out test set.
"""
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from src.config import SPLITS_DIR, BEST_MODEL_PATH, BATCH_SIZE, NUM_WORKERS, MAPS
from src.dataset import ValorantMapDataset, get_val_transforms
from src.model import build_model

def test_model():
    print("=" * 60)
    print("Evaluating Model on Test Set")
    print("=" * 60)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️ Device: {device}")
    
    # Load test data
    test_dataset = ValorantMapDataset(SPLITS_DIR / "test", transforms=get_val_transforms())
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS)
    
    # Load best model
    checkpoint = torch.load(BEST_MODEL_PATH, map_location=device, weights_only=False)
    model = build_model(pretrained=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    print(f"✅ Loaded model from epoch {checkpoint['epoch']} (Val Acc: {checkpoint['val_acc']:.2f}%)\n")
    
    # Evaluate
    correct = 0
    total = 0
    class_correct = {m: 0 for m in MAPS}
    class_total = {m: 0 for m in MAPS}
    
    with torch.no_grad():
        for images, labels, map_names in tqdm(test_loader, desc="Testing"):
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            _, predicted = outputs.max(1)
            
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            for pred, label, map_name in zip(predicted, labels, map_names):
                class_total[map_name] += 1
                if pred == label:
                    class_correct[map_name] += 1
    
    overall_acc = 100. * correct / total
    print(f"\n🎯 Overall Test Accuracy: {overall_acc:.2f}% ({correct}/{total})")
    print("\nPer-Class Test Accuracy:")
    for m in MAPS:
        if class_total[m] > 0:
            acc = 100. * class_correct[m] / class_total[m]
            print(f"  {m:10s}: {acc:5.1f}% ({class_correct[m]}/{class_total[m]})")

if __name__ == "__main__":
    test_model()
