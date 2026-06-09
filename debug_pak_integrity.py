"""
Kiểm tra hash path convention - RE Engine dùng forward slash hay backslash?
Hash cần khớp chính xác với cách game tính.
"""
import sys, struct, os
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
sys.path.insert(0, r'd:\RE4_VietHoa')
from pak_builder import get_filename_hash

# Test path conventions
test_paths = [
    # Forward slash versions
    '/natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_common.msg.22',
    '/natives/stm/_chainsaw/message/mes_main_conv/ch_mes_main_conv_cp51.msg.22',
    '/natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_purpose.msg.22',
    # Backslash versions
    r'\natives\stm\_chainsaw\message\mes_main_sys\ch_mes_main_sys_common.msg.22',
]

print("=== Hash tests ===")
for p in test_paths:
    h = get_filename_hash(p)
    print(f"  {h:016X} : {p}")

print()

# Đọc PAK và show actual hashes + thử match
GAME_DIR = r'd:\Games\Resident Evil 4'
pak_path = os.path.join(GAME_DIR, "re_chunk_000.pak.patch_006.pak")

with open(pak_path, 'rb') as f:
    f.read(4)   # magic
    f.read(4)   # version
    num_files = struct.unpack('<I', f.read(4))[0]
    f.read(4)   # fingerprint
    
    pak_entries = []
    for i in range(num_files):
        h = struct.unpack('<Q', f.read(8))[0]
        off = struct.unpack('<q', f.read(8))[0]
        sc = struct.unpack('<q', f.read(8))[0]
        sd = struct.unpack('<q', f.read(8))[0]
        attr = struct.unpack('<q', f.read(8))[0]
        chk = struct.unpack('<Q', f.read(8))[0]
        pak_entries.append((h, off, sc, sd, attr))

print(f"PAK has {num_files} entries")
print()

# Show first 5 and last 5 entries
print("First 5 PAK hashes:")
for h, off, sc, sd, attr in pak_entries[:5]:
    print(f"  {h:016X} offset={off} size={sc}/{sd}")

print()
print("Last 5 PAK hashes:")
for h, off, sc, sd, attr in pak_entries[-5:]:
    print(f"  {h:016X} offset={off} size={sc}/{sd}")

print()

# Kiểm tra xem offset có hợp lý không
HEADER = 16
ENTRY_SIZE = 48
data_start = HEADER + num_files * ENTRY_SIZE
print(f"Data starts at: {data_start}")
print(f"PAK file size: {os.path.getsize(pak_path):,}")

# Check offsets are valid
bad_offsets = 0
for h, off, sc, sd, attr in pak_entries:
    if off < data_start or off + sc > os.path.getsize(pak_path):
        bad_offsets += 1
        print(f"  BAD OFFSET: hash={h:016X} off={off} sc={sc}")

if bad_offsets == 0:
    print("✓ All offsets are valid!")
else:
    print(f"✗ {bad_offsets} bad offsets found!")

print()

# Kiểm tra sorted order
print("Checking sort order...")
prev_h = 0
out_of_order = 0
for i, (h, off, sc, sd, attr) in enumerate(pak_entries):
    if h < prev_h:
        out_of_order += 1
        print(f"  OUT OF ORDER at idx={i}: {prev_h:016X} -> {h:016X}")
    prev_h = h

if out_of_order == 0:
    print("✓ Entry table is properly sorted!")
else:
    print(f"✗ {out_of_order} out-of-order entries!")

print()

# Kiểm tra: file ch_mes_main_sys_common có đúng hash không?
target = '/natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_common.msg.22'
target_hash = get_filename_hash(target)
print(f"Target hash for ch_mes_main_sys_common: {target_hash:016X}")
found = any(h == target_hash for h, *_ in pak_entries)
print(f"Found in PAK: {found}")

# Thử đọc nội dung actual của entry đó từ PAK và kiểm tra có phải msg file không
if found:
    for h, off, sc, sd, attr in pak_entries:
        if h == target_hash:
            print(f"  offset={off} size={sc}/{sd} attr={attr}")
            with open(pak_path, 'rb') as f:
                f.seek(off)
                raw = f.read(min(sc, 200))
            print(f"  First 8 bytes: {raw[:8].hex()}")
            # RE MSG magic: 4D 53 47 00 or similar
            print(f"  Magic check: {raw[:4]}")
            
            # If compressed, decompress
            if attr == 1:
                import zlib
                try:
                    decompressed = zlib.decompress(raw[:sc] if sc <= 200 else raw, -15)
                    print(f"  Decompressed first 8 bytes: {decompressed[:8].hex()}")
                    print(f"  MSG magic: {decompressed[:4]}")
                except Exception as e:
                    print(f"  Decompress error: {e}")
            break
