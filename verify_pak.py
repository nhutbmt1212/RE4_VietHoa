import struct
import sys
sys.path.insert(0, r'd:\RE4_VietHoa')
from pak_builder import get_filename_hash

# Read my own patch_006.pak
pak_path = r'd:\Games\Resident Evil 4\re_chunk_000.pak.patch_006.pak'

with open(pak_path, 'rb') as f:
    magic = struct.unpack('<I', f.read(4))[0]
    version = struct.unpack('<i', f.read(4))[0]
    total = struct.unpack('<i', f.read(4))[0]
    fingerprint = struct.unpack('<I', f.read(4))[0]
    
    print(f'=== My patch_006.pak ===')
    print(f'Magic: 0x{magic:08X}  Version: {version}  Files: {total}  FP: 0x{fingerprint:08X}')
    
    hashes_in_pak = []
    for i in range(total):
        h = struct.unpack('<Q', f.read(8))[0]
        offset = struct.unpack('<q', f.read(8))[0]
        csz = struct.unpack('<q', f.read(8))[0]
        dsz = struct.unpack('<q', f.read(8))[0]
        attr = struct.unpack('<q', f.read(8))[0]
        chk = struct.unpack('<Q', f.read(8))[0]
        hashes_in_pak.append(h)
        print(f'  [{i}] hash=0x{h:016X}  offset={offset}  csz={csz}  dsz={dsz}  attr={attr}')

print()

# Read patch_005.pak and get ALL hashes for comparison
pak5_path = r'd:\Games\Resident Evil 4\re_chunk_000.pak.patch_005.pak'
pak5_hashes = set()
with open(pak5_path, 'rb') as f:
    f.read(4)  # magic
    ver5 = struct.unpack('<i', f.read(4))[0]
    total5 = struct.unpack('<i', f.read(4))[0]
    f.read(4)  # fingerprint
    print(f'=== patch_005.pak === Version: {ver5}  Files: {total5}')
    
    # Try with 48-byte entries
    for i in range(total5):
        h = struct.unpack('<Q', f.read(8))[0]
        f.read(40)  # rest of 48-byte entry
        pak5_hashes.add(h)

print(f'patch_005 has {len(pak5_hashes)} hashes loaded')
print()

# Now compute hashes for various path formats
paths_to_test = [
    '/natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22',
    'natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22',
    '/Natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22',
]
for p in paths_to_test:
    h = get_filename_hash(p)
    found = h in pak5_hashes
    match = h in hashes_in_pak
    print(f'Hash("{p}")')
    print(f'  = 0x{h:016X}  in_pak006={match}  in_pak005={found}')
