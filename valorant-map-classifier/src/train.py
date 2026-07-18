"""
Training loop with validation, early stopping, and W&B logging.
"""
import os
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False

from src.config import (
    SPLITS_DIR, MODELS_DIR, NUM_EPOCHS, LEARNING_RATE, WEIGHT_DECAY,
    BATCH_SIZE, NUM_WORKERS, EARLY_STOP_PATIENCE, USE_WANDB,
    WANDB_PROJECT, WANDB_ENTITY, BEST_MODEL_PATH, MAPS, MODEL_NAME
)

from src.dataset import ValorantMapDataset, get_train_transforms, get_val_transforms
from src.model import build_model, count_parameters


def get_dataloaders():
    """Create train and validation dataloaders."""
    train_dataset = ValorantMapDataset(
        SPLITS_DIR / "train",
        transforms=get_train_transforms()
    )
    val_dataset = ValorantMapDataset(
        SPLITS_DIR / "val",
        transforms=get_val_transforms()
    )
    
    train_loader = DataLoader(
        train_dataset, batch_size=BATCH_SIZE, shuffle=True,
        num_workers=NUM_WORKERS, pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset, batch_size=BATCH_SIZE, shuffle=False,
        num_workers=NUM_WORKERS, pin_memory=True
    )
    
    return train_loader, val_loader


def train_one_epoch(model, loader, criterion, optimizer, device):
    """Train for one epoch."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    pbar = tqdm(loader, desc="Training", leave=False)
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
        
        pbar.set_postfix({
            'loss': f"{loss.item():.4f}",
            'acc': f"{100. * correct / total:.2f}%"
        })
    
    epoch_loss = running_loss / total
    epoch_acc = 100. * correct / total
    return epoch_loss, epoch_acc


def validate(model, loader, criterion, device):
    """Validate model."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    # Per-class accuracy tracking
    class_correct = {m: 0 for m in MAPS}
    class_total = {m: 0 for m in MAPS}
    
    with torch.no_grad():
        for images, labels, map_names in loader:
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            # Per-class stats
            for pred, label, map_name in zip(predicted, labels, map_names):
                class_total[map_name] += 1
                if pred == label:
                    class_correct[map_name] += 1
    
    epoch_loss = running_loss / total
    epoch_acc = 100. * correct / total
    
    # Per-class accuracy
    per_class_acc = {}
    for m in MAPS:
        if class_total[m] > 0:
            per_class_acc[m] = 100. * class_correct[m] / class_total[m]
        else:
            per_class_acc[m] = 0.0
    
    return epoch_loss, epoch_acc, per_class_acc


def train():
    """Main training function."""
    print("=" * 60)
    print("Valorant Map Classifier - Training")
    print("=" * 60)
    
    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️  Device: {device}")
    
    # Data
    train_loader, val_loader = get_dataloaders()
    
    # Model
    model = build_model(pretrained=True).to(device)
    print(f"🧠 Model: {MODEL_NAME} | Params: {count_parameters(model):,}")
    
    # Loss, optimizer, scheduler
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=NUM_EPOCHS, eta_min=1e-6
    )
    
    # W&B init
    if USE_WANDB and WANDB_AVAILABLE:
        wandb.init(
            project=WANDB_PROJECT,
            entity=WANDB_ENTITY,
            config={
                "model": MODEL_NAME,
                "batch_size": BATCH_SIZE,
                "epochs": NUM_EPOCHS,
                "lr": LEARNING_RATE,
                "weight_decay": WEIGHT_DECAY,
                "image_size": 224,
                "num_maps": len(MAPS)
            }
        )
        wandb.watch(model, log="all", log_freq=50)
    
    # Training loop
    best_val_acc = 0.0
    patience_counter = 0
    
    for epoch in range(NUM_EPOCHS):
        start_time = time.time()
        
        # Train
        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, device
        )
        
        # Validate
        val_loss, val_acc, per_class_acc = validate(
            model, val_loader, criterion, device
        )
        
        # Step scheduler
        scheduler.step()
        
        elapsed = time.time() - start_time
        
        # Logging
        print(f"\nEpoch {epoch+1}/{NUM_EPOCHS} ({elapsed:.1f}s)")
        print(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"  Val   Loss: {val_loss:.4f} | Val   Acc: {val_acc:.2f}%")
        
        # Print per-class accuracy
        print("  Per-class accuracy:")
        for m in MAPS:
            print(f"    {m:10s}: {per_class_acc[m]:5.1f}%")
        
        # W&B logging
        if USE_WANDB and WANDB_AVAILABLE:
            log_dict = {
                "epoch": epoch + 1,
                "train/loss": train_loss,
                "train/acc": train_acc,
                "val/loss": val_loss,
                "val/acc": val_acc,
                "lr": optimizer.param_groups[0]['lr']
            }
            for m in MAPS:
                log_dict[f"val_acc/{m.lower()}"] = per_class_acc[m]
            wandb.log(log_dict)
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'maps': MAPS
            }, BEST_MODEL_PATH)
            print(f"  💾 Saved best model (val_acc: {val_acc:.2f}%)")
        else:
            patience_counter += 1
            print(f"  ⏳ No improvement ({patience_counter}/{EARLY_STOP_PATIENCE})")
        
        # Early stopping
        if patience_counter >= EARLY_STOP_PATIENCE:
            print(f"\n🛑 Early stopping at epoch {epoch+1}")
            break
    
    print(f"\n🎉 Training complete! Best val acc: {best_val_acc:.2f}%")
    print(f"📁 Best model saved to: {BEST_MODEL_PATH}")
    
    if USE_WANDB and WANDB_AVAILABLE:
        wandb.finish()


if __name__ == "__main__":
    train()
