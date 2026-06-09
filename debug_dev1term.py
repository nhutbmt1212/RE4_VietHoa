"""
Kiểm tra dev1_term_menu.msg.22 hiện tại trong loose files
Xem nó có entry SEPARATE WAYS / THE MERCENARIES không
và entry nào controls những items đó trên main menu
"""
import sys, os
sys.path.insert(0, r'd:\RE4_VietHoa\tools\REMSG_Converter\src')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
from REWString import decrypt

# Đọc loose file hiện tại
loose_file = r'd:\Games\Resident Evil 4\natives\stm\_chainsaw\message\dev1_term\dev1_term_menu.msg.22'
print(f"File: {loose_file}")
print(f"Size: {os.path.getsize(loose_file):,} bytes")
print()

with open(loose_file, 'rb') as f:
    raw = f.read()

dec = decrypt(raw)
dec_str = dec.decode('utf-16-le', errors='replace')

# Tìm keyword
keywords = ['SEPARATE', 'MERCENARIES', 'EXIT', 'Quit', 'AnotherOrder', 'Another', 'Mercen']
for kw in keywords:
    pos = dec_str.find(kw)
    if pos >= 0:
        snippet = dec_str[max(0,pos-20):pos+60].replace('\x00','')
        print(f"  FOUND '{kw}' at char {pos}: ...{snippet}...")
    else:
        print(f"  NOT FOUND: '{kw}'")

print()
print("=== Tìm trong extracted JSON (bản gốc) ===")
import json
json_path = r'd:\RE4_VietHoa\extracted_msg\natives\stm\_chainsaw\message\dev1_term\dev1_term_menu.msg.22.json'
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total entries: {len(data['entries'])}")
print()
for i, entry in enumerate(data['entries']):
    name = entry.get('name', '')
    # Tìm entry liên quan đến AnotherOrder, Mercenaries, Start menu
    if any(kw.lower() in name.lower() for kw in ['another', 'mercenar', 'separ', 'startmenu', 'start_menu', 'dlc', 'bonus_']):
        print(f"  idx={i} name={name}")
        for si, c in enumerate(entry['content'][:6]):
            if c:
                print(f"    slot[{si}]={c[:50]}")
        print()
