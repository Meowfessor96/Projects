"""
Fine-tune the existing best model on the user-corrected feedback dataset.
"""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from src.config import PROJECT_ROOT, BEST_MODEL_PATH, BATCH_SIZE, NUM_WORKERS, MAPS
from src.dataset import ValorantMapDataset, get_train_transforms, get_val_transforms
from src.model import build_model

FEEDBACK_DIR = PROJECT_ROOT / "data" / "feedback"

def fine_tune():
    print("=" * 60)
    print("Fine-Tuning Model on Feedback Data")
    print("=" * 60)
    
    if not FEEDBACK_DIR.exists() or len(list(FEEDBACK_DIR.rglob("*.jpg"))) == 0:
        print("❌ No feedback data found in data/feedback/")
        print("   Run `python -m src.collect_feedback` first!")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️ Device: {device}")
    
    # Load feedback data (use train transforms to augment these precious few images)
    dataset = ValorantMapDataset(FEEDBACK_DIR, transforms=get_train_transforms())
    print(f"📂 Found {len(dataset)} feedback images to learn from.")
    
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS)
    
    # Load existing best model
    checkpoint = torch.load(BEST_MODEL_PATH, map_location=device, weights_only=False)
    model = build_model(pretrained=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    
    # Fine-tuning settings: Lower learning rate so we don't "catastrophically forget" previous knowledge
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()
    
    epochs = 10  # Small number of epochs is enough for fine-tuning
    
    print(f"\n🚀 Starting fine-tuning for {epochs} epochs...\n")
    
    model.train()
    for epoch in range(epochs):
        running_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(loader, desc=f"Epoch {epoch+1}/{epochs}")
        for images, labels, _ in pbar:
            images = images.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            pbar.set_postfix({'loss': f"{loss.item():.4f}", 'acc': f"{100.*correct/total:.2f}%"})
            
    # Save the newly fine-tuned model
    fine_tuned_path = BEST_MODEL_PATH.parent / "fine_tuned_model.pth"
    torch.save({
        'model_state_dict': model.state_dict(),
        'maps': MAPS
    }, fine_tuned_path)
    
    print(f"\n🎉 Fine-tuning complete!")
    print(f"💾 New model saved to: {fine_tuned_path}")
    print("💡 Tip: You can now use this new model in inference.py by passing --model path/to/fine_tuned_model.pth")

if __name__ == "__main__":
    fine_tune()
