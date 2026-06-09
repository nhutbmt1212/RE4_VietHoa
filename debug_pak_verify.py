"""
debug_pak_verify.py
Đọc PAK patch, giải nén một file speach và kiểm tra REMSG_Converter
xem text tiếng Việt có được ghi vào đúng slot không.
"""
import os, struct, zlib, json, subprocess, shutil, tempfile

PAK_PATH = r"d:\Games\Resident Evil 4\re_chunk_000.pak.patch_006.pak"
EXTRACTED = r"d:\RE4_VietHoa\extracted_msg"
SCRIPT_DIR = r"d:\RE4_VietHoa"
TOOLS_DIR = os.path.join(SCRIPT_DIR, "tools", "REMSG_Converter", "src")

def murmur3_32(data: bytes, seed: int = 0xFFFFFFFF) -> int:
    c1, c2 = 0xCC9E2D51, 0x1B873593
    h1 = seed & 0xFFFFFFFF
    stream_length = 0
    i = 0
    while i < len(data):
        chunk = data[i:i+4]
        stream_length += len(chunk)
        k1 = 0
        if len(chunk) == 4:
            k1 = struct.unpack_from('<I', chunk)[0]
            k1 = (k1 * c1) & 0xFFFFFFFF
            k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
            k1 = (k1 * c2) & 0xFFFFFFFF
            h1 ^= k1
            h1 = ((h1 << 13) | (h1 >> 19)) & 0xFFFFFFFF
            h1 = (h1 * 5 + 0xE6546B64) & 0xFFFFFFFF
        elif len(chunk) > 0:
            for b in range(len(chunk)):
                if b == 0: k1 = chunk[0]
                elif b == 1: k1 |= chunk[1] << 8
                elif b == 2: k1 |= chunk[2] << 16
            k1 = (k1 * c1) & 0xFFFFFFFF
            k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
            k1 = (k1 * c2) & 0xFFFFFFFF
            h1 ^= k1
        i += 4
    h1 ^= stream_length & 0xFFFFFFFF
    h1 ^= h1 >> 16
    h1 = (h1 * 0x85EBCA6B) & 0xFFFFFFFF
    h1 ^= h1 >> 13
    h1 = (h1 * 0xC2B2AE35) & 0xFFFFFFFF
    h1 ^= h1 >> 16
    return h1

def get_filename_hash(filename: str) -> int:
    h_upper = murmur3_32(filename.upper().encode('utf-16-le'))
    h_lower = murmur3_32(filename.lower().encode('utf-16-le'))
    return (h_upper << 32) | h_lower

# Find the hash for the speach file
TARGET_PATH = "natives/stm/_chainsaw/message/mes_main_speach/ch_mes_main_speach.msg.22"
target_hash = get_filename_hash('/' + TARGET_PATH)
print(f"Looking for: /{TARGET_PATH}")
print(f"Hash: {target_hash:#018x}")

# Also try conv file
CONV_PATH = "natives/stm/_chainsaw/message/mes_main_conv/ch_mes_main_bino_cp13.msg.22"
conv_hash = get_filename_hash('/' + CONV_PATH)

with open(PAK_PATH, 'rb') as f:
    magic, version, total, fingerprint = struct.unpack('<IiII', f.read(16))
    
    entries = []
    for i in range(total):
        data = struct.unpack('<QqqqQQ', f.read(48))
        entries.append({
            'hash': data[0], 'offset': data[1],
            'comp_size': data[2], 'decomp_size': data[3],
            'attrs': data[4]
        })
    
    # Find our target entries
    for path, h in [(TARGET_PATH, target_hash), (CONV_PATH, conv_hash)]:
        print(f"\n--- {path} ---")
        found = None
        for entry in entries:
            if entry['hash'] == h:
                found = entry
                break
        
        if not found:
            print("NOT FOUND in PAK!")
            continue
        
        print(f"Found! offset={found['offset']}, comp={found['comp_size']}, decomp={found['decomp_size']}, attrs={found['attrs']}")
        
        # Decompress
        f.seek(found['offset'])
        comp_data = f.read(found['comp_size'])
        if found['attrs'] == 1:
            raw = zlib.decompress(comp_data, -15)
        else:
            raw = comp_data
        
        # Save to temp and use REMSG_Converter to parse back to JSON
        tmpdir = tempfile.mkdtemp()
        try:
            fname = os.path.basename(path)
            tmp_msg = os.path.join(tmpdir, fname)
            with open(tmp_msg, 'wb') as tf:
                tf.write(raw)
            
            remsg_script = os.path.join(TOOLS_DIR, "main.py")
            if os.path.exists(remsg_script):
                cmd = ["python", remsg_script, "-i", tmp_msg, "-m", "msg"]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                tmp_json = tmp_msg + ".json"
                
                if os.path.exists(tmp_json):
                    with open(tmp_json, encoding='utf-8') as jf:
                        data_parsed = json.load(jf)
                    
                    print(f"Entries: {len(data_parsed['entries'])}")
                    
                    # Find first entry with Vietnamese
                    viet_found = False
                    for entry_data in data_parsed['entries']:
                        content = entry_data['content']
                        for i, c in enumerate(content):
                            if c and any(ord(ch) > 0x1EA0 and ord(ch) < 0x1EF9 for ch in c):
                                print(f"Vietnamese found at slot [{i}]: {c[:60]!r}")
                                viet_found = True
                                break
                        if viet_found:
                            # Show context
                            print("Slots around Vietnamese:")
                            for i, c in enumerate(content[:8]):
                                status = " <-- VIETNAMESE" if (c and any(ord(ch) > 0x1EA0 and ord(ch) < 0x1EF9 for ch in c)) else ""
                                print(f"  [{i}]: {c[:60]!r}{status}")
                            break
                    
                    if not viet_found:
                        # Show first entry with content
                        for entry_data in data_parsed['entries']:
                            content = entry_data['content']
                            real = [(i, c) for i, c in enumerate(content) if c and c.strip() and '#Rejected#' not in c]
                            if real:
                                print(f"First entry with real content: {entry_data['name']}")
                                for i, c in real[:5]:
                                    print(f"  [{i}]: {c[:60]!r}")
                                print("No Vietnamese found in any slot!")
                                break
                else:
                    print(f"JSON not generated. stderr: {res.stderr[:200]}")
            else:
                print(f"REMSG_Converter not found at: {remsg_script}")
                # Just show raw bytes
                print(f"Raw data (first 64 bytes): {raw[:64].hex()}")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
