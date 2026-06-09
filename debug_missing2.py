"""
Debug tìm ASSISTED/STANDARD/HARDCORE và subtitle chưa dịch
"""
import json, os, csv, sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

EXTRACTED = r'd:\RE4_VietHoa\extracted_msg'
CSV       = r'd:\RE4_VietHoa\vietnamese_translation.csv'

KEYWORDS = ['ASSISTED', 'STANDARD', 'HARDCORE', "what's taking so long", "taking so long"]

# -------------------------------------------------------
# 1. Tìm trong CSV
# -------------------------------------------------------
print("=== [1] CSV - tìm ASSISTED/STANDARD/HARDCORE/subtitle ===")
with open(CSV, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        orig = row.get('English', row.get('Original', '')).strip()
        viet = row.get('Vietnamese', '').strip()
        for kw in KEYWORDS:
            if kw.lower() in orig.lower():
                status = 'OK' if viet else 'MISSING'
                print(f"  [{status}] {os.path.basename(row['File Path'])} idx={row['Entry Index']}")
                print(f"    Orig: {orig[:70]}")
                print(f"    Viet: {viet[:70] if viet else '[EMPTY - CHƯA DỊCH]'}")
                break

print()

# -------------------------------------------------------
# 2. Tìm trong JSON files
# -------------------------------------------------------
print("=== [2] JSON files - tìm ASSISTED/STANDARD/HARDCORE ===")
for root, dirs, files in os.walk(EXTRACTED):
    for fname in files:
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for i, entry in enumerate(data.get('entries', [])):
                for si, c in enumerate(entry.get('content', [])):
                    if c and any(kw.lower() in c.lower() for kw in ['ASSISTED', 'STANDARD', 'HARDCORE']):
                        if si == 1:  # chỉ in slot English
                            rel = os.path.relpath(fpath, EXTRACTED)
                            print(f"  File: {rel}")
                            print(f"  idx={i} slot={si}: {c[:60]}")
                            # Show all slots briefly
                            print(f"  All slots: {[s[:20] if s else '' for s in entry['content'][:6]]}")
                            print()
                            break
        except:
            pass

print()
print("=== [3] JSON files - tìm subtitle 'taking so long' ===")
for root, dirs, files in os.walk(EXTRACTED):
    for fname in files:
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for i, entry in enumerate(data.get('entries', [])):
                for si, c in enumerate(entry.get('content', [])):
                    if c and 'taking so long' in c.lower():
                        rel = os.path.relpath(fpath, EXTRACTED)
                        print(f"  File: {rel}")
                        print(f"  idx={i} name={entry.get('name','')}")
                        for j, slot in enumerate(entry['content']):
                            if slot:
                                print(f"    slot[{j}]={slot[:50]}")
                        print()
        except:
            pass
