"""
DEBUG STEP 4: Kiểm tra PAK hiện tại có chứa file ao_mes_main_sys_mainmenu không?
Và kiểm tra xem ch_mes_develop_misc (file chứa menu title như SEPARATE WAYS trên màn hình)
"""
import os, sys, json, csv, struct
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

GAME_DIR   = r"d:\Games\Resident Evil 4"
CSV        = r'd:\RE4_VietHoa\vietnamese_translation.csv'
EXTRACTED  = r'd:\RE4_VietHoa\extracted_msg'

# -------------------------------------------------------
# STEP 4A: Kiểm tra PAK patch_006 có file nào bên trong
# -------------------------------------------------------
pak_path = os.path.join(GAME_DIR, "re_chunk_000.pak.patch_006.pak")
print(f"=== PAK Patch 006: {pak_path} ===")
if not os.path.exists(pak_path):
    print("PAK FILE KHÔNG TỒN TẠI!")
else:
    print(f"PAK tồn tại, kích thước: {os.path.getsize(pak_path):,} bytes")
    
    # Đọc PAK header (RE Engine format)
    with open(pak_path, 'rb') as f:
        magic = f.read(4)
        print(f"Magic: {magic}")
        f.seek(0)
        data = f.read(min(1024, os.path.getsize(pak_path)))
    
    # Tìm file paths trong PAK (thường là null-terminated strings)
    # Tìm "natives" string
    text_data = data.decode('utf-8', errors='replace')
    if 'natives' in text_data:
        print("'natives' found in PAK header!")
    if 'ao_mes_main_sys_mainmenu' in text_data:
        print("'ao_mes_main_sys_mainmenu' found in first 1024 bytes!")
    else:
        # Check full file (search for strings)
        print("Scanning full PAK for file references...")
        with open(pak_path, 'rb') as f:
            pak_data = f.read()
        
        keywords = [
            b'ao_mes_main_sys_mainmenu',
            b'ch_mes_main_sys_mainmenu', 
            b'mc_mes_main_sys_mainmenu',
            b'dev1_term_menu',
            b'mes_develop_misc',
            b'ch_mes_develop',
        ]
        for kw in keywords:
            pos = pak_data.find(kw)
            if pos >= 0:
                print(f"  FOUND: {kw.decode()} at offset {pos}")
            else:
                print(f"  NOT FOUND: {kw.decode()}")

print()

# -------------------------------------------------------
# STEP 4B: Tìm file nào chứa "SEPARATE WAYS" cho main menu
# -------------------------------------------------------
print("=== STEP 4B: File nào hiển thị SEPARATE WAYS trên main menu? ===")
print()
print("Nhìn vào screenshot: Menu chính RE4 có:")
print("  - CỨU CHUYỆN CHÍNH  (đã dịch)")
print("  - SEPARATE WAYS     (CHƯA DỊCH)")
print("  - THE MERCENARIES   (CHƯA DỊCH)")
print("  - PHÚC LỢI          (đã dịch)")
print("  - TÙY CHỌN          (đã dịch)")
print()
print("Tìm file chứa cả 4 items này cùng nhau...")

# Tìm trong extracted_msg
for root, dirs, files in os.walk(EXTRACTED):
    for fname in files:
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                raw = f.read()
            # File phải có cả SEPARATE WAYS và MAIN STORY/CỨU CHUYỆN
            if 'SEPARATE WAYS' in raw and 'MAIN STORY' in raw:
                rel = os.path.relpath(fpath, EXTRACTED)
                print(f"\n  *** FOUND: {rel}")
                data = json.loads(raw)
                for i, entry in enumerate(data.get('entries', [])):
                    for slot_i, c in enumerate(entry.get('content', [])):
                        if c and any(kw in c.upper() for kw in ['SEPARATE WAYS', 'MAIN STORY', 'MERCENARIES', 'EXTRA', 'BONUS']):
                            print(f"    idx={i} slot={slot_i}: {c[:60]}")
        except:
            pass

print()

# -------------------------------------------------------  
# STEP 4C: Tìm file ch_mes_develop (thường là title card)
# -------------------------------------------------------
print("=== STEP 4C: mes_develop_misc ===")
dev_dir = os.path.join(EXTRACTED, r'natives\stm\_chainsaw\message\mes_develop_misc')
if os.path.exists(dev_dir):
    for fname in os.listdir(dev_dir):
        if fname.endswith('.json'):
            fpath = os.path.join(dev_dir, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"\n  File: {fname} ({len(data['entries'])} entries)")
            for i, entry in enumerate(data.get('entries', [])[:20]):
                c = entry.get('content', [''])[0] if entry.get('content') else ''
                if c and c.strip():
                    print(f"    idx={i}: {c[:80]}")
else:
    print(f"  NOT FOUND: {dev_dir}")
    
# Check _chainsaw/message/dlc
dlc_dir = os.path.join(EXTRACTED, r'natives\stm\_chainsaw\message\dlc')
if os.path.exists(dlc_dir):
    print(f"\n=== DLC dir contents ===")
    for root, dirs, files in os.walk(dlc_dir):
        for fname in files:
            if fname.endswith('.json'):
                fpath = os.path.join(root, fname)
                rel = os.path.relpath(fpath, EXTRACTED)
                with open(fpath, 'r', encoding='utf-8') as f:
                    raw = f.read()
                if 'SEPARATE' in raw or 'MERCENARIES' in raw:
                    print(f"  *** {rel}")
