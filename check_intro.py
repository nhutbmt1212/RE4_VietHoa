"""Search ALL extracted JSON files for subtitle text"""
import json, os

search_texts = [
    "cop inside me died",
    "September 29, 1998",
    "september 29",
    "Raccoon City",
    "I had a choice",
    "I'll never forget",
]

EXTRACTED = 'extracted_msg'
total_files = 0
found = []

for root, dirs, files in os.walk(EXTRACTED):
    for fname in files:
        if not fname.endswith('.json'):
            continue
        total_files += 1
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for i, entry in enumerate(data.get('entries', [])):
                for slot_idx, c in enumerate(entry.get('content', [])):
                    if not c:
                        continue
                    for st in search_texts:
                        if st.lower() in c.lower():
                            rel = os.path.relpath(fpath, EXTRACTED).replace('\\', '/')
                            found.append((rel, i, slot_idx, c[:80]))
                            break
        except:
            pass

print(f"Searched {total_files} JSON files")
print(f"Found {len(found)} matches:\n")
for rel, idx, slot, text in found:
    print(f"  {rel}")
    print(f"  idx={idx} slot={slot}: {text}")
    print()
