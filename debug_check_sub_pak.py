import struct, sys, os, zlib
sys.path.insert(0, r'd:\RE4_VietHoa')
sys.path.insert(0, r'd:\RE4_VietHoa\tools\REMSG_Converter\src')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
from pak_builder import get_filename_hash
from REWString import decrypt

GAME_DIR = r'd:\Games\Resident Evil 4'
pak006   = os.path.join(GAME_DIR, 're_chunk_000.pak.patch_006.pak')

def extract_from_pak006(vpath):
    h = get_filename_hash('/' + vpath)
    with open(pak006, 'rb') as f:
        f.read(4); f.read(4)
        num_files = struct.unpack('<I', f.read(4))[0]
        f.read(4)
        for i in range(num_files):
            eh = struct.unpack('<Q', f.read(8))[0]
            off = struct.unpack('<q', f.read(8))[0]
            sc  = struct.unpack('<q', f.read(8))[0]
            sd  = struct.unpack('<q', f.read(8))[0]
            attr= struct.unpack('<q', f.read(8))[0]
            chk = struct.unpack('<Q', f.read(8))[0]
            if eh == h:
                f.seek(off)
                compressed = f.read(sc)
                return zlib.decompress(compressed, -15) if attr == 1 else compressed
    return None

data = extract_from_pak006('natives/stm/_chainsaw/message/mes_main_conv/ch_mes_main_conv_cp11.msg.22')
if not data:
    print("Không tìm thấy ch_mes_main_conv_cp11 trong PAK006!")
else:
    print("Tìm thấy file trong PAK. Kích thước:", len(data))
    dec_str = decrypt(data).decode('utf-16-le', errors='replace')
    print("=== Nội dung đầu tiên ===")
    print(dec_str[:1000].replace('\x00', ' '))
