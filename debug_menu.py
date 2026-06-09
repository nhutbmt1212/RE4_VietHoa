import json
import os

# Check the JSON structure of dev1_term_menu
json_path = r"extracted_msg\natives\stm\_chainsaw\message\dev1_term\dev1_term_menu.msg.22.json"

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total entries: {len(data['entries'])}")
print(f"\n--- First 5 entries structure ---")
for entry in data['entries'][:5]:
    print(f"  name: {entry.get('name', 'N/A')}")
    print(f"  content ({len(entry['content'])} slots): {entry['content']}")
    print()

# Find START GAME entry
print("\n--- Looking for START GAME / menu entries ---")
for i, entry in enumerate(data['entries']):
    name = entry.get('name', '')
    content = entry['content']
    # Check if any content contains START or GAME
    for j, c in enumerate(content):
        if c and ('START' in c.upper() or 'NEW GAME' in c.upper() or 'CONTINUE' in c.upper()):
            print(f"  idx={i} name={name}")
            print(f"    content slots: {content}")
            break
    if i > 30:
        break

# Print entries 10-20 (where idx=12 START GAME should be)
print("\n--- Entries 10-20 ---")
for i, entry in enumerate(data['entries']):
    if 10 <= i <= 20:
        print(f"  idx={i} name={entry.get('name','N/A')} content={entry['content']}")
