import json
import os
import csv
import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

EXTRACTED = r'd:\RE4_VietHoa\extracted_msg'
CSV_PATH  = r'd:\RE4_VietHoa\vietnamese_translation.csv'

# -------------------------------------------------------
# STEP 1: Xem cấu trúc slot của dev1_term_menu
# -------------------------------------------------------
p1 = os.path.join(EXTRACTED, r'natives\stm\_chainsaw\message\dev1_term\dev1_term_menu.msg.22.json')
with open(p1, 'r', encoding='utf-8') as f:
    menu_data = json.load(f)

print('=== [1] dev1_term_menu.msg.22 ===')
print(f'Total entries: {len(menu_data["entries"])}')
first = menu_data['entries'][0]
print(f'Slots per entry: {len(first["content"])}')
print(f'First entry slots: {first["content"][:5]}')
print()

# Tìm những entry chưa dịch (vẫn còn tiếng Anh)
print('--- Entries có chứa SEPARATE / MERCENARIES / EXIT ---')
for i, entry in enumerate(menu_data['entries']):
    for si, c in enumerate(entry.get('content', [])):
        if c and any(kw in c.upper() for kw in ['SEPARATE', 'MERCENARIES', 'EXIT']):
            print(f'  idx={i} slot={si} name={entry.get("name","")}')
            print(f'    content={entry["content"]}')
            break

print()

# -------------------------------------------------------
# STEP 2: Xem cấu trúc slot ch_mes_main_sys_mainmenu
# -------------------------------------------------------
p2 = os.path.join(EXTRACTED, r'natives\stm\_chainsaw\message\mes_main_sys\ch_mes_main_sys_mainmenu.msg.22.json')
if os.path.exists(p2):
    with open(p2, 'r', encoding='utf-8') as f:
        sys_menu = json.load(f)
    print('=== [2] ch_mes_main_sys_mainmenu.msg.22 ===')
    print(f'Total entries: {len(sys_menu["entries"])}')
    first2 = sys_menu['entries'][0]
    print(f'Slots per entry: {len(first2["content"])}')
    print(f'First entry slots: {first2["content"][:5]}')
    print()
    print('--- Entries có chứa SEPARATE / MERCENARIES / EXIT ---')
    for i, entry in enumerate(sys_menu['entries']):
        for si, c in enumerate(entry.get('content', [])):
            if c and any(kw in c.upper() for kw in ['SEPARATE', 'MERCENARIES', 'EXIT']):
                print(f'  idx={i} slot={si} name={entry.get("name","")}')
                print(f'    content={entry["content"]}')
                break
else:
    print(f'File NOT found: {p2}')

print()

# -------------------------------------------------------
# STEP 3: Kiểm tra trong CSV có dịch "SEPARATE WAYS" không
# -------------------------------------------------------
print('=== [3] CSV - tìm SEPARATE WAYS / MERCENARIES / EXIT ===')
with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        orig = row.get('English', row.get('Original', '')).strip()
        viet = row.get('Vietnamese', '').strip()
        if any(kw in orig.upper() for kw in ['SEPARATE WAYS', 'THE MERCENARIES', 'EXIT']):
            status = 'OK' if viet else 'MISSING'
            print(f'  [{status}] idx={row["Entry Index"]} file={os.path.basename(row["File Path"])}')
            print(f'    Orig: {orig[:70]}')
            print(f'    Viet: {viet[:70] if viet else "[EMPTY]"}')

print()

# -------------------------------------------------------
# STEP 4: import_translation logic - slot filter check
# -------------------------------------------------------
print('=== [4] Phân tích logic slot trong import_translation.py ===')
print('Logic hiện tại:')
print('  for i in range(len(content)):')
print('      if content[i].strip():   <- chỉ ghi đè slot != empty')
print('          content[i] = viet_text')
print()
print('Vấn đề tiềm ẩn: nếu slot ENGLISH bị empty, nhưng slot khác có text,')
print('thì game vẫn đọc slot đó và hiển thị tiếng Anh.')
print()
print('--- Kiểm tra slot structure của entry SEPARATE WAYS trong dev1_term_menu ---')
for i, entry in enumerate(menu_data['entries']):
    for si, c in enumerate(entry.get('content', [])):
        if c and 'SEPARATE' in c.upper():
            print(f'  Entry idx={i}, name={entry.get("name","")}')
            for j, slot in enumerate(entry['content']):
                print(f'    slot[{j}] = {repr(slot[:50] if slot else "")}')

# -------------------------------------------------------
# STEP 5: Kiểm tra _anotherorder (Separate Ways DLC)
# -------------------------------------------------------
print()
p3 = os.path.join(EXTRACTED, r'natives\stm\_anotherorder\message')
if os.path.exists(p3):
    print(f'=== [5] _anotherorder/message contents ===')
    for root, dirs, files in os.walk(p3):
        for fname in files:
            if fname.endswith('.json'):
                rel = os.path.relpath(os.path.join(root, fname), EXTRACTED)
                print(f'  {rel}')
else:
    print(f'_anotherorder NOT found: {p3}')
