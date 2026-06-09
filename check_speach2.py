"""Check speach file for subtitle text and translation coverage"""
import json, csv, os

speach_json = r"extracted_msg\natives\stm\_chainsaw\message\mes_main_speach\ch_mes_main_speach.msg.22.json"

with open(speach_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total entries in ch_mes_main_speach: {len(data['entries'])}")
print(f"Slots per entry: {len(data['entries'][0]['content']) if data['entries'] else 0}")

# Check first 5 entries
print("\n--- First 5 entries ---")
for i, entry in enumerate(data['entries'][:5]):
    name = entry.get('name', '')
    c1 = entry['content'][1] if len(entry['content']) > 1 else ''
    print(f"  idx={i} name={name[:50]}")
    print(f"    slot[1]={c1[:60]}")

# Search for "cop inside me died"
print("\n--- Searching for 'cop inside me died' ---")
found = False
for i, entry in enumerate(data['entries']):
    for slot_idx, c in enumerate(entry['content']):
        if c and 'cop inside me died' in c.lower():
            print(f"  FOUND at idx={i} slot={slot_idx}: {c}")
            found = True
if not found:
    print("  NOT FOUND in speach file")

# Count translations in CSV for speach file
print("\n--- CSV coverage for speach file ---")
total_rows = 0
translated_rows = 0
with open('vietnamese_translation.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        fp = row['File Path'].replace('\\', '/').strip()
        if fp.endswith('.json'): fp = fp[:-5]
        if 'ch_mes_main_speach.msg.22' in fp and 'merchant' not in fp and 'shooting' not in fp:
            total_rows += 1
            if row['Vietnamese'].strip():
                translated_rows += 1

print(f"  Total rows in CSV for speach: {total_rows}")
print(f"  Translated: {translated_rows}")
print(f"  Untranslated: {total_rows - translated_rows}")

# Show some untranslated examples
print("\n--- First untranslated entries ---")
count = 0
with open('vietnamese_translation.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        fp = row['File Path'].replace('\\', '/').strip()
        if fp.endswith('.json'): fp = fp[:-5]
        if 'ch_mes_main_speach.msg.22' in fp and 'merchant' not in fp and 'shooting' not in fp:
            if not row['Vietnamese'].strip():
                orig = row.get('English', row.get('Original', '')).strip()
                print(f"  idx={row['Entry Index']}: {orig[:60]}")
                count += 1
                if count >= 10:
                    print("  ...")
                    break
