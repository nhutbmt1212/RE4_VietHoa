"""Debug why only 152 files are being processed"""
import csv
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "vietnamese_translation.csv")
EXTRACTED_DIR = os.path.join(SCRIPT_DIR, "extracted_msg")

translations_by_file = {}

with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        file_path = row["File Path"].replace("\\", "/").strip()
        if file_path.endswith(".json"):
            file_path = file_path[:-5]
            
        entry_idx_str = row["Entry Index"].strip()
        if not entry_idx_str:
            continue
        idx = int(entry_idx_str)
        viet = row["Vietnamese"].strip()

        if viet:
            if file_path not in translations_by_file:
                translations_by_file[file_path] = []
            translations_by_file[file_path].append((idx, viet))

print(f"Files with translations: {len(translations_by_file)}")

# Check which files exist vs don't exist
existing = 0
missing = 0
missing_list = []

for file_path in translations_by_file:
    original_msg = os.path.join(EXTRACTED_DIR, file_path)
    original_json = original_msg + ".json"
    
    if os.path.exists(original_json) and os.path.exists(original_msg):
        existing += 1
    else:
        missing += 1
        missing_list.append(file_path)

print(f"Files that EXIST (will be processed): {existing}")
print(f"Files that DON'T EXIST (will be skipped): {missing}")

if missing_list:
    print(f"\nMissing files (first 20):")
    for f in missing_list[:20]:
        print(f"  {f}")
        
# Check dev1_term specifically
print(f"\n=== dev1_term files ===")
for fp in translations_by_file:
    if 'dev1_term' in fp:
        msg = os.path.join(EXTRACTED_DIR, fp)
        json_f = msg + ".json"
        print(f"  {fp}")
        print(f"    .msg: {'EXISTS' if os.path.exists(msg) else 'MISSING'}")
        print(f"    .json: {'EXISTS' if os.path.exists(json_f) else 'MISSING'}")
        print(f"    translations: {len(translations_by_file[fp])}")
