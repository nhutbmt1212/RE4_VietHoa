"""
Kiểm tra tại sao file đã dịch trong CSV nhưng game vẫn hiện tiếng Anh:
1. File có trong PAK không?
2. Slot nào được ghi đè?
"""
import json, os, csv, sys, struct
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

EXTRACTED = r'd:\RE4_VietHoa\extracted_msg'
GAME_DIR  = r'd:\Games\Resident Evil 4'

# -------------------------------------------------------
# Đọc danh sách file trong PAK mới
# -------------------------------------------------------
pak_path = os.path.join(GAME_DIR, "re_chunk_000.pak.patch_006.pak")
print(f"PAK size: {os.path.getsize(pak_path):,} bytes")

from pak_builder import get_filename_hash

# Files cần kiểm tra
check_files = [
    'natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_common.msg.22',
    'natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_purpose.msg.22',
    'natives/stm/_chainsaw/message/mes_main_conv/ch_mes_main_conv_cp51.msg.22',
    'natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_mainmenu.msg.22',
]

# Đọc entry table PAK
with open(pak_path, 'rb') as f:
    magic = f.read(4)
    version = struct.unpack('<I', f.read(4))[0]
    num_files = struct.unpack('<I', f.read(4))[0]
    f.read(4)  # fingerprint
    
    pak_hashes = set()
    pak_entries = []
    for i in range(num_files):
        h = struct.unpack('<Q', f.read(8))[0]
        off = struct.unpack('<q', f.read(8))[0]
        sc = struct.unpack('<q', f.read(8))[0]
        sd = struct.unpack('<q', f.read(8))[0]
        attr = struct.unpack('<q', f.read(8))[0]
        chk = struct.unpack('<Q', f.read(8))[0]
        pak_hashes.add(h)
        pak_entries.append((h, off, sc, sd))

print(f"PAK entries: {num_files}")
print()

print("=== Kiểm tra file trong PAK ===")
for fpath in check_files:
    vpath = '/' + fpath
    h = get_filename_hash(vpath)
    in_pak = h in pak_hashes
    print(f"  {'✓ IN PAK' if in_pak else '✗ NOT IN PAK'}: {fpath}")

print()

# -------------------------------------------------------
# Xem slot của ch_mes_main_sys_common idx=191 (ASSISTED)
# -------------------------------------------------------
p = os.path.join(EXTRACTED, r'natives\stm\_chainsaw\message\mes_main_sys\ch_mes_main_sys_common.msg.22.json')
with open(p, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== ch_mes_main_sys_common - ASSISTED (idx=191) slots ===")
entry = data['entries'][191]
print(f"name: {entry.get('name','')}")
for i, slot in enumerate(entry['content']):
    marker = ' <-- được ghi đè' if slot else ' <-- EMPTY (bỏ qua)'
    if slot or i <= 5:
        print(f"  slot[{i:2d}] = {repr(slot[:40]) if slot else '(empty)'}{marker}")

print()
print("Kết luận: import_translation ghi slot nào?")
print("  Logic: if content[i].strip() or i == 1: -> ghi")
print()
print("  slot[0]='ASSISTED' -> GHI: 'ĐƯỢC HỖ TRỢ'")
print("  slot[1]='ASSISTED' -> GHI: 'ĐƯỢC HỖ TRỢ'  (luôn ghi)")
print()
print("Nhưng game hiển thị 'ASSISTED'... Vậy file này CÓ trong PAK không?")
print()

# -------------------------------------------------------
# Kiểm tra xem file này có trong CSV đủ điều kiện compile không
# (import_translation chỉ compile file nào có trong translations_by_file)
# -------------------------------------------------------
print("=== Kiểm tra import_translation flow ===")
CSV = r'd:\RE4_VietHoa\vietnamese_translation.csv'
translations_by_file = {}
with open(CSV, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        file_path = row['File Path']
        idx = int(row['Entry Index'])
        viet = row['Vietnamese'].strip()
        if viet:
            if file_path not in translations_by_file:
                translations_by_file[file_path] = []
            translations_by_file[file_path].append((idx, viet))

# Normalize path
target_paths = [
    r'natives\stm\_chainsaw\message\mes_main_sys\ch_mes_main_sys_common.msg.22',
    r'natives\stm\_chainsaw\message\mes_main_sys\ch_mes_main_sys_purpose.msg.22',
    r'natives\stm\_chainsaw\message\mes_main_conv\ch_mes_main_conv_cp51.msg.22',
]

for tp in target_paths:
    if tp in translations_by_file:
        edits = translations_by_file[tp]
        print(f"  OK: {os.path.basename(tp)} -> {len(edits)} edits")
        # Show relevant idx
        for idx, viet in edits:
            if idx in [191, 192, 193, 3, 57]:
                print(f"    idx={idx} viet={viet[:40]}")
    else:
        print(f"  MISSING FROM translations_by_file: {tp}")
