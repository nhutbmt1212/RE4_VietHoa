"""
Kiểm tra file nào CÓ trong PAK_006 vs file nào KHÔNG có
Đặc biệt: dev1_term_menu, ch_mes_develop_ao, ch_mes_main_sys_purpose
"""
import struct, sys, os, zlib
sys.path.insert(0, r'd:\RE4_VietHoa')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
from pak_builder import get_filename_hash

GAME_DIR = r'd:\Games\Resident Evil 4'
pak006   = os.path.join(GAME_DIR, 're_chunk_000.pak.patch_006.pak')

# Đọc tất cả hash trong PAK_006
with open(pak006, 'rb') as f:
    f.read(4); f.read(4)
    num_files = struct.unpack('<I', f.read(4))[0]
    f.read(4)
    pak_hashes = set()
    for i in range(num_files):
        h = struct.unpack('<Q', f.read(8))[0]
        f.read(40)
        pak_hashes.add(h)

print(f"PAK_006 total files: {num_files}")
print()

# Danh sách file CẦN kiểm tra
check = [
    # Main menu items (SEPARATE WAYS, THE MERCENARIES, EXIT)
    'natives/stm/_chainsaw/message/mes_develop_misc/ch_mes_develop_ao.msg.22',
    'natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22',
    'natives/stm/_chainsaw/message/dev1_term/dev1_term_storeanddlc.msg.22',
    # Difficulty names
    'natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_common.msg.22',
    'natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_mainmenu.msg.22',
    # Subtitle
    'natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_purpose.msg.22',
    'natives/stm/_chainsaw/message/mes_main_conv/ch_mes_main_conv_cp51.msg.22',
    # HUD (Skip Cutscene, Pause Menu)
    'natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_hud.msg.22',
    'natives/stm/_chainsaw/message/dev1_term/dev1_term_hud.msg.22',
    # Mercenaries & Separate Ways menus
    'natives/stm/_mercenaries/message/mes_main_sys/mc_mes_main_sys_mainmenu.msg.22',
    'natives/stm/_anotherorder/message/mes_main_sys/ao_mes_main_sys_mainmenu.msg.22',
]

print("=== File trong PAK_006? ===")
missing = []
for fpath in check:
    h = get_filename_hash('/' + fpath)
    in_pak = h in pak_hashes
    status = '✓ IN PAK' if in_pak else '✗ MISSING'
    print(f"  [{status}] {os.path.basename(fpath)}")
    if not in_pak:
        missing.append(fpath)

print()
print(f"Missing count: {len(missing)}")
for m in missing:
    print(f"  -> {m}")
