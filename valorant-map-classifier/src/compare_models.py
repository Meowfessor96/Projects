"""
Compare the original best_model.pth vs fine_tuned_model.pth on the test set.
"""
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from src.config import SPLITS_DIR, BEST_MODEL_PATH, BATCH_SIZE, NUM_WORKERS, MAPS, PROJECT_ROOT
from src.dataset import ValorantMapDataset, get_val_transforms
from src.model import build_model

FINE_TUNED_PATH = PROJECT_ROOT / "models" / "fine_tuned_model.pth"


def evaluate_model(model_path, model_name):
    """Evaluate a single model on the test set."""
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        return None
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Load test data
    test_dataset = ValorantMapDataset(SPLITS_DIR / "test", transforms=get_val_transforms())
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS)
    
    # Load model
    checkpoint = torch.load(model_path, map_location=device, weights_only=False)
    model = build_model(pretrained=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    # Evaluate
    correct = 0
    total = 0
    class_correct = {m: 0 for m in MAPS}
    class_total = {m: 0 for m in MAPS}
    
    with torch.no_grad():
        for images, labels, map_names in test_loader:
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
    per_class_acc = {}
    for m in MAPS:
        if class_total[m] > 0:
            per_class_acc[m] = 100. * class_correct[m] / class_total[m]
        else:
            per_class_acc[m] = 0.0
    
    return {
        'name': model_name,
        'overall_acc': overall_acc,
        'per_class': per_class_acc,
        'correct': correct,
        'total': total
    }


def compare_models():
    print("=" * 70)
    print("Model Comparison: Original vs Fine-Tuned")
    print("=" * 70)
    
    # Evaluate both models
    print("\n📊 Evaluating original model...")
    original_results = evaluate_model(BEST_MODEL_PATH, "Original (best_model.pth)")
    
    print("📊 Evaluating fine-tuned model...")
    fine_tuned_results = evaluate_model(FINE_TUNED_PATH, "Fine-Tuned (fine_tuned_model.pth)")
    
    if not original_results or not fine_tuned_results:
        print("\n❌ Could not compare models. Make sure both exist in models/")
        return
    
    # Print comparison
    print("\n" + "=" * 70)
    print("OVERALL ACCURACY COMPARISON")
    print("=" * 70)
    print(f"{'Model':<30} {'Accuracy':<15} {'Correct/Total':<15}")
    print("-" * 70)
    print(f"{original_results['name']:<30} {original_results['overall_acc']:>6.2f}%      {original_results['correct']:>3}/{original_results['total']:<3}")
    print(f"{fine_tuned_results['name']:<30} {fine_tuned_results['overall_acc']:>6.2f}%      {fine_tuned_results['correct']:>3}/{fine_tuned_results['total']:<3}")
    
    diff = fine_tuned_results['overall_acc'] - original_results['overall_acc']
    if diff > 0:
        print(f"\n✅ Fine-tuned model is BETTER by {diff:.2f}%")
    elif diff < 0:
        print(f"\n⚠️  Fine-tuned model is WORSE by {abs(diff):.2f}% (may have overfit)")
    else:
        print(f"\n➡️  Both models perform equally")
    
    # Per-class comparison
    print("\n" + "=" * 70)
    print("PER-MAP ACCURACY COMPARISON")
    print("=" * 70)
    print(f"{'Map':<12} {'Original':<12} {'Fine-Tuned':<12} {'Difference':<12}")
    print("-" * 70)
    
    improvements = []
    regressions = []
    
    for m in MAPS:
        orig_acc = original_results['per_class'][m]
        ft_acc = fine_tuned_results['per_class'][m]
        diff = ft_acc - orig_acc
        
        if diff > 0:
            improvements.append((m, diff))
            marker = "✅"
        elif diff < 0:
            regressions.append((m, diff))
            marker = "⚠️"
        else:
            marker = "➡️"
        
        print(f"{m:<12} {orig_acc:>6.2f}%     {ft_acc:>6.2f}%     {diff:>+6.2f}%  {marker}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if improvements:
        print(f"\n📈 Maps that IMPROVED ({len(improvements)}):")
        for m, diff in sorted(improvements, key=lambda x: x[1], reverse=True):
            print(f"   {m:<12} +{diff:.2f}%")
    
    if regressions:
        print(f"\n📉 Maps that REGRESSED ({len(regressions)}):")
        for m, diff in sorted(regressions, key=lambda x: x[1]):
            print(f"   {m:<12} {diff:.2f}%")
    
    if not improvements and not regressions:
        print("\n➡️  No changes detected across any maps.")
    
    # Recommendation
    print("\n" + "=" * 70)
    if diff > 2:
        print("💡 RECOMMENDATION: Use the fine-tuned model!")
        print(f"   It improved overall accuracy by {diff:.2f}%")
    elif diff < -2:
        print("💡 RECOMMENDATION: Stick with the original model!")
        print(f"   The fine-tuned model regressed by {abs(diff):.2f}% (likely overfit)")
    else:
        print("💡 RECOMMENDATION: Both models perform similarly.")
        print("   Check per-class results to decide which to use.")
    print("=" * 70)


if __name__ == "__main__":
    compare_models()
