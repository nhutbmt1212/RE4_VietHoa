"""
deploy_loose.py
Lấy file đã compiled từ PAK_006 và copy vào đúng thư mục natives/
để override loose files cũ đang block bản dịch.
"""
import os, sys, struct, zlib, shutil
sys.path.insert(0, r'd:\RE4_VietHoa')
sys.path.insert(0, r'd:\RE4_VietHoa\tools\REMSG_Converter\src')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
from pak_builder import get_filename_hash

GAME_DIR  = r'd:\Games\Resident Evil 4'
EXTRACTED = r'd:\RE4_VietHoa\extracted_msg'
pak006    = os.path.join(GAME_DIR, 're_chunk_000.pak.patch_006.pak')
natives   = os.path.join(GAME_DIR, 'natives')

# Đọc toàn bộ PAK_006 vào dict: hash -> (offset, sc, sd, attr)
print("Reading PAK_006 entries...")
pak_index = {}
with open(pak006, 'rb') as f:
    f.read(4); f.read(4)
    num_files = struct.unpack('<I', f.read(4))[0]
    f.read(4)
    for i in range(num_files):
        h   = struct.unpack('<Q', f.read(8))[0]
        off = struct.unpack('<q', f.read(8))[0]
        sc  = struct.unpack('<q', f.read(8))[0]
        sd  = struct.unpack('<q', f.read(8))[0]
        attr= struct.unpack('<q', f.read(8))[0]
        chk = struct.unpack('<Q', f.read(8))[0]
        pak_index[h] = (off, sc, sd, attr)

print(f"PAK_006: {num_files} files indexed")
print()

def extract_from_pak006(vpath):
    """Extract và decompress file từ PAK_006 theo virtual path"""
    h = get_filename_hash('/' + vpath)
    if h not in pak_index:
        return None
    off, sc, sd, attr = pak_index[h]
    with open(pak006, 'rb') as f:
        f.seek(off)
        compressed = f.read(sc)
    if attr == 1:
        return zlib.decompress(compressed, -15)
    return compressed

# Danh sách loose files cần cập nhật (case-insensitive path từ log)
# Game dùng path lowercase, chúng ta map đến virtual path trong PAK
loose_to_virtual = []

# Quét tất cả loose files trong natives/ và tìm path tương ứng trong PAK
for root, dirs, files in os.walk(natives):
    for fname in files:
        loose_path = os.path.join(root, fname)
        # Convert loose path -> virtual PAK path
        rel = os.path.relpath(loose_path, GAME_DIR).replace('\\', '/')
        vpath = rel  # e.g. "natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22"
        
        h = get_filename_hash('/' + vpath)
        if h in pak_index:
            loose_to_virtual.append((loose_path, vpath, h))
        else:
            # Thử lowercase
            h2 = get_filename_hash('/' + vpath.lower())
            if h2 in pak_index:
                loose_to_virtual.append((loose_path, vpath.lower(), h2))
            else:
                print(f"  [NO MATCH in PAK] {fname}")

print(f"Loose files with PAK match: {len(loose_to_virtual)}")
print()

# Deploy: extract từ PAK_006 và copy vào loose files location
deployed = 0
for loose_path, vpath, h in loose_to_virtual:
    data = extract_from_pak006(vpath)
    if data is None:
        # Try without slash
        h_alt = get_filename_hash(vpath)
        if h_alt in pak_index:
            off, sc, sd, attr = pak_index[h_alt]
            with open(pak006, 'rb') as f:
                f.seek(off)
                compressed = f.read(sc)
            data = zlib.decompress(compressed, -15) if attr == 1 else compressed
    
    if data:
        # Backup nếu chưa có
        bak = loose_path + '.bak_original'
        if not os.path.exists(bak):
            shutil.copy2(loose_path, bak)
        
        with open(loose_path, 'wb') as f:
            f.write(data)
        print(f"  [DEPLOYED] {os.path.basename(loose_path)} ({len(data):,} bytes)")
        deployed += 1
    else:
        print(f"  [FAILED] {os.path.basename(vpath)}")

print()
print(f"Total deployed: {deployed}/{len(loose_to_virtual)}")
print()
print("Hãy khởi động lại game để kiểm tra!")
