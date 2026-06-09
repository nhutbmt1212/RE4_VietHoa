"""
Tìm hash KHÔNG có dấu / trong patch_001~005
Game có thể dùng path không có leading slash
"""
import struct, sys, os
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
sys.path.insert(0, r'd:\RE4_VietHoa')
from pak_builder import get_filename_hash, murmur3_32

GAME_DIR = r'd:\Games\Resident Evil 4'

# Tính hash cả 2 cách
def hash_no_slash(path):
    """Path không có leading /"""
    upper_bytes = path.upper().encode('utf-16-le')
    lower_bytes = path.lower().encode('utf-16-le')
    h_upper = murmur3_32(upper_bytes)
    h_lower = murmur3_32(lower_bytes)
    return (h_upper << 32) | h_lower

targets_no_slash = {
    'natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_common.msg.22': 'ch_mes_main_sys_common',
    'natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_purpose.msg.22': 'ch_mes_main_sys_purpose',
    'natives/stm/_chainsaw/message/mes_main_conv/ch_mes_main_conv_cp51.msg.22': 'ch_mes_main_conv_cp51',
    'natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22': 'dev1_term_menu',
    'natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_mainmenu.msg.22': 'ch_mes_main_sys_mainmenu',
}

print("Hash WITHOUT leading slash:")
target_hash_map = {}
for path, name in targets_no_slash.items():
    h = hash_no_slash(path)
    print(f"  {h:016X} : {name}")
    target_hash_map[h] = name

print()
print("Hash WITH leading slash (current):")
for path, name in targets_no_slash.items():
    h = get_filename_hash('/' + path)
    print(f"  {h:016X} : {name}")

print()

# Tìm trong patch_005 (lớn nhất - bản update mới nhất của Capcom)
pak_path = os.path.join(GAME_DIR, "re_chunk_000.pak.patch_005.pak")
print(f"Scanning patch_005.pak ({os.path.getsize(pak_path):,} bytes)...")

with open(pak_path, 'rb') as f:
    f.read(4); f.read(4)
    num_files = struct.unpack('<I', f.read(4))[0]
    f.read(4)
    
    print(f"  {num_files} files")
    found = []
    for i in range(num_files):
        h = struct.unpack('<Q', f.read(8))[0]
        off = struct.unpack('<q', f.read(8))[0]
        sc = struct.unpack('<q', f.read(8))[0]
        sd = struct.unpack('<q', f.read(8))[0]
        attr = struct.unpack('<q', f.read(8))[0]
        chk = struct.unpack('<Q', f.read(8))[0]
        if h in target_hash_map:
            found.append((h, off, sc, sd, attr))
            print(f"  FOUND (no-slash): {h:016X} -> {target_hash_map[h]}")

if not found:
    print("  KHÔNG TÌM THẤY trong patch_005!")
    print()
    
    # Thử scan toàn bộ patch_005 để lấy 5 hash đầu/cuối và so sánh
    with open(pak_path, 'rb') as f:
        f.read(4); f.read(4)
        num_files = struct.unpack('<I', f.read(4))[0]
        f.read(4)
        first_hashes = []
        for i in range(min(5, num_files)):
            h = struct.unpack('<Q', f.read(8))[0]
            f.read(40)  # skip rest of entry
            first_hashes.append(h)
    
    print(f"  First 5 hashes in patch_005: {[f'{h:016X}' for h in first_hashes]}")
    print()
    print("  NOTE: Nếu không tìm thấy ở cả 2 dạng hash, nghĩa là")
    print("  game lấy file từ MAIN PAK (57GB) chứ không phải từ patch_001~005.")
    print("  patch_006 của chúng ta PHẢI override được main pak.")
    print()
    print("  -> Kiểm tra: thử verify bằng cách extract 1 file từ patch_006 và xem nội dung")

print()
print("=== Verify: đọc ch_mes_main_sys_common từ patch_006 của chúng ta ===")
pak006 = os.path.join(GAME_DIR, "re_chunk_000.pak.patch_006.pak")
target_hash_slash = get_filename_hash('/natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_common.msg.22')

with open(pak006, 'rb') as f:
    f.read(4); f.read(4)
    num_files = struct.unpack('<I', f.read(4))[0]
    f.read(4)
    
    for i in range(num_files):
        h = struct.unpack('<Q', f.read(8))[0]
        off = struct.unpack('<q', f.read(8))[0]
        sc = struct.unpack('<q', f.read(8))[0]
        sd = struct.unpack('<q', f.read(8))[0]
        attr = struct.unpack('<q', f.read(8))[0]
        chk = struct.unpack('<Q', f.read(8))[0]
        
        if h == target_hash_slash:
            print(f"  Found ch_mes_main_sys_common in patch_006")
            print(f"  offset={off} compressed={sc} decompressed={sd} attr={attr}")
            
            # Extract and decompress
            with open(pak006, 'rb') as f2:
                f2.seek(off)
                compressed_data = f2.read(sc)
            
            import zlib
            if attr == 1:
                raw = zlib.decompress(compressed_data, -15)
            else:
                raw = compressed_data
            
            print(f"  Extracted {len(raw)} bytes, MSG magic: {raw[:4].hex()}")
            
            # Parse msg22 format để xem entry 191 (ASSISTED)
            # Đơn giản: tìm chuỗi 'ĐƯỢC HỖ TRỢ' trong raw
            viet_text = 'ĐƯỢC HỖ TRỢ'.encode('utf-16-le')
            if viet_text in raw:
                print(f"  ✓ 'ĐƯỢC HỖ TRỢ' FOUND in extracted file!")
            else:
                print(f"  ✗ 'ĐƯỢC HỖ TRỢ' NOT FOUND in extracted file!")
                # Thử tìm ASSISTED
                eng_text = 'ASSISTED'.encode('utf-16-le')
                if eng_text in raw:
                    print(f"  'ASSISTED' still present (not overwritten)")
                else:
                    print(f"  'ASSISTED' also not found (file content issue)")
            break
