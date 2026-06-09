"""
Main PAK có version khác của file - size khác.
Tìm file ch_mes_main_sys_common bằng cách:
1. Decrypt các candidate files và tìm chuỗi 'ASSISTED'
2. Cũng thử tìm với size range

Hoặc: dùng approach khác - tìm hash trong patch_001 (bản DLC lớn nhất có thể có file này)
"""
import struct, sys, os, zlib
sys.path.insert(0, r'd:\RE4_VietHoa')
sys.path.insert(0, r'd:\RE4_VietHoa\tools\REMSG_Converter\src')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
from pak_builder import get_filename_hash
from REWString import decrypt

GAME_DIR  = r'd:\Games\Resident Evil 4'

our_hash = get_filename_hash('/natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_common.msg.22')
print(f"Our hash: {our_hash:016X}")

# Tìm trong MAIN PAK - thay vì dùng size, dùng hash range để tìm vị trí binary search
# (PAK entry table sorted by hash - binary search!)
main_pak = os.path.join(GAME_DIR, 're_chunk_000.pak')

with open(main_pak, 'rb') as f:
    f.read(4); f.read(4)
    num_files = struct.unpack('<I', f.read(4))[0]
    f.read(4)

ENTRY_SIZE = 48
HEADER_SIZE = 16

# Binary search cho our_hash trong main PAK
def read_entry(f, idx):
    f.seek(HEADER_SIZE + idx * ENTRY_SIZE)
    h   = struct.unpack('<Q', f.read(8))[0]
    off = struct.unpack('<q', f.read(8))[0]
    sc  = struct.unpack('<q', f.read(8))[0]
    sd  = struct.unpack('<q', f.read(8))[0]
    attr= struct.unpack('<q', f.read(8))[0]
    chk = struct.unpack('<Q', f.read(8))[0]
    return h, off, sc, sd, attr

print(f"\nBinary search for our hash in main PAK ({num_files:,} entries)...")
with open(main_pak, 'rb') as f:
    lo, hi = 0, num_files - 1
    found = False
    while lo <= hi:
        mid = (lo + hi) // 2
        h, off, sc, sd, attr = read_entry(f, mid)
        if h == our_hash:
            print(f"FOUND at idx={mid}: offset={off} sc={sc} sd={sd}")
            found = True
            break
        elif h < our_hash:
            lo = mid + 1
        else:
            hi = mid - 1
    
    if not found:
        print(f"NOT FOUND in main PAK!")
        # Show nearest entries
        print(f"\nNearest entries around our hash {our_hash:016X}:")
        for idx in [lo-2, lo-1, lo, lo+1, lo+2]:
            if 0 <= idx < num_files:
                h, off, sc, sd, attr = read_entry(f, idx)
                print(f"  idx={idx}: {h:016X} (sd={sd})")

print()

# Thử với no-slash
no_slash = get_filename_hash('natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_common.msg.22')
print(f"No-slash hash: {no_slash:016X}")
with open(main_pak, 'rb') as f:
    lo, hi = 0, num_files - 1
    found2 = False
    while lo <= hi:
        mid = (lo + hi) // 2
        h, off, sc, sd, attr = read_entry(f, mid)
        if h == no_slash:
            print(f"FOUND (no-slash) at idx={mid}: offset={off} sc={sc} sd={sd}")
            found2 = True
            break
        elif h < no_slash:
            lo = mid + 1
        else:
            hi = mid - 1
    if not found2:
        print(f"NOT FOUND (no-slash) in main PAK!")

print()

# Kết luận: nếu không có trong main PAK -> file này được game load từ đâu?
# -> Có thể từ loose files hoặc từ một streaming system khác
print("=== GIẢ THUYẾT MỚI ===")
print("Nếu file KHÔNG trong main PAK -> Game load từ:")
print("  1. Streaming file system riêng biệt")
print("  2. REFramework mod loader")
print("  3. Loose files trong thư mục game")
print()
print("Kiểm tra xem có thư mục 'natives' hay 'reframework' trong game dir không:")
game_dir = r'd:\Games\Resident Evil 4'
for item in os.listdir(game_dir):
    full = os.path.join(game_dir, item)
    is_dir = os.path.isdir(full)
    size = '' if is_dir else f' ({os.path.getsize(full):,}b)'
    print(f"  {'[DIR]' if is_dir else '[FILE]'} {item}{size}")
