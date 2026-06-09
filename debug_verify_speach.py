"""
debug_verify_speach.py
Mô phỏng chính xác logic inject của mod_manager để kiểm tra
xem file speach có được ghi tiếng Việt vào đúng slot không.
"""
import json, os, csv, subprocess, shutil, time

SCRIPT_DIR = r"d:\RE4_VietHoa"
CSV_PATH = os.path.join(SCRIPT_DIR, "vietnamese_translation.csv")
EXTRACTED_DIR = os.path.join(SCRIPT_DIR, "extracted_msg")
REMSG = os.path.join(SCRIPT_DIR, "tools", "REMSG_Converter", "src", "main.py")

TEST_TARGETS = [
    # (file_path, mode) - test both option and always-on
    "natives/stm/_chainsaw/message/mes_main_speach/ch_mes_main_speach.msg.22",
    "natives/stm/_chainsaw/message/mes_main_conv/ch_mes_main_bino_cp13.msg.22",
    "natives/stm/_anotherorder/message/mes_main_speach/ao_mes_main_speach.msg.22",
]

# Load CSV translations
print("Loading CSV...")
translations_by_file = {}
with open(CSV_PATH, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        fp = row["File Path"].replace("\\", "/").strip()
        if fp.endswith(".json"):
            fp = fp[:-5]
        idx = int(row["Entry Index"].strip())
        viet = row["Vietnamese"].strip()
        if viet:
            if fp not in translations_by_file:
                translations_by_file[fp] = []
            translations_by_file[fp].append((idx, viet))

print(f"Loaded translations for {len(translations_by_file)} files")

tmpdir = os.path.join(SCRIPT_DIR, "_debug_tmp")
os.makedirs(tmpdir, exist_ok=True)

for file_path in TEST_TARGETS:
    print(f"\n{'='*60}")
    print(f"Testing: {file_path}")
    
    edits = translations_by_file.get(file_path, [])
    print(f"CSV entries: {len(edits)}")
    if edits:
        print(f"Sample: idx={edits[0][0]} -> {edits[0][1][:50]!r}")
    
    original_msg = os.path.join(EXTRACTED_DIR, file_path)
    original_json = original_msg + ".json"
    
    if not os.path.exists(original_json):
        print(f"JSON not found: {original_json}")
        continue
    
    # Test OPTION mode (slot [3])
    for mode in ["option", "always-on"]:
        print(f"\n  Mode: {mode}")
        
        with open(original_json, encoding="utf-8") as f:
            data = json.load(f)
        
        for idx, viet_text in edits[:5]:  # test first 5
            if idx < len(data["entries"]):
                content = data["entries"][idx]["content"]
                if mode == "always-on":
                    for i in range(len(content)):
                        if content[i].strip():
                            content[i] = viet_text
                else:  # option
                    if len(content) > 3:
                        content[3] = viet_text
        
        # Check result
        viet_in_slots = {}
        for entry in data["entries"]:
            for i, c in enumerate(entry["content"]):
                if c and any(0x1EA0 <= ord(ch) <= 0x1EF9 for ch in c):
                    viet_in_slots[i] = viet_in_slots.get(i, 0) + 1
        
        print(f"  Vietnamese text written to slots: {dict(list(viet_in_slots.items())[:5])}")
        
        if mode == "option":
            # Confirm slot 3 is being used
            s3_count = viet_in_slots.get(3, 0)
            print(f"  Slot [3] (Italian) has Vietnamese: {s3_count} entries")
            
            # Check if there are entries with content but Vietnamese NOT in slot 3
            problem_entries = 0
            for entry in data["entries"]:
                content = entry["content"]
                has_real = any(c.strip() and "#Rejected#" not in c for c in content[:7])
                slot3_is_viet = len(content) > 3 and any(0x1EA0 <= ord(ch) <= 0x1EF9 for ch in (content[3] or ""))
                if has_real and not slot3_is_viet:
                    problem_entries += 1
            
            print(f"  Entries with content but NO Vietnamese in slot[3]: {problem_entries}")
        
        break  # Only test option mode for now

# Check game's language setting
print("\n\n=== GAME CONFIGURATION ===")
game_dir = r"d:\Games\Resident Evil 4"
config_file = os.path.join(game_dir, "local_config.ini")
if os.path.exists(config_file):
    print(f"\nlocal_config.ini content:")
    with open(config_file, encoding='utf-8', errors='ignore') as f:
        content = f.read()
    # Show language-related settings
    for line in content.split('\n'):
        if any(kw in line.lower() for kw in ['lang', 'language', 'display', 'text', 'voic']):
            print(f"  {line.strip()}")
else:
    print("local_config.ini not found")

# Check if REFramework is present
refw = os.path.join(game_dir, "dinput8.dll")
refw2 = os.path.join(game_dir, "openxr_loader.dll")
print(f"\nREFramework (dinput8.dll): {'EXISTS' if os.path.exists(refw) else 'NOT FOUND'}")

# Check reframework folder
refw_dir = os.path.join(game_dir, "reframework")
if os.path.exists(refw_dir):
    print(f"reframework/ folder contents: {os.listdir(refw_dir)[:10]}")

shutil.rmtree(tmpdir, ignore_errors=True)
