import struct, sys, os, zlib, subprocess
sys.path.insert(0, r'd:\RE4_VietHoa')
from pak_builder import get_filename_hash

GAME_DIR = r'd:\Games\Resident Evil 4'
PAK006 = os.path.join(GAME_DIR, 're_chunk_000.pak.patch_006.pak')
TOOLS_DIR = r'd:\RE4_VietHoa\tools\REMSG_Converter\src'

def extract_from_pak(vpath, out_path):
    h = get_filename_hash('/' + vpath)
    with open(PAK006, 'rb') as f:
        f.read(8)
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
                comp = f.read(sc)
                data = zlib.decompress(comp, -15) if attr == 1 else comp
                with open(out_path, 'wb') as outf:
                    outf.write(data)
                return True
    return False

test_msg = 'cp11_test.msg.22'
test_json = 'cp11_test.msg.22.json'
if extract_from_pak('natives/stm/_chainsaw/message/mes_main_conv/ch_mes_main_conv_cp11.msg.22', test_msg):
    print("Extracted from PAK successfully.")
    # Decompile it using REMSG_Converter
    subprocess.run(['python', os.path.join(TOOLS_DIR, 'main.py'), '-i', test_msg, '-e', test_json, '-m', 'json'])
    
    import json
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    with open(test_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("First 5 entries:")
    for e in data['entries'][:5]:
        eng = e['content'][1] if len(e['content']) > 1 else ''
        vie = e['content'][0] if len(e['content']) > 0 else ''
        if eng:
            print(f"EN: {eng[:60]}")
            print(f"VI: {vie[:60]}")
            print('-')
    
    # Check entry 16 "How far could he have gone?"
    e = data['entries'][16]
    eng = e['content'][1] if len(e['content']) > 1 else ''
    vie = e['content'][0] if len(e['content']) > 0 else ''
    print("Entry 16:")
    print(f"EN: {eng}")
    print(f"VI: {vie}")
else:
    print("Not found in PAK.")
