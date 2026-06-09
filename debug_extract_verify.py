"""
Extract file từ patch_006 PAK, decrypt chuỗi và xác nhận nội dung tiếng Việt
"""
import sys, os, zlib, struct
sys.path.insert(0, r'd:\RE4_VietHoa')
sys.path.insert(0, r'd:\RE4_VietHoa\tools\REMSG_Converter\src')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

from pak_builder import get_filename_hash
from REWString import decrypt

GAME_DIR = r'd:\Games\Resident Evil 4'
pak006   = os.path.join(GAME_DIR, "re_chunk_000.pak.patch_006.pak")

def extract_from_pak(pak_path, vpath):
    target_hash = get_filename_hash('/' + vpath)
    with open(pak_path, 'rb') as f:
        f.read(4); f.read(4)
        num_files = struct.unpack('<I', f.read(4))[0]
        f.read(4)
        entries = []
        for i in range(num_files):
            h   = struct.unpack('<Q', f.read(8))[0]
            off = struct.unpack('<q', f.read(8))[0]
            sc  = struct.unpack('<q', f.read(8))[0]
            sd  = struct.unpack('<q', f.read(8))[0]
            attr= struct.unpack('<q', f.read(8))[0]
            chk = struct.unpack('<Q', f.read(8))[0]
            if h == target_hash:
                f.seek(off)
                compressed = f.read(sc)
                if attr == 1:
                    return zlib.decompress(compressed, -15)
                return compressed
    return None

# Extract ch_mes_main_sys_common
vpath = 'natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_common.msg.22'
raw = extract_from_pak(pak006, vpath)

if raw is None:
    print("ERROR: File not found in PAK!")
else:
    print(f"Extracted: {len(raw)} bytes, magic={raw[:4].hex()}")
    
    # MSG22 format: header, then string pool at some offset
    # String pool is encrypted with XOR key
    # Let's find the string pool offset from header
    # MSG format header: magic(4) + version(4) + numEntries(4) + numLanguages(4) + ...
    
    # Try to find the string pool by looking for encrypted 'ASSISTED'
    # 'ASSISTED'.encode('utf-16-le') then encrypt with XOR key
    from REWString import encrypt, KEY
    
    # Test: encrypt 'ASSISTED\x00' and search
    assisted_plain = 'ASSISTED\x00'.encode('utf-16-le')
    # Encrypt needs to know the starting position (XOR is position-dependent)
    # We need to try all possible start offsets
    
    viet_plain = 'ĐƯỢC HỖ TRỢ\x00'.encode('utf-16-le')
    
    print(f"\nSearching for encrypted strings...")
    print(f"  Plaintext 'ASSISTED' UTF-16LE: {assisted_plain.hex()}")
    
    # Bruteforce: try encrypting at each possible start offset
    found_assisted = []
    found_viet = []
    
    for start_offset in range(0, len(raw) - len(assisted_plain)):
        # Encrypt 'ASSISTED' starting at this offset in the key cycle
        encrypted_test = bytearray()
        prev = 0
        # XOR key is position-dependent: KEY[i & 0xF]
        # But the start_offset tells us which position in KEY cycle
        for j, byte in enumerate(assisted_plain):
            pos = (start_offset + j) & 0xF
            enc_byte = byte ^ prev ^ KEY[pos]
            encrypted_test.append(enc_byte)
            prev = enc_byte
        
        if raw[start_offset:start_offset+len(assisted_plain)] == bytes(encrypted_test):
            found_assisted.append(start_offset)
    
    if found_assisted:
        print(f"  'ASSISTED' found encrypted at offsets: {found_assisted[:5]}")
    else:
        print(f"  'ASSISTED' NOT found (wrong encrypt algorithm?)")
    
    # Try decrypt the whole file and search plaintext
    print()
    print("Trying full file decrypt...")
    try:
        decrypted = decrypt(raw)
        # Search for ASSISTED in decrypted
        assisted_utf16 = 'ASSISTED'.encode('utf-16-le')
        viet_utf16 = 'ĐƯỢC HỖ TRỢ'.encode('utf-16-le')
        
        pos_a = decrypted.find(assisted_utf16)
        pos_v = decrypted.find(viet_utf16)
        
        print(f"  After full decrypt:")
        print(f"    'ASSISTED' at: {pos_a}")
        print(f"    'ĐƯỢC HỖ TRỢ' at: {pos_v}")
    except Exception as e:
        print(f"  Full decrypt error: {e}")

    # Thử parse msg header để tìm string pool offset
    print()
    print("MSG22 header bytes:")
    for i in range(0, min(64, len(raw)), 4):
        val = struct.unpack_from('<I', raw, i)[0] if i+4 <= len(raw) else 0
        print(f"  [{i:3d}] {raw[i:i+4].hex()} = {val}")
