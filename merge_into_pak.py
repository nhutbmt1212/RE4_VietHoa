"""
merge_into_pak.py
-----------------
Reads an existing game PAK file, appends new files from a directory,
and writes a new merged PAK. Used to inject mod files into existing patches.
"""

import os
import sys
import struct
import zlib
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pak_builder import (
    get_filename_hash, get_data_checksum,
    inflate_compress, should_compress,
    COMPRESSION_NONE, COMPRESSION_INFLATE,
    M32, M64
)

PAK_MAGIC       = 0x414B504B
ENTRY_SIZE      = 48


def read_pak_entries(pak_path):
    """Read all entries from an existing PAK file."""
    entries = []
    with open(pak_path, 'rb') as f:
        magic       = struct.unpack('<I', f.read(4))[0]
        version     = struct.unpack('<I', f.read(4))[0]
        total_files = struct.unpack('<i', f.read(4))[0]
        fingerprint = struct.unpack('<I', f.read(4))[0]

        print(f"Reading {os.path.basename(pak_path)}: magic=0x{magic:08X} ver={version} files={total_files} fp=0x{fingerprint:08X}")

        for _ in range(total_files):
            h       = struct.unpack('<Q', f.read(8))[0]
            offset  = struct.unpack('<q', f.read(8))[0]
            csz     = struct.unpack('<q', f.read(8))[0]
            dsz     = struct.unpack('<q', f.read(8))[0]
            attr    = struct.unpack('<q', f.read(8))[0]
            chk     = struct.unpack('<Q', f.read(8))[0]
            entries.append({
                'hash_name': h,
                'offset': offset,
                'compressed_size': csz,
                'decompressed_size': dsz,
                'attributes': attr,
                'checksum': chk,
            })

        # Read all file data blobs in offset order
        data_map = {}
        sorted_entries = sorted(entries, key=lambda e: e['offset'])
        for entry in sorted_entries:
            f.seek(entry['offset'])
            data_map[entry['hash_name']] = f.read(entry['compressed_size'])

    return version, fingerprint, entries, data_map


def merge_pak(source_pak, mod_dir, output_pak):
    """
    Merge files from mod_dir into source_pak and write to output_pak.
    Mod files override existing entries with the same hash.
    """
    version, fingerprint, orig_entries, orig_data = read_pak_entries(source_pak)

    # Build dict of original entries by hash
    orig_by_hash = {e['hash_name']: e for e in orig_entries}

    # Collect mod files
    mod_files = []
    for root, _, files in os.walk(mod_dir):
        for fname in files:
            full = os.path.join(root, fname)
            rel  = os.path.relpath(full, mod_dir).replace('\\', '/')
            mod_files.append((rel, full))

    # Build mod entries
    mod_entries = []
    mod_data    = {}
    for rel_path, full_path in mod_files:
        raw = open(full_path, 'rb').read()
        virtual_path = '/' + rel_path
        h = get_filename_hash(virtual_path)

        if should_compress(raw):
            compressed = inflate_compress(raw)
            attr = COMPRESSION_INFLATE
        else:
            compressed = raw
            attr = COMPRESSION_NONE

        entry = {
            'hash_name':         h,
            'offset':            0,   # will be filled below
            'compressed_size':   len(compressed),
            'decompressed_size': len(raw),
            'attributes':        attr,
            'checksum':          get_data_checksum(raw),
        }
        mod_entries.append(entry)
        mod_data[h] = compressed
        action = 'OVERRIDE' if h in orig_by_hash else 'NEW'
        print(f"  [{action}] {virtual_path}  ({len(raw)} -> {len(compressed)} bytes)")

    # Merge: start with originals, override with mod entries
    final_by_hash = dict(orig_by_hash)
    final_data    = dict(orig_data)
    for entry in mod_entries:
        final_by_hash[entry['hash_name']] = entry
        final_data[entry['hash_name']]    = mod_data[entry['hash_name']]

    # Write merged PAK
    all_entries = sorted(final_by_hash.values(), key=lambda e: e['hash_name'])
    total = len(all_entries)
    header_size = 16
    entry_table_size = total * ENTRY_SIZE
    current_offset = header_size + entry_table_size

    # Assign offsets
    for e in all_entries:
        e['offset'] = current_offset
        current_offset += final_data[e['hash_name']].__len__()

    # Make a backup of the original
    backup = source_pak + '.bak'
    if not os.path.exists(backup):
        print(f"Backing up original to {backup}")
        shutil.copy2(source_pak, backup)

    with open(output_pak, 'wb') as f:
        # Header
        f.write(struct.pack('<I', PAK_MAGIC))
        f.write(struct.pack('<I', version))      # preserve original version
        f.write(struct.pack('<i', total))
        f.write(struct.pack('<I', fingerprint))  # preserve original fingerprint

        # Entry table placeholder
        f.write(b'\x00' * entry_table_size)

        # File data
        for e in all_entries:
            f.write(final_data[e['hash_name']])

        # Write entry table
        f.seek(header_size)
        for e in all_entries:
            f.write(struct.pack('<Q', e['hash_name'] & M64))
            f.write(struct.pack('<q', e['offset']))
            f.write(struct.pack('<q', e['compressed_size']))
            f.write(struct.pack('<q', e['decompressed_size']))
            f.write(struct.pack('<q', e['attributes']))
            f.write(struct.pack('<Q', e['checksum'] & M64))

    print(f"\n[OK] Merged PAK written: {output_pak}  ({os.path.getsize(output_pak):,} bytes)")
    print(f"     Original entries: {len(orig_entries)}  Mod entries: {len(mod_entries)}  Total: {total}")


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python merge_into_pak.py <source.pak> <mod_dir> <output.pak>")
        sys.exit(1)
    merge_pak(sys.argv[1], sys.argv[2], sys.argv[3])
