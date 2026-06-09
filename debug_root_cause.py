"""
DEBUG STEP 5: TÌM GỐC RỄ CUỐI CÙNG
1. PAK patch_006 KHÔNG có file menu nào -> menu chưa được đóng gói
2. ch_mes_develop_ao.msg.22 có SEPARATE WAYS nhưng content slot thế nào?
3. Tìm tất cả file trong PAK patch_006 để biết nó chứa gì
"""
import os, sys, json, csv, struct
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

GAME_DIR  = r"d:\Games\Resident Evil 4"
EXTRACTED = r'd:\RE4_VietHoa\extracted_msg'
CSV       = r'd:\RE4_VietHoa\vietnamese_translation.csv'

# -------------------------------------------------------
# STEP 5A: Đọc danh sách file trong PAK patch_006
# -------------------------------------------------------
pak_path = os.path.join(GAME_DIR, "re_chunk_000.pak.patch_006.pak")
print(f"=== Nội dung PAK patch_006 ===")

# RE Engine PAK format:
# Magic: KPKA (4 bytes)
# Version: 2 (4 bytes)  
# Num files: 4 bytes
# Padding: 4 bytes
# File entries: [hash_lo(4), hash_hi(4), offset(8), size_compressed(8), size_decompressed(8), flags(4)]
# After entries: file data

with open(pak_path, 'rb') as f:
    magic = f.read(4)
    version = struct.unpack('<I', f.read(4))[0]
    num_files = struct.unpack('<I', f.read(4))[0]
    padding = f.read(4)
    print(f"Magic: {magic}, Version: {version}, Files: {num_files}")
    
    # Đọc tất cả file entries
    entries = []
    for i in range(num_files):
        hash_lo = struct.unpack('<I', f.read(4))[0]
        hash_hi = struct.unpack('<I', f.read(4))[0]
        offset  = struct.unpack('<Q', f.read(8))[0]
        size_c  = struct.unpack('<Q', f.read(8))[0]
        size_d  = struct.unpack('<Q', f.read(8))[0]
        flags   = struct.unpack('<I', f.read(4))[0]
        entries.append((hash_lo, hash_hi, offset, size_c, size_d, flags))
    
    print(f"Total entries: {len(entries)}")
    for i, (hl, hh, off, sc, sd, fl) in enumerate(entries[:10]):
        print(f"  [{i}] hash=({hl:08X},{hh:08X}) offset={off} size={sc}/{sd} flags={fl}")

print()

# -------------------------------------------------------
# STEP 5B: Kiểm tra ch_mes_develop_ao.msg.22 slots
# -------------------------------------------------------
p = os.path.join(EXTRACTED, r'natives\stm\_chainsaw\message\mes_develop_misc\ch_mes_develop_ao.msg.22.json')
with open(p, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== ch_mes_develop_ao.msg.22 - SEPARATE WAYS (idx=0) ===")
entry = data['entries'][0]
print(f"name: {entry.get('name','')}")
print("Slots:")
for i, slot in enumerate(entry['content']):
    print(f"  slot[{i:2d}] = {repr(slot[:60]) if slot else '(empty)'}")

print()
print("=== ch_mes_develop_ao.msg.22 - THE MERCENARIES (idx=2) ===")
if len(data['entries']) > 2:
    entry2 = data['entries'][2]
    print(f"name: {entry2.get('name','')}")
    print("Slots:")
    for i, slot in enumerate(entry2['content']):
        print(f"  slot[{i:2d}] = {repr(slot[:60]) if slot else '(empty)'}")

print()

# -------------------------------------------------------
# STEP 5C: Kiểm tra CSV có ch_mes_develop_ao không?
# -------------------------------------------------------
print("=== ch_mes_develop_ao trong CSV ===")
with open(CSV, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = [row for row in reader if 'ch_mes_develop_ao' in row.get('File Path','')]
for row in rows:
    print(f"  idx={row['Entry Index']} orig={row.get('English','')[:50]} viet={row.get('Vietnamese','')[:50]}")

print()

# -------------------------------------------------------
# STEP 5D: Kiểm tra import_translation: file có được xử lý không?
# (Xem trong extracted_msg có .json và .msg không)
# -------------------------------------------------------
print("=== Kiểm tra extracted_msg cho ch_mes_develop_ao ===")
develop_path = os.path.join(EXTRACTED, r'natives\stm\_chainsaw\message\mes_develop_misc\ch_mes_develop_ao.msg.22')
print(f"msg file: {'EXISTS' if os.path.exists(develop_path) else 'MISSING'}")
print(f"json file: {'EXISTS' if os.path.exists(develop_path+'.json') else 'MISSING'}")

print()

# -------------------------------------------------------
# STEP 5E: Tìm hiểu tại sao PAK không có menu files
# -> Kiểm tra pak_builder.py xem nó lấy file từ đâu
# -------------------------------------------------------
print("=== Phân tích pak_builder.py ===")
pak_builder = r'd:\RE4_VietHoa\pak_builder.py'
with open(pak_builder, 'r', encoding='utf-8') as f:
    content = f.read()
# Tìm dòng quan trọng
lines = content.split('\n')
for i, line in enumerate(lines):
    if any(kw in line for kw in ['mod_dir', 'Vietnamese', 'walk', 'glob', 'msg']):
        print(f"  L{i+1}: {line.rstrip()}")

print()

# -------------------------------------------------------
# STEP 5F: Kiểm tra vietnamese_mod directory
# -------------------------------------------------------
mod_dir = r'd:\RE4_VietHoa\vietnamese_mod'
print(f"=== vietnamese_mod directory ===")
if os.path.exists(mod_dir):
    count = 0
    for root, dirs, files in os.walk(mod_dir):
        for f in files:
            print(f"  {os.path.relpath(os.path.join(root,f), mod_dir)}")
            count += 1
            if count > 30:
                print("  ...")
                break
        if count > 30:
            break
else:
    print(f"  NOT FOUND (đã bị xóa sau khi build PAK)")
    print("  -> import_translation xóa mod_dir sau khi build!")
    print("  -> Cần tạo lại từ đầu để kiểm tra")
