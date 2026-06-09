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

test_msg = 'tutorial_test.msg.22'
test_json = 'tutorial_test.msg.22.json'
if extract_from_pak('natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_tutorial.msg.22', test_msg):
    print("Extracted from PAK successfully.")
    subprocess.run(['python', os.path.join(TOOLS_DIR, 'main.py'), '-i', test_msg, '-m', 'json'])
    import json
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    try:
        with open(test_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for e in data['entries']:
            if 'Crouch' in str(e):
                print(f"EN: {e['content'][1] if len(e['content']) > 1 else ''}")
                print(f"VI: {e['content'][0] if len(e['content']) > 0 else ''}")
                print('-')
    except Exception as ex:
        print("Error reading json:", ex)
else:
    print("Not found in PAK.")
