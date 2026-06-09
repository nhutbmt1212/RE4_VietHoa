"""
Verify what's actually in the installed PAK file.
Lists all files and their sizes.
"""
import struct
import os

PAK_PATH = r"d:\Games\Resident Evil 4\re_chunk_000.pak.patch_006.pak"

if not os.path.exists(PAK_PATH):
    print(f"PAK not installed: {PAK_PATH}")
    exit()

print(f"Verifying PAK: {PAK_PATH}")
print(f"File size: {os.path.getsize(PAK_PATH):,} bytes\n")

with open(PAK_PATH, 'rb') as f:
    # Read header
    magic = struct.unpack('<I', f.read(4))[0]
    version = struct.unpack('<i', f.read(4))[0]
    total_files = struct.unpack('<i', f.read(4))[0]
    fingerprint = struct.unpack('<I', f.read(4))[0]
    
    print(f"Magic:       0x{magic:08X} ({'OK' if magic == 0x414B504B else 'WRONG'})")
    print(f"Version:     0x{version:08X}")
    print(f"Total files: {total_files}")
    print(f"Fingerprint: 0x{fingerprint:08X} ({'OK' if fingerprint == 0xDEC0ADDE else 'WRONG'})")
    
    # Read entries
    entries = []
    for _ in range(total_files):
        hash_name = struct.unpack('<Q', f.read(8))[0]
        offset = struct.unpack('<q', f.read(8))[0]
        compressed_size = struct.unpack('<q', f.read(8))[0]
        decompressed_size = struct.unpack('<q', f.read(8))[0]
        attributes = struct.unpack('<q', f.read(8))[0]
        checksum = struct.unpack('<Q', f.read(8))[0]
        entries.append({
            'hash': hash_name,
            'offset': offset,
            'compressed': compressed_size,
            'decompressed': decompressed_size,
            'attr': attributes
        })

print(f"\nEntries in PAK: {len(entries)}")

# Check for any suspiciously small or zero-size entries
print("\n--- Suspicious entries (size < 100 bytes) ---")
for i, e in enumerate(entries):
    if e['decompressed'] < 100:
        print(f"  Entry {i}: hash=0x{e['hash']:016X} decomp={e['decompressed']} comp={e['compressed']}")

# Count .new files that might have slipped in (can't tell by hash alone but check count)
print(f"\nTotal entries: {len(entries)} (expected ~509)")
if len(entries) > 515:
    print(f"WARNING: More files than expected! Possible .new/.json files packed in.")
elif len(entries) == 510:
    print(f"WARNING: Might have 1 extra .new file packed!")
else:
    print(f"Count looks reasonable.")
