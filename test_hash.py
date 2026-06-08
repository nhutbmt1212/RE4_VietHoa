import struct

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
            k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
            k1 = (k1 * c2) & 0xFFFFFFFF
            h1 ^= k1
            h1 = ((h1 << 13) | (h1 >> 19)) & 0xFFFFFFFF
            h1 = (h1 * 5 + 0xE6546B64) & 0xFFFFFFFF
        elif len(chunk) == 3:
            k1 = chunk[0] | (chunk[1] << 8) | (chunk[2] << 16)
            k1 = (k1 * c1) & 0xFFFFFFFF
            k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
            k1 = (k1 * c2) & 0xFFFFFFFF
            h1 ^= k1
        elif len(chunk) == 2:
            k1 = chunk[0] | (chunk[1] << 8)
            k1 = (k1 * c1) & 0xFFFFFFFF
            k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
            k1 = (k1 * c2) & 0xFFFFFFFF
            h1 ^= k1
        elif len(chunk) == 1:
            k1 = chunk[0]
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
    upper_bytes = filename.upper().encode('utf-16-le')
    lower_bytes = filename.lower().encode('utf-16-le')
    h_upper = murmur3_32(upper_bytes)
    h_lower = murmur3_32(lower_bytes)
    return (h_upper << 32) | h_lower

pak_path = r'd:\Games\Resident Evil 4\re_chunk_000.pak.patch_005.pak'
hashes = set()
with open(pak_path, 'rb') as f:
    f.read(8)
    total = struct.unpack('<i', f.read(4))[0]
    f.read(4)
    for _ in range(total):
        h = struct.unpack('<Q', f.read(8))[0]
        hashes.add(h)
        f.read(40)

test_paths = [
    'natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22',
    'natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22'.replace('/', '\\'),
    '/natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22',
    'stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22',
]

for p in test_paths:
    h = get_filename_hash(p)
    print(f"{p} -> {hex(h)}  In pak? {h in hashes}")
