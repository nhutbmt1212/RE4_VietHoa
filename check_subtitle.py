"""Check if subtitle text is in CSV and what slot it uses"""
import csv
import json
import os

search_text = "cop inside me died"

print(f"=== Searching CSV for: '{search_text}' ===")
found_in_csv = []
with open('vietnamese_translation.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        orig = row.get('English', row.get('Original', '')).strip()
        viet = row.get('Vietnamese', '').strip()
        if search_text.lower() in orig.lower():
            found_in_csv.append(row)
            print(f"  File: {row['File Path']}")
            print(f"  Idx:  {row['Entry Index']}")
            print(f"  Orig: {orig[:80]}")
            print(f"  Viet: {viet[:80] if viet else '[EMPTY - NOT TRANSLATED]'}")
            print()

if not found_in_csv:
    print("  NOT FOUND in CSV")

# Also search in all JSON files
print(f"\n=== Searching JSON files for: '{search_text}' ===")
EXTRACTED = 'extracted_msg'
for root, dirs, files in os.walk(EXTRACTED):
    for fname in files:
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for i, entry in enumerate(data.get('entries', [])):
                for slot_idx, c in enumerate(entry.get('content', [])):
                    if c and search_text.lower() in c.lower():
                        rel = os.path.relpath(fpath, EXTRACTED).replace('\\', '/')
                        print(f"  File: {rel}")
                        print(f"  Entry idx={i}, slot={slot_idx}")
                        print(f"  Text: {c[:100]}")
                        print()
        except:
            pass
