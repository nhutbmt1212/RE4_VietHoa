"""
debug_missing.py
Tìm các entry chưa được dịch trong CSV:
1. "SEPARATE WAYS", "THE MERCENARIES", "EXIT" trong main menu
2. "Expanded Treasure Map" popup (DLC)
3. "See what's taking so long" subtitle
"""
import csv, json, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "vietnamese_translation.csv")
EXTRACTED_DIR = os.path.join(SCRIPT_DIR, "extracted_msg")

SEARCH_TERMS = [
    "SEPARATE WAYS",
    "THE MERCENARIES",
    "EXIT",
    "Expanded Treasure Map",
    "taking so long",
    "Play through the main story",
    "nightmare",
]

print("=== SEARCHING IN EXTRACTED JSON FILES ===\n")

for root, dirs, files in os.walk(EXTRACTED_DIR):
    for fname in files:
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, encoding='utf-8') as f:
                data = json.load(f)
        except:
            continue

        for entry in data.get('entries', []):
            for slot_idx, c in enumerate(entry.get('content', [])):
                if not c:
                    continue
                for term in SEARCH_TERMS:
                    if term.lower() in c.lower():
                        rel = os.path.relpath(fpath, EXTRACTED_DIR).replace('\\', '/')
                        print(f"Term: '{term}'")
                        print(f"  File: {rel}")
                        print(f"  Entry: {entry['name']}")
                        print(f"  Slot [{slot_idx}]: {c[:80]!r}")
                        print()

print("\n=== CHECKING CSV COVERAGE ===\n")

# Load all translated entries
translated = set()
with open(CSV_PATH, encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Vietnamese'].strip():
            key = (row['File Path'].replace('\\', '/').replace('.json','').strip(), row['Entry Name'].strip())
            translated.add(key)

# Search JSON files again and check if in CSV
for root, dirs, files in os.walk(EXTRACTED_DIR):
    for fname in files:
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, encoding='utf-8') as f:
                data = json.load(f)
        except:
            continue

        rel = os.path.relpath(fpath, EXTRACTED_DIR).replace('\\', '/').replace('.json', '')

        for i, entry in enumerate(data.get('entries', [])):
            for slot_idx, c in enumerate(entry.get('content', [])):
                if not c:
                    continue
                for term in SEARCH_TERMS:
                    if term.lower() in c.lower():
                        key = (rel, entry['name'])
                        in_csv = key in translated
                        print(f"Term: '{term}'")
                        print(f"  File: {rel}")
                        print(f"  Entry idx={i}: {entry['name']}")
                        print(f"  In CSV with Vietnamese: {in_csv}")
                        if not in_csv:
                            # Check if in CSV at all (without Vietnamese)
                            in_csv_notranslated = False
                            with open(CSV_PATH, encoding='utf-8-sig') as cf:
                                reader2 = csv.DictReader(cf)
                                for row in reader2:
                                    fp = row['File Path'].replace('\\', '/').replace('.json','').strip()
                                    if fp == rel and row['Entry Name'].strip() == entry['name']:
                                        in_csv_notranslated = True
                                        print(f"  Found in CSV but Vietnamese='{row['Vietnamese'][:30]}'")
                                        break
                            if not in_csv_notranslated:
                                print(f"  NOT IN CSV AT ALL")
                                # Show what the entry looks like
                                content = entry['content']
                                real = [(si, sc) for si, sc in enumerate(content) if sc and '#Rejected#' not in sc]
                                print(f"  Real slots: {[si for si, _ in real[:5]]}")
                                for si, sc in real[:3]:
                                    print(f"    [{si}]: {sc[:60]!r}")
                        print()
                        break
