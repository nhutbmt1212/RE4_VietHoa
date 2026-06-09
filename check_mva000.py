"""Check the mva000 file structure and verify PAK contains translated version"""
import json, csv, struct, os

# Check JSON structure
json_path = r"extracted_msg\natives\stm\_chainsaw\message\mes_main_cs\ch_mes_main_mva000.msg.22.json"
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total entries: {len(data['entries'])}")
for i, entry in enumerate(data['entries']):
    print(f"  idx={i} name={entry.get('name','')}")
    print(f"    slots ({len(entry['content'])}): ", end='')
    for j, c in enumerate(entry['content']):
        if c and '#Rejected#' not in c:
            print(f"[{j}]='{c[:30]}' ", end='')
    print()

# Check if translated version matches
print("\n=== Translation in CSV ===")
with open('vietnamese_translation.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        fp = row['File Path'].replace('\\','/').strip()
        if fp.endswith('.json'): fp = fp[:-5]
        if 'mva000' in fp:
            print(f"  idx={row['Entry Index']} viet={row['Vietnamese'].strip()[:60]}")

# Check the number of language slots
print(f"\nNumber of slots per entry: {len(data['entries'][0]['content'])}")
print("\nSlot mapping:")
slot_langs = {0:'Japanese', 1:'English', 2:'French', 3:'Italian', 4:'German', 
              5:'Spanish(EU)', 6:'Russian', 7:'Polish', 10:'Portuguese(BR)',
              11:'Korean', 12:'Traditional Chinese', 13:'Simplified Chinese',
              21:'Arabic', 32:'Spanish(LA)'}
for slot, lang in slot_langs.items():
    if slot < len(data['entries'][0]['content']):
        c = data['entries'][0]['content'][slot]
        print(f"  slot {slot:2d} ({lang}): '{c[:40] if c else ''}'" )
