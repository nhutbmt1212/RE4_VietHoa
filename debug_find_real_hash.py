"""
Tìm hash thực của các file trong MAIN PAK (57GB)
Bằng cách so sánh với file gốc - dùng binary search trên entry table
"""
import struct, sys, os, zlib
sys.path.insert(0, r'd:\RE4_VietHoa')
sys.path.insert(0, r'd:\RE4_VietHoa\tools\REMSG_Converter\src')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
from pak_builder import get_filename_hash
from REWString import decrypt

GAME_DIR  = r'd:\Games\Resident Evil 4'
EXTRACTED = r'd:\RE4_VietHoa\extracted_msg'

# Chiến lược: lấy nội dung của file gốc từ extracted_msg,
# rồi tìm trong main PAK file nào có cùng decompressed size
# -> Từ đó suy ra hash thực tế của game

# File cần kiểm tra: ch_mes_main_sys_common.msg.22
orig_path = os.path.join(EXTRACTED, 
    r'natives\stm\_chainsaw\message\mes_main_sys\ch_mes_main_sys_common.msg.22')
orig_size = os.path.getsize(orig_path)
print(f"Original ch_mes_main_sys_common size: {orig_size} bytes")

# Tính hash của chúng ta
our_hash = get_filename_hash('/natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_common.msg.22')
print(f"Our hash (with /): {our_hash:016X}")

no_slash_hash = get_filename_hash('natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_common.msg.22')
print(f"Our hash (no /):   {no_slash_hash:016X}")

print()

# Tìm trong main PAK bằng cách scan entry table
# Main PAK có thể có entry size khác nhau - cần kiểm tra format
main_pak = os.path.join(GAME_DIR, 're_chunk_000.pak')
print(f"Main PAK size: {os.path.getsize(main_pak):,} bytes")

with open(main_pak, 'rb') as f:
    magic = f.read(4)
    version = struct.unpack('<I', f.read(4))[0]
    num_files = struct.unpack('<I', f.read(4))[0]
    fingerprint = struct.unpack('<I', f.read(4))[0]
    print(f"Main PAK: magic={magic} version={version:08X} files={num_files} fp={fingerprint:08X}")

ENTRY_SIZE = 48  # 8+8+8+8+8+8
HEADER_SIZE = 16
data_start = HEADER_SIZE + num_files * ENTRY_SIZE

print(f"Entry table: {num_files} entries")
print(f"Data starts at: {data_start:,}")
print()

# Scan entry table để tìm file có decompressed_size == orig_size
print(f"Searching for decompressed_size == {orig_size}...")
candidates = []
BATCH = 10000
with open(main_pak, 'rb') as f:
    f.seek(HEADER_SIZE)
    for i in range(num_files):
        h   = struct.unpack('<Q', f.read(8))[0]
        off = struct.unpack('<q', f.read(8))[0]
        sc  = struct.unpack('<q', f.read(8))[0]
        sd  = struct.unpack('<q', f.read(8))[0]
        attr= struct.unpack('<q', f.read(8))[0]
        chk = struct.unpack('<Q', f.read(8))[0]
        if sd == orig_size:
            candidates.append((h, off, sc, sd, attr))
        if i % 100000 == 0 and i > 0:
            print(f"  Scanned {i:,}/{num_files:,}... candidates so far: {len(candidates)}")

print(f"Found {len(candidates)} candidates with decompressed_size={orig_size}")
print()

# Verify candidates bằng cách extract và tìm 'ASSISTED' trong đó
for h, off, sc, sd, attr in candidates[:20]:
    # Kiểm tra xem hash này có phải là no-slash hay with-slash của chúng ta không
    is_our_hash = (h == our_hash or h == no_slash_hash)
    
    with open(main_pak, 'rb') as f:
        f.seek(off)
        compressed = f.read(sc)
    
    try:
        if attr == 1:
            raw = zlib.decompress(compressed, -15)
        else:
            raw = compressed
        
        dec = decrypt(raw)
        assisted = 'ASSISTED'.encode('utf-16-le')
        if assisted in dec:
            print(f"MATCH! hash={h:016X} {'(OUR HASH!)' if is_our_hash else '(DIFFERENT HASH)'}")
            print(f"  offset={off} sc={sc} sd={sd}")
            print(f"  'ASSISTED' found in decrypted content")
            # Compare hash
            if not is_our_hash:
                print(f"  -> Game uses hash: {h:016X}")
                print(f"  -> We use hash:    {our_hash:016X}")
                print(f"  -> MISMATCH! Our file won't override game's file")
    except Exception as e:
        pass
