"""
Benchmark inference speed and model size.
"""
import time
import torch
import os
from pathlib import Path

from src.config import BEST_MODEL_PATH, PROJECT_ROOT
from src.model import build_model


def benchmark_model(model_path: Path = BEST_MODEL_PATH):
    """Measure model size and inference latency."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Model size
    size_mb = os.path.getsize(model_path) / (1024 * 1024)
    print(f"📦 Model size: {size_mb:.2f} MB")
    
    # Load model
    checkpoint = torch.load(model_path, map_location=device, weights_only=False)
    model = build_model(pretrained=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    # Warmup
    dummy_input = torch.randn(1, 3, 224, 224, device=device)
    for _ in range(10):
        _ = model(dummy_input)
    
    # Benchmark
    iterations = 100
    start = time.time()
    with torch.no_grad():
        for _ in range(iterations):
            _ = model(dummy_input)
    end = time.time()
    
    avg_latency = (end - start) / iterations * 1000  # ms
    fps = 1000 / avg_latency
    
    print(f" Average latency: {avg_latency:.2f}ms")
    print(f" Throughput: {fps:.1f} FPS")
    print(f"️  Device: {device}")
    
    return size_mb, avg_latency, fps


if __name__ == "__main__":
    print("=" * 50)
    print("Model Benchmarking")
    print("=" * 50)
    benchmark_model(BEST_MODEL_PATH)
    
    # Also benchmark fine-tuned if it exists
    fine_tuned_path = PROJECT_ROOT / "models" / "fine_tuned_model.pth"
    if fine_tuned_path.exists():
        print("\n" + "=" * 50)
        print("Fine-Tuned Model Benchmarking")
        print("=" * 50)
        benchmark_model(fine_tuned_path)