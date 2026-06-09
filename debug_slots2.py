"""
DEBUG STEP 2: Phân tích chi tiết slot structure
- Xem slot nào game RE4 đọc (slot index là gì?)
- Tại sao ao_mes_main_sys_mainmenu SEPARATE WAYS vẫn hiện tiếng Anh?
"""
import json
import os
import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

EXTRACTED = r'd:\RE4_VietHoa\extracted_msg'

# -------------------------------------------------------
# PHÂN TÍCH SLOT INDEX
# Mỗi entry có 33 slots - tương ứng với ngôn ngữ nào?
# Slot 0 = Japanese, 1 = English, ...
# -------------------------------------------------------

# Kiểm tra dev1_term_menu để hiểu thứ tự slot
p1 = os.path.join(EXTRACTED, r'natives\stm\_chainsaw\message\dev1_term\dev1_term_menu.msg.22.json')
with open(p1, 'r', encoding='utf-8') as f:
    menu_data = json.load(f)

# Lấy entry idx=27 (EXIT) và hiển thị đầy đủ 33 slots
print("=== dev1_term_menu.msg.22 - Entry EXIT (idx=27) ===")
entry = menu_data['entries'][27]
print(f"name: {entry.get('name','')}")
for i, slot in enumerate(entry['content']):
    print(f"  slot[{i:2d}] = {repr(slot[:60]) if slot else '(empty)'}")

print()

# Kiểm tra ch_mes_main_sys_mainmenu để thấy tại sao SEPARATE WAYS không hiện
p2 = os.path.join(EXTRACTED, r'natives\stm\_chainsaw\message\mes_main_sys\ch_mes_main_sys_mainmenu.msg.22.json')
with open(p2, 'r', encoding='utf-8') as f:
    ch_menu = json.load(f)

print("=== ch_mes_main_sys_mainmenu.msg.22 - Toàn bộ entries ===")
print(f"Total: {len(ch_menu['entries'])} entries")
for i, entry in enumerate(ch_menu['entries'][:15]):
    slots_preview = []
    for j, c in enumerate(entry['content'][:5]):
        slots_preview.append(f"[{j}]={repr(c[:20]) if c else 'empty'}")
    print(f"  idx={i:3d} name={entry.get('name','')[:50]}")
    print(f"         " + " | ".join(slots_preview))

print()

# Kiểm tra ao_mes_main_sys_mainmenu (Separate Ways mainmenu)
p3 = os.path.join(EXTRACTED, r'natives\stm\_anotherorder\message\mes_main_sys\ao_mes_main_sys_mainmenu.msg.22.json')
with open(p3, 'r', encoding='utf-8') as f:
    ao_menu = json.load(f)

print("=== ao_mes_main_sys_mainmenu.msg.22 - Entry SEPARATE WAYS (idx=0) ===")
entry = ao_menu['entries'][0]
print(f"name: {entry.get('name','')}")
for i, slot in enumerate(entry['content']):
    print(f"  slot[{i:2d}] = {repr(slot[:60]) if slot else '(empty)'}")

print()

# mc_mes_main_sys_mainmenu (Mercenaries mainmenu)  
p4 = os.path.join(EXTRACTED, r'natives\stm\_mercenaries\message\mes_main_sys\mc_mes_main_sys_mainmenu.msg.22.json')
if os.path.exists(p4):
    with open(p4, 'r', encoding='utf-8') as f:
        mc_menu = json.load(f)
    print("=== mc_mes_main_sys_mainmenu.msg.22 - Entry THE MERCENARIES (idx=0) ===")
    entry = mc_menu['entries'][0]
    print(f"name: {entry.get('name','')}")
    for i, slot in enumerate(entry['content']):
        print(f"  slot[{i:2d}] = {repr(slot[:60]) if slot else '(empty)'}")
else:
    print(f"NOT FOUND: {p4}")
    # Liệt kê mercenaries message
    p4_dir = os.path.join(EXTRACTED, r'natives\stm\_mercenaries\message')
    if os.path.exists(p4_dir):
        for root, dirs, files in os.walk(p4_dir):
            for f in files:
                if f.endswith('.json'):
                    print(f"  {os.path.relpath(os.path.join(root,f), EXTRACTED)}")

print()
print("=== KIỂM TRA: Import_translation ghi vào slot nào? ===")
print("Logic: ghi đè TẤT CẢ slot != empty")
print("Vấn đề: nếu slot 1 (English) = empty, nhưng slot 0 (Japanese) có text")
print("thì game sẽ fallback sang slot 1 (English) = empty -> hiển thị gì?")
print()
print("QUAN TRỌNG: Game RE4 Remake dùng slot nào cho 'không có ngôn ngữ này'?")

# Xem metadata của file msg nếu có
print()
print("=== msg.22 metadata (nếu có) ===")
p1_raw = os.path.join(EXTRACTED, r'natives\stm\_anotherorder\message\mes_main_sys\ao_mes_main_sys_mainmenu.msg.22.json')
with open(p1_raw, 'r', encoding='utf-8') as f:
    raw = json.load(f)
# Top level keys
print(f"JSON keys: {list(raw.keys())}")
# language_ids nếu có
if 'language_ids' in raw:
    print(f"language_ids: {raw['language_ids']}")
elif 'languages' in raw:
    print(f"languages: {raw['languages']}")
