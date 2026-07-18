"""
Interactive script to collect hard examples and correct the model.
Uses a global counter (feedback_1, feedback_2, ...) so you can reuse the same test file.
"""
import shutil
from pathlib import Path
import torch

from src.config import MAPS, BEST_MODEL_PATH, PROJECT_ROOT
from src.inference import load_model, predict_image

FEEDBACK_DIR = PROJECT_ROOT / "data" / "feedback"


def get_next_feedback_number() -> int:
    """
    Scan all feedback folders and return the next available counter number.
    Looks for files matching pattern: feedback_<number>*
    """
    if not FEEDBACK_DIR.exists():
        return 1
    
    max_num = 0
    # Scan all subdirectories (one per map)
    for file in FEEDBACK_DIR.rglob("feedback_*"):
        if file.is_file():
            try:
                # Extract the number from "feedback_<number>..."
                parts = file.stem.split("_")
                if len(parts) >= 2:
                    num = int(parts[1])
                    max_num = max(max_num, num)
            except (ValueError, IndexError):
                continue
    
    return max_num + 1


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _ = load_model(BEST_MODEL_PATH, device)
    
    print("\n" + "=" * 60)
    print("🧠 Interactive Model Feedback Collector")
    print("=" * 60)
    print("Instructions:")
    print("1. Paste the path to a tricky image (or type 'q' to quit)")
    print("2. Review the Top 3 predictions.")
    print("3. If correct, press Enter to skip.")
    print("4. If WRONG, type the correct map name (e.g., 'ASCENT').")
    print(f"Valid maps: {', '.join(MAPS)}\n")
    
    # Get the starting counter for this session
    counter = get_next_feedback_number()
    print(f"📊 Starting feedback counter at: {counter}\n")
    
    while True:
        img_path_str = input("📸 Enter image path (or 'q' to quit): ").strip().strip('"')
        
        if img_path_str.lower() == 'q':
            print("👋 Exiting feedback collector.")
            break
            
        img_path = Path(img_path_str)
        if not img_path.exists():
            print("❌ File not found. Try again.\n")
            continue
            
        # Get predictions
        try:
            predictions = predict_image(model, img_path, device, top_k=3)
        except Exception as e:
            print(f"❌ Error processing image: {e}\n")
            continue
            
        print("\n🔮 Model Predictions:")
        for i, (map_name, conf) in enumerate(predictions, 1):
            bar = "█" * int(conf / 2)
            print(f"  {i}. {map_name:10s} {conf:5.2f}% {bar}")
            
        # Ask for feedback
        correct_map = input("\n❓ Is the #1 prediction correct? (Press Enter for Yes, or type correct map name): ").strip().upper()
        
        if not correct_map:
            print("✅ Skipping (Model was correct).\n")
            continue
            
        if correct_map == 'Q':
            break
            
        if correct_map not in MAPS:
            print(f"⚠️ Invalid map name. Please choose from: {', '.join(MAPS)}\n")
            continue
            
        # Save to feedback directory with counter-based name
        target_dir = FEEDBACK_DIR / correct_map
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Use counter + original extension (e.g., feedback_1.jpg)
        new_filename = f"feedback_{counter}{img_path.suffix.lower()}"
        dest_path = target_dir / new_filename
        
        # Safety check: if file somehow exists, increment until we find a free slot
        while dest_path.exists():
            counter += 1
            new_filename = f"feedback_{counter}{img_path.suffix.lower()}"
            dest_path = target_dir / new_filename
        
        shutil.copy(img_path, dest_path)
        print(f"💾 Saved as: {dest_path}")
        print("   The model will learn from this next time we fine-tune!\n")
        
        # Increment counter for next image
        counter += 1

if __name__ == "__main__":
    main()
