import os
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

hashes = {}
base_name = 'natives/stm/_chainsaw/message/dev1_term/dev1_term_menu'
for lang in ['', '_en', '_ja', '_fr', '_it', '_de', '_es', '_ru', '_zh', '_ko', '_pt', '_ar']:
    name = f'/{base_name}{lang}.msg.22'
    hashes[get_filename_hash(name)] = name
    
base_name2 = 'natives/stm/_mercenaries/message/mes_main_sys/mc_mes_main_sys_mainmenu'
for lang in ['', '_en', '_ja', '_fr', '_it', '_de', '_es', '_ru', '_zh', '_ko', '_pt', '_ar']:
    name = f'/{base_name2}{lang}.msg.22'
    hashes[get_filename_hash(name)] = name

game_dir = r'd:\Games\Resident Evil 4'
for i in range(6):
    suffix = f'.patch_{i:03d}.pak' if i > 0 else ''
    pak_path = os.path.join(game_dir, f're_chunk_000.pak{suffix}')
    
    if not os.path.exists(pak_path):
        continue
        
    found = []
    with open(pak_path, 'rb') as f:
        f.read(8)
        total = struct.unpack('<i', f.read(4))[0]
        f.read(4)
        for _ in range(total):
            h = struct.unpack('<Q', f.read(8))[0]
            if h in hashes:
                found.append(hashes[h])
            f.read(40)
            
    if found:
        print(f'Found files in {os.path.basename(pak_path)}:')
        for name in found:
            print(f'  {name}')
