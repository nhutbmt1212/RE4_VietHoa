"""
Simulate what always-on mode does to dev1_term_menu 
to verify the translation is applied correctly.
"""
import json
import csv
import copy

json_path = r"extracted_msg\natives\stm\_chainsaw\message\dev1_term\dev1_term_menu.msg.22.json"

# Load translations from CSV for this file
translations = []
with open('vietnamese_translation.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        fp = row['File Path'].replace('\\', '/').strip()
        if fp.endswith('.json'):
            fp = fp[:-5]
        if fp == 'natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22':
            viet = row['Vietnamese'].strip()
            idx = int(row['Entry Index'].strip())
            if viet:
                translations.append((idx, viet))

print(f"Total translations for this file: {len(translations)}")

# Load JSON
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

data2 = copy.deepcopy(data)

# Apply always-on mode
for idx, viet_text in translations:
    if idx < len(data2['entries']):
        content = data2['entries'][idx]['content']
        for i in range(len(content)):
            if content[i].strip():
                content[i] = viet_text

# Check results for key entries
print("\n--- Result for key entries after always-on ---")
key_indices = [12, 15, 17, 18, 19, 20, 21, 22]
for idx in key_indices:
    if idx < len(data2['entries']):
        entry = data2['entries'][idx]
        print(f"  idx={idx} name={entry['name']}")
        print(f"    slot[0]={entry['content'][0]}")
        print(f"    slot[1]={entry['content'][1]}")
        print(f"    slot[3]={entry['content'][3]}")
        print()

# Check if translations contain entries for dev1_term_hud etc
print("\n--- Files in CSV that might be menu-related ---")
files_found = set()
with open('vietnamese_translation.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        fp = row['File Path'].replace('\\', '/').strip()
        if 'dev1_term' in fp and row['Vietnamese'].strip():
            files_found.add(fp)

for f in sorted(files_found):
    print(f"  {f}")
