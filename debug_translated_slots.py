"""
debug_translated_slots.py
Tìm những entry trong CSV có bản dịch tiếng Việt
và kiểm tra slot tương ứng trong file JSON để biết game đọc slot nào.
"""
import csv, json, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "vietnamese_translation.csv")
EXTRACTED_DIR = os.path.join(SCRIPT_DIR, "extracted_msg")

# Tìm các entry có bản dịch tiếng Việt, xem slot gốc trong file JSON
print("=== ENTRIES WITH VIETNAMESE TRANSLATION ===\n")

shown_types = {}

with open(CSV_PATH, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        fp = row["File Path"].replace("\\", "/").strip()
        if fp.endswith(".json"):
            fp = fp[:-5]
        
        viet = row["Vietnamese"].strip()
        eng = row["English"].strip()
        entry_name = row["Entry Name"].strip()
        entry_idx = int(row["Entry Index"].strip())
        
        if not viet:
            continue
        
        # Get folder type
        parts = fp.split("/")
        folder_type = parts[-2] if len(parts) >= 2 else "unknown"
        
        if folder_type in shown_types and shown_types[folder_type] >= 2:
            continue
        
        # Load the JSON and check what's actually in the slots
        json_path = os.path.join(EXTRACTED_DIR, fp) + ".json"
        if not os.path.exists(json_path):
            continue
        
        with open(json_path, encoding="utf-8") as f2:
            data = json.load(f2)
        
        if entry_idx >= len(data["entries"]):
            continue
        
        entry = data["entries"][entry_idx]
        content = entry["content"]
        
        # Find which slots have real (non-Rejected, non-empty) content
        real_slots = [(i, c) for i, c in enumerate(content) if c.strip() and "#Rejected#" not in c]
        rejected_slots = [i for i, c in enumerate(content) if "#Rejected#" in c]
        empty_slots = [i for i, c in enumerate(content) if not c.strip()]
        
        if folder_type not in shown_types:
            shown_types[folder_type] = 0
        
        print(f"Type: {folder_type}")
        print(f"  File: {fp.split('/')[-1]}")
        print(f"  Entry [{entry_idx}]: {entry_name}")
        print(f"  English: {eng[:60]}")
        print(f"  Vietnamese: {viet[:60]}")
        print(f"  Total slots: {len(content)}")
        print(f"  Real content slots: {[i for i, _ in real_slots]}")
        if real_slots:
            for i, c in real_slots[:5]:
                print(f"    [{i}]: {repr(c[:70])}")
        print(f"  #Rejected# slots: {len(rejected_slots)} ({rejected_slots[:5]}...)")
        print(f"  Empty slots: {len(empty_slots)}")
        print()
        
        shown_types[folder_type] += 1
        
        if len(shown_types) >= 10 and all(v >= 2 for v in shown_types.values()):
            break

# Summary - which file types have #Rejected# as placeholder
print("\n=== SUMMARY: FILE TYPES AND THEIR SLOT STRUCTURE ===\n")
type_structures = {}
with open(CSV_PATH, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        fp = row["File Path"].replace("\\", "/").strip()
        if fp.endswith(".json"):
            fp = fp[:-5]
        viet = row["Vietnamese"].strip()
        if not viet:
            continue
        entry_idx = int(row["Entry Index"].strip())
        parts = fp.split("/")
        folder_type = parts[-2] if len(parts) >= 2 else "unknown"
        
        if folder_type in type_structures:
            continue
        
        json_path = os.path.join(EXTRACTED_DIR, fp) + ".json"
        if not os.path.exists(json_path):
            continue
        
        with open(json_path, encoding="utf-8") as f2:
            data = json.load(f2)
        
        if entry_idx >= len(data["entries"]):
            continue
        
        entry = data["entries"][entry_idx]
        content = entry["content"]
        
        has_real = any(c.strip() and "#Rejected#" not in c for c in content)
        all_rejected = all("#Rejected#" in c for c in content if c.strip())
        
        if all_rejected:
            structure = "ALL_REJECTED"
        elif has_real:
            real_slots = [i for i, c in enumerate(content) if c.strip() and "#Rejected#" not in c]
            structure = f"HAS_REAL at {real_slots[:5]}"
        else:
            structure = "EMPTY"
        
        type_structures[folder_type] = structure

for ft, st in sorted(type_structures.items()):
    print(f"  {ft}: {st}")
