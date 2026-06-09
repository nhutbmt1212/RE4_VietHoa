"""
debug_pak_content.py
Đọc PAK patch và liệt kê các file trong đó, kiểm tra một file cụ thể
để xem slot nào có tiếng Việt.
"""
import os, struct, zlib, json

PAK_PATH = r"d:\Games\Resident Evil 4\re_chunk_000.pak.patch_006.pak"
EXTRACTED = r"d:\RE4_VietHoa\extracted_msg"

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
        elif len(chunk) == 3:
            k1 = chunk[0] | (chunk[1] << 8) | (chunk[2] << 16)
        elif len(chunk) == 2:
            k1 = chunk[0] | (chunk[1] << 8)
        elif len(chunk) == 1:
            k1 = chunk[0]
        if k1:
            k1 = (k1 * c1) & 0xFFFFFFFF
            k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
            k1 = (k1 * c2) & 0xFFFFFFFF
            h1 ^= k1
        if len(chunk) == 4:
            h1 = ((h1 << 13) | (h1 >> 19)) & 0xFFFFFFFF
            h1 = (h1 * 5 + 0xE6546B64) & 0xFFFFFFFF
        i += 4
    h1 ^= stream_length & 0xFFFFFFFF
    h1 ^= h1 >> 16
    h1 = (h1 * 0x85EBCA6B) & 0xFFFFFFFF
    h1 ^= h1 >> 13
    h1 = (h1 * 0xC2B2AE35) & 0xFFFFFFFF
    h1 ^= h1 >> 16
    return h1

def get_filename_hash(filename: str) -> int:
    upper_bytes = filename.upper().encode('utf-16-le')
    lower_bytes = filename.lower().encode('utf-16-le')
    h_upper = murmur3_32(upper_bytes)
    h_lower = murmur3_32(lower_bytes)
    return (h_upper << 32) | h_lower

# Build a mapping from hash -> known file paths from extracted_msg
print("Building hash map from extracted files...")
hash_to_path = {}
for root, dirs, files in os.walk(EXTRACTED):
    for fname in files:
        if fname.endswith('.json') or fname.endswith('.bak'):
            continue
        full = os.path.join(root, fname)
        rel = os.path.relpath(full, EXTRACTED).replace('\\', '/')
        virtual_path = '/' + rel
        h = get_filename_hash(virtual_path)
        hash_to_path[h] = rel

print(f"Known paths: {len(hash_to_path)}")

# Read PAK
print(f"\nReading PAK: {PAK_PATH}")
with open(PAK_PATH, 'rb') as f:
    magic, version, total_files, fingerprint = struct.unpack('<IiII', f.read(16))
    print(f"Magic: {magic:#010x}, Version: {version:#010x}, Files: {total_files}")
    
    entries = []
    for i in range(total_files):
        hash_name, offset, comp_size, decomp_size, attrs, checksum = struct.unpack('<QqqqQQ', f.read(48))
        entries.append({
            'hash': hash_name,
            'offset': offset,
            'comp_size': comp_size,
            'decomp_size': decomp_size,
            'attrs': attrs,
        })
    
    print(f"\nFiles in PAK ({total_files} total):")
    known = 0
    unknown = 0
    file_data_cache = {}
    
    for entry in entries:
        h = entry['hash']
        path = hash_to_path.get(h, None)
        if path:
            known += 1
        else:
            unknown += 1
        
        # Read and decompress the file data
        f.seek(entry['offset'])
        comp_data = f.read(entry['comp_size'])
        if entry['attrs'] == 1:
            try:
                raw = zlib.decompress(comp_data, -15)
            except:
                raw = None
        else:
            raw = comp_data
        
        if path:
            file_data_cache[path] = raw
            print(f"  {path}")
    
    print(f"\nKnown: {known}, Unknown: {unknown}")

# Check a specific speach file from PAK
print("\n=== Checking speach content in PAK ===")
for path, raw in file_data_cache.items():
    if 'speach' in path and raw:
        print(f"File: {path}, size: {len(raw)} bytes")
        # Find corresponding JSON in extracted_msg
        json_path = os.path.join(EXTRACTED, path) + ".json"
        if os.path.exists(json_path):
            with open(json_path, encoding='utf-8') as jf:
                original = json.load(jf)
            print(f"  Original has {len(original['entries'])} entries")
        # Try to parse the raw binary (first few bytes for magic)
        if len(raw) >= 4:
            print(f"  Magic: {raw[:4].hex()} ({raw[:4]})")
        break

# Also check subtitle/conv files
print("\n=== Files in PAK by category ===")
cats = {}
for path in file_data_cache:
    parts = path.split('/')
    cat = parts[-2] if len(parts) >= 2 else 'other'
    cats[cat] = cats.get(cat, 0) + 1

for cat, count in sorted(cats.items()):
    print(f"  {cat}: {count} files")
