"""
Fix trực tiếp: Ghi bản dịch thẳng vào file JSON rồi compile và deploy vào loose files
Không cần qua CSV pipeline

Các entry cần fix:
1. mc_mes_main_sys_mainmenu idx=0 (MC_Mes_Main_Sys_MainMenu_GameTitle) -> THE MERCENARIES -> LÍNH ĐÁNH THUÊ
2. ao_mes_main_sys_mainmenu idx=0 (AO_Mes_Main_Sys_MainMenu_GameTitle) -> SEPARATE WAYS -> CON ĐƯỜNG RIÊNG  
3. dev1_term_menu idx=65 (Dev1_Term_Menu_MainMenu_QuitGame) -> QUIT GAME -> THOÁT
4. ch_mes_main_sys_common idx=191 ASSISTED -> HỖTRỢ
5. ch_mes_main_sys_common idx=192 STANDARD -> TIÊU CHUẨN
6. ch_mes_main_sys_common idx=193 HARDCORE -> CỨNG RẮN
7. ch_mes_main_sys_purpose idx=3 "See what's taking so long" -> "Xem điều gì đang lâu"
"""
import json, os, sys, subprocess, shutil, struct, zlib
sys.path.insert(0, r'd:\RE4_VietHoa')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
from pak_builder import get_filename_hash

EXTRACTED  = r'd:\RE4_VietHoa\extracted_msg'
TOOLS_DIR  = r'd:\RE4_VietHoa\tools\REMSG_Converter\src'
GAME_DIR   = r'd:\Games\Resident Evil 4'
NATIVES    = os.path.join(GAME_DIR, 'natives')
PAK006     = os.path.join(GAME_DIR, 're_chunk_000.pak.patch_006.pak')

# Danh sách các fix trực tiếp
FIXES = [
    # (relative_path_from_extracted, entry_idx, vietnamese_text)
    (
        r'natives\stm\_mercenaries\message\mes_main_sys\mc_mes_main_sys_mainmenu.msg.22',
        0, 'LÍNH ĐÁNH THUÊ'
    ),
    (
        r'natives\stm\_anotherorder\message\mes_main_sys\ao_mes_main_sys_mainmenu.msg.22',
        0, 'CON ĐƯỜNG RIÊNG'
    ),
    (
        r'natives\stm\_chainsaw\message\dev1_term\dev1_term_menu.msg.22',
        65, 'THOÁT'
    ),
    (
        r'natives\stm\_chainsaw\message\mes_main_sys\ch_mes_main_sys_common.msg.22',
        191, 'HỖ TRỢ'
    ),
    (
        r'natives\stm\_chainsaw\message\mes_main_sys\ch_mes_main_sys_common.msg.22',
        192, 'TIÊU CHUẨN'
    ),
    (
        r'natives\stm\_chainsaw\message\mes_main_sys\ch_mes_main_sys_common.msg.22',
        193, 'CỨNG RẮN'
    ),
    (
        r'natives\stm\_chainsaw\message\mes_main_sys\ch_mes_main_sys_purpose.msg.22',
        3, 'Xem điều gì đang lâu vậy'
    ),
]

# Group fixes by file
fixes_by_file = {}
for rel, idx, viet in FIXES:
    if rel not in fixes_by_file:
        fixes_by_file[rel] = []
    fixes_by_file[rel].append((idx, viet))

print(f"Files to fix: {len(fixes_by_file)}")
print()

for rel_path, edits in fixes_by_file.items():
    msg_path  = os.path.join(EXTRACTED, rel_path)
    json_path = msg_path + '.json'

    if not os.path.exists(json_path):
        print(f"MISSING JSON: {json_path}")
        continue

    print(f"Processing: {os.path.basename(rel_path)}")

    # Đọc JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Áp dụng edits
    for idx, viet in edits:
        entry = data['entries'][idx]
        name  = entry.get('name', '')
        print(f"  idx={idx} ({name})")
        content = entry['content']
        for i in range(len(content)):
            if content[i].strip() or i == 1:
                old = content[i]
                content[i] = viet
                if old != viet:
                    print(f"    slot[{i}]: '{old[:30]}' -> '{viet}'")

    # Lưu JSON
    with open(json_path, 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Compile .msg.22 dùng REMSG_Converter
    cmd = ['python', os.path.join(TOOLS_DIR, 'main.py'),
           '-i', msg_path, '-e', json_path, '-m', 'json']
    res = subprocess.run(cmd, capture_output=True, text=True)
    new_msg = msg_path + '.new'

    if res.returncode != 0 or not os.path.exists(new_msg):
        print(f"  COMPILE FAILED: {res.stderr[:200]}")
        continue

    compiled_data = open(new_msg, 'rb').read()
    os.remove(new_msg)
    print(f"  Compiled: {len(compiled_data):,} bytes")

    # Deploy vào loose files nếu tồn tại
    loose_path = os.path.join(NATIVES, rel_path.replace('natives\\', ''))
    if os.path.exists(loose_path):
        # Backup
        bak = loose_path + '.bak2'
        if not os.path.exists(bak):
            shutil.copy2(loose_path, bak)
        with open(loose_path, 'wb') as f:
            f.write(compiled_data)
        print(f"  [LOOSE DEPLOYED] {loose_path}")
    else:
        # Tạo thư mục nếu cần
        os.makedirs(os.path.dirname(loose_path), exist_ok=True)
        with open(loose_path, 'wb') as f:
            f.write(compiled_data)
        print(f"  [NEW LOOSE FILE] {loose_path}")

    # Cập nhật msg gốc cho lần compile sau
    with open(msg_path, 'wb') as f:
        f.write(compiled_data)

    print()

print("DONE! Khởi động lại game để kiểm tra.")
print()
print("Cần rebuild PAK006 để đồng bộ:")
print("  python import_translation.py")
