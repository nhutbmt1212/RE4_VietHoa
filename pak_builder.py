"""
pak_builder.py
--------------
Builds a RE Engine PAK patch file from a source directory.
Replicates the logic of REE.Packer (C# tool) entirely in Python.

PAK Format (version 4):
  Header (16 bytes):
    - Magic:       4 bytes  = 0x414B504B ("KPKA")
    - Version:     4 bytes  = 4
    - TotalFiles:  4 bytes
    - Fingerprint: 4 bytes  = 0xDEC0ADDE

  Entry Table (48 bytes per entry, sorted by dwHashName):
    - dwHashName:         8 bytes  (Murmur3 upper<<32 | lower)
    - dwOffset:           8 bytes
    - dwCompressedSize:   8 bytes
    - dwDecompressedSize: 8 bytes
    - dwAttributes:       8 bytes  (0=none, 1=inflate/deflate)
    - dwChecksum:         8 bytes  (xxHash64<<32 | xxHash32)

  File data (after entry table, contiguous)
"""

import os
import struct
import zlib


# ─────────────────────────────────────────────
#  Murmur3-32  (matches C# HashCore32)
# ─────────────────────────────────────────────
def _rotl32(x, r):
    x &= 0xFFFFFFFF
    return ((x << r) | (x >> (32 - r))) & 0xFFFFFFFF


def murmur3_32(data: bytes, seed: int = 0xFFFFFFFF) -> int:
    c1 = 0xCC9E2D51
    c2 = 0x1B873593
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
            k1 = _rotl32(k1, 15)
            k1 = (k1 * c2) & 0xFFFFFFFF
            h1 ^= k1
            h1 = _rotl32(h1, 13)
            h1 = (h1 * 5 + 0xE6546B64) & 0xFFFFFFFF
        elif len(chunk) == 3:
            k1 = chunk[0] | (chunk[1] << 8) | (chunk[2] << 16)
            k1 = (k1 * c1) & 0xFFFFFFFF
            k1 = _rotl32(k1, 15)
            k1 = (k1 * c2) & 0xFFFFFFFF
            h1 ^= k1
        elif len(chunk) == 2:
            k1 = chunk[0] | (chunk[1] << 8)
            k1 = (k1 * c1) & 0xFFFFFFFF
            k1 = _rotl32(k1, 15)
            k1 = (k1 * c2) & 0xFFFFFFFF
            h1 ^= k1
        elif len(chunk) == 1:
            k1 = chunk[0]
            k1 = (k1 * c1) & 0xFFFFFFFF
            k1 = _rotl32(k1, 15)
            k1 = (k1 * c2) & 0xFFFFFFFF
            h1 ^= k1
        i += 4

    h1 ^= stream_length & 0xFFFFFFFF
    # fmix32
    h1 ^= h1 >> 16
    h1 = (h1 * 0x85EBCA6B) & 0xFFFFFFFF
    h1 ^= h1 >> 13
    h1 = (h1 * 0xC2B2AE35) & 0xFFFFFFFF
    h1 ^= h1 >> 16
    return h1


def get_filename_hash(filename: str) -> int:
    """Combine Murmur3 of upper-case and lower-case UTF-16LE."""
    upper_bytes = filename.upper().encode('utf-16-le')
    lower_bytes = filename.lower().encode('utf-16-le')
    h_upper = murmur3_32(upper_bytes)
    h_lower = murmur3_32(lower_bytes)
    return (h_upper << 32) | h_lower


# ─────────────────────────────────────────────
#  xxHash32 and xxHash64  (matches C# xxHash)
# ─────────────────────────────────────────────
PRIME32_1 = 0x9E3779B1
PRIME32_2 = 0x85EBCA77
PRIME32_3 = 0xC2B2AE3D
PRIME32_4 = 0x27D4EB2F
PRIME32_5 = 0x165667B1

PRIME64_1 = 0x9E3779B185EBCA87
PRIME64_2 = 0xC2B2AE3D27D4EB4F
PRIME64_3 = 0x165667B19E3779F9
PRIME64_4 = 0x85EBCA77C2B2AE63
PRIME64_5 = 0x27D4EB2F165667C5

M32 = 0xFFFFFFFF
M64 = 0xFFFFFFFFFFFFFFFF


def _rotl32x(x, r):
    x &= M32
    return ((x << r) | (x >> (32 - r))) & M32


def _rotl64(x, r):
    x &= M64
    return ((x << r) | (x >> (64 - r))) & M64


def xxhash32(data: bytes, seed: int = 0xFFFFFFFF) -> int:
    seed &= M32
    offset = 0
    end = len(data)

    if len(data) < 16:
        h = (seed + PRIME32_5) & M32
    else:
        v1 = (seed + PRIME32_1 + PRIME32_2) & M32
        v2 = (seed + PRIME32_2) & M32
        v3 = seed
        v4 = (seed - PRIME32_1) & M32

        while offset <= end - 16:
            v1 = _rotl32x((v1 + struct.unpack_from('<I', data, offset)[0] * PRIME32_2) & M32, 13)
            v1 = (v1 * PRIME32_1) & M32; offset += 4
            v2 = _rotl32x((v2 + struct.unpack_from('<I', data, offset)[0] * PRIME32_2) & M32, 13)
            v2 = (v2 * PRIME32_1) & M32; offset += 4
            v3 = _rotl32x((v3 + struct.unpack_from('<I', data, offset)[0] * PRIME32_2) & M32, 13)
            v3 = (v3 * PRIME32_1) & M32; offset += 4
            v4 = _rotl32x((v4 + struct.unpack_from('<I', data, offset)[0] * PRIME32_2) & M32, 13)
            v4 = (v4 * PRIME32_1) & M32; offset += 4

        h = (_rotl32x(v1, 1) + _rotl32x(v2, 7) + _rotl32x(v3, 12) + _rotl32x(v4, 18)) & M32

    h = (h + len(data)) & M32

    while offset + 4 <= end:
        h = (_rotl32x((h + struct.unpack_from('<I', data, offset)[0] * PRIME32_3) & M32, 17) * PRIME32_4) & M32
        offset += 4

    while offset < end:
        h = (_rotl32x((h + (data[offset] & 0xFF) * PRIME32_5) & M32, 11) * PRIME32_1) & M32
        offset += 1

    h ^= h >> 15; h = (h * PRIME32_2) & M32
    h ^= h >> 13; h = (h * PRIME32_3) & M32
    h ^= h >> 16
    return h


def xxhash64(data: bytes, seed: int = 0xFFFFFFFF) -> int:
    seed &= M64
    offset = 0
    end = len(data)

    def round64(acc, val):
        acc = (acc + (val & M64) * PRIME64_2) & M64
        acc = _rotl64(acc, 31)
        return (acc * PRIME64_1) & M64

    def merge64(acc, val):
        val = round64(0, val)
        acc ^= val
        return (acc * PRIME64_1 + PRIME64_4) & M64

    if len(data) < 32:
        h = (seed + PRIME64_5) & M64
    else:
        v1 = (seed + PRIME64_1 + PRIME64_2) & M64
        v2 = (seed + PRIME64_2) & M64
        v3 = seed
        v4 = (seed - PRIME64_1) & M64

        while offset <= end - 32:
            v1 = round64(v1, struct.unpack_from('<Q', data, offset)[0]); offset += 8
            v2 = round64(v2, struct.unpack_from('<Q', data, offset)[0]); offset += 8
            v3 = round64(v3, struct.unpack_from('<Q', data, offset)[0]); offset += 8
            v4 = round64(v4, struct.unpack_from('<Q', data, offset)[0]); offset += 8

        h = (_rotl64(v1, 1) + _rotl64(v2, 7) + _rotl64(v3, 12) + _rotl64(v4, 18)) & M64
        h = merge64(h, v1)
        h = merge64(h, v2)
        h = merge64(h, v3)
        h = merge64(h, v4)

    h = (h + len(data)) & M64

    while offset + 8 <= end:
        h ^= round64(0, struct.unpack_from('<Q', data, offset)[0])
        h = (_rotl64(h, 27) * PRIME64_1 + PRIME64_4) & M64; offset += 8

    if offset + 4 <= end:
        h ^= (struct.unpack_from('<I', data, offset)[0] * PRIME64_1) & M64
        h = (_rotl64(h, 23) * PRIME64_2 + PRIME64_3) & M64; offset += 4

    while offset < end:
        h ^= ((data[offset] & 0xFF) * PRIME64_5) & M64
        h = (_rotl64(h, 11) * PRIME64_1) & M64; offset += 1

    h ^= h >> 33; h = (h * PRIME64_2) & M64
    h ^= h >> 29; h = (h * PRIME64_3) & M64
    h ^= h >> 32
    return h


def get_data_checksum(data: bytes) -> int:
    """Matches PakHash.iGetDataHash: (xxHash64 << 32) | xxHash32_of_xxHash64_bytes"""
    h64 = xxhash64(data) & M64
    h64_bytes = struct.pack('<Q', h64)
    h32 = xxhash32(h64_bytes) & M32
    # Combine and keep within uint64 range
    return ((h64 & 0xFFFFFFFF) << 32) | h32



# ─────────────────────────────────────────────
#  Compression: raw Deflate (no zlib header)
# ─────────────────────────────────────────────
# Magic numbers that must NOT be compressed (matches C# logic)
NO_COMPRESS_MAGIC1 = {0x75B22630, 0x564D4552, 0x44484B42, 0x4B504B41}
NO_COMPRESS_MAGIC2 = {0x70797466}

COMPRESSION_NONE    = 0
COMPRESSION_INFLATE = 1  # raw deflate


def should_compress(data: bytes) -> bool:
    if len(data) < 8:
        return False
    m1 = struct.unpack_from('<I', data, 0)[0]
    m2 = struct.unpack_from('<I', data, 4)[0]
    if m1 in NO_COMPRESS_MAGIC1 or m2 in NO_COMPRESS_MAGIC2:
        return False
    return True


def inflate_compress(data: bytes) -> bytes:
    """Raw deflate – strips the 2-byte zlib header and 4-byte Adler32 trailer."""
    compressed = zlib.compress(data, level=6)
    # zlib adds 2-byte header + 4-byte checksum; raw deflate strips both
    return compressed[2:-4]


# ─────────────────────────────────────────────
#  PAK builder
# ─────────────────────────────────────────────
def build_pak(src_folder: str, output_pak: str):
    """
    Pack all files in src_folder into output_pak.
    Folder structure relative to src_folder becomes the virtual path inside the PAK.
    """
    PAK_MAGIC       = 0x414B504B
    PAK_VERSION     = 0x00080004   # matches actual game PAK version
    PAK_FINGERPRINT = 0xDEC0ADDE
    ENTRY_SIZE      = 48  # bytes per entry

    # Collect files
    all_files = []
    for root, _, files in os.walk(src_folder):
        for fname in files:
            full = os.path.join(root, fname)
            rel  = os.path.relpath(full, src_folder).replace('\\', '/')
            all_files.append((rel, full))

    total = len(all_files)
    print(f"[PAK] Packing {total} file(s) into: {output_pak}")

    entries = []
    file_data_blobs = []

    HEADER_SIZE = 16
    data_start  = HEADER_SIZE + total * ENTRY_SIZE
    current_offset = data_start

    for rel_path, full_path in all_files:
        raw = open(full_path, 'rb').read()

        # Hash
        virtual_path = '/' + rel_path
        hash_name = get_filename_hash(virtual_path)

        # Checksum
        checksum = get_data_checksum(raw)

        # Compress?
        if should_compress(raw):
            compressed = inflate_compress(raw)
            attr = COMPRESSION_INFLATE
        else:
            compressed = raw
            attr = COMPRESSION_NONE

        entry = {
            'hash_name':        hash_name,
            'offset':           current_offset,
            'compressed_size':  len(compressed),
            'decompressed_size':len(raw),
            'attributes':       attr,
            'checksum':         checksum,
        }
        entries.append(entry)
        file_data_blobs.append(compressed)
        current_offset += len(compressed)

        print(f"  [PACK] {virtual_path}  ({len(raw)} -> {len(compressed)} bytes)")

    # Sort entry table by hash_name (ascending)
    combined = sorted(zip(entries, file_data_blobs), key=lambda x: x[0]['hash_name'])
    entries_sorted = [c[0] for c in combined]

    with open(output_pak, 'wb') as f:
        # Header
        f.write(struct.pack('<I', PAK_MAGIC))
        f.write(struct.pack('<i', PAK_VERSION))
        f.write(struct.pack('<i', total))
        f.write(struct.pack('<I', PAK_FINGERPRINT))

        # Entry table placeholder (will seek back and fill)
        f.write(b'\x00' * (total * ENTRY_SIZE))

        # File data (in order of collection, NOT sorted)
        for _, blob in combined:
            f.write(blob)

        # Seek back and write sorted entry table
        f.seek(HEADER_SIZE)
        for e in entries_sorted:
            f.write(struct.pack('<Q', e['hash_name']))
            f.write(struct.pack('<q', e['offset']))
            f.write(struct.pack('<q', e['compressed_size']))
            f.write(struct.pack('<q', e['decompressed_size']))
            f.write(struct.pack('<q', e['attributes']))
            f.write(struct.pack('<Q', e['checksum']))

    print(f"[PAK] Done! Output: {output_pak}  ({os.path.getsize(output_pak):,} bytes)")


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python pak_builder.py <src_folder> <output.pak>")
        sys.exit(1)
    build_pak(sys.argv[1], sys.argv[2])
