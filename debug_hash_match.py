"""
Kiểm tra xem patch_001 đến patch_005 có override file của chúng ta không
(RE Engine load PAK theo thứ tự số: patch_005 > patch_004 > ... > patch_001 > main)
patch_006 của chúng ta sẽ có PRIORITY CAO NHẤT -> phải override tất cả

Nhưng cần xác nhận: patch_006 có hash KHỚP với hash trong patch_001-005 không?
Nếu hash của chúng ta tính sai, game sẽ không tìm thấy file.

Kiểm tra bằng cách tìm hash của ch_mes_main_sys_common trong patch_005 (bản gốc của game)
"""
import struct, sys, zlib, os
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
sys.path.insert(0, r'd:\RE4_VietHoa')
from pak_builder import get_filename_hash

GAME_DIR = r'd:\Games\Resident Evil 4'

target_files = [
    '/natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_common.msg.22',
    '/natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_purpose.msg.22',
    '/natives/stm/_chainsaw/message/mes_main_conv/ch_mes_main_conv_cp51.msg.22',
    '/natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_mainmenu.msg.22',
    '/natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22',
]

target_hashes = {get_filename_hash(p): p for p in target_files}
print("Target hashes:")
for h, p in target_hashes.items():
    print(f"  {h:016X} : {os.path.basename(p)}")
print()

# Tìm trong patch_005 (lớn nhất = bản update game mới nhất)
for patch_num in [5, 4, 3, 2, 1]:
    pak_path = os.path.join(GAME_DIR, f"re_chunk_000.pak.patch_00{patch_num}.pak")
    if not os.path.exists(pak_path):
        continue
    
    pak_size = os.path.getsize(pak_path)
    with open(pak_path, 'rb') as f:
        magic = f.read(4)
        version = struct.unpack('<I', f.read(4))[0]
        num_files = struct.unpack('<I', f.read(4))[0]
        f.read(4)
        
        found_targets = []
        for i in range(num_files):
            h = struct.unpack('<Q', f.read(8))[0]
            off = struct.unpack('<q', f.read(8))[0]
            sc = struct.unpack('<q', f.read(8))[0]
            sd = struct.unpack('<q', f.read(8))[0]
            attr = struct.unpack('<q', f.read(8))[0]
            chk = struct.unpack('<Q', f.read(8))[0]
            if h in target_hashes:
                found_targets.append((h, off, sc, sd, attr))
    
    if found_targets:
        print(f"patch_00{patch_num}.pak ({pak_size:,} bytes, {num_files} files):")
        for h, off, sc, sd, attr in found_targets:
            print(f"  FOUND: {target_hashes[h]}")
            print(f"    offset={off} size={sc}/{sd}")
    else:
        print(f"patch_00{patch_num}.pak: none of target files found")

print()
print("=== KẾT LUẬN ===")
print("Nếu các file trên nằm trong patch_001~005, game dùng patch_006 của chúng ta")
print("  (patch số cao hơn = ưu tiên cao hơn)")
print()
print("Nếu KHÔNG tìm thấy trong patch_001~005:")
print("  -> hash của chúng ta tính ĐÚNG nhưng game vẫn lấy từ main pak")
print("  -> Có thể cần kiểm tra lại encoding của path string trong hash")
