"""
Model architecture using EfficientNet-B0 with transfer learning.
"""
import torch
import torch.nn as nn
from torchvision import models

from src.config import NUM_CLASSES, MODEL_NAME


def build_model(pretrained: bool = True) -> nn.Module:
    """
    Build EfficientNet-B0 with modified classification head.
    """
    if MODEL_NAME == "efficientnet_b0":
        if pretrained:
            weights = models.EfficientNet_B0_Weights.DEFAULT
            model = models.efficientnet_b0(weights=weights)
        else:
            model = models.efficientnet_b0(weights=None)
        
        # Freeze early layers (optional - comment out to train all)
        # for param in model.features[:6].parameters():
        #     param.requires_grad = False
        
        # Replace classifier head
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=0.3, inplace=True),
            nn.Linear(in_features, NUM_CLASSES)
        )
        
    elif MODEL_NAME == "resnet50":
        if pretrained:
            weights = models.ResNet50_Weights.DEFAULT
            model = models.resnet50(weights=weights)
        else:
            model = models.resnet50(weights=None)
        
        in_features = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(in_features, NUM_CLASSES)
        )
    else:
        raise ValueError(f"Unknown model: {MODEL_NAME}")
    
    return model


def count_parameters(model: nn.Module) -> int:
    """Count trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
