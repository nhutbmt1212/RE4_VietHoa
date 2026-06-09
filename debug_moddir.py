"""
Simulate inject to check what ends up in MOD_DIR
and why only 152 files get there.
"""
import os
import json
import csv
import subprocess
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "vietnamese_translation.csv")
EXTRACTED_DIR = os.path.join(SCRIPT_DIR, "extracted_msg")
MOD_DIR = os.path.join(SCRIPT_DIR, "debug_mod_dir")

mode = "always-on"

# Clean
if os.path.exists(MOD_DIR):
    shutil.rmtree(MOD_DIR)

# Read CSV
translations_by_file = {}
with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        file_path = row["File Path"].replace("\\", "/").strip()
        if file_path.endswith(".json"):
            file_path = file_path[:-5]
        entry_idx_str = row["Entry Index"].strip()
        if not entry_idx_str:
            continue
        idx = int(entry_idx_str)
        viet = row["Vietnamese"].strip()
        if viet:
            if file_path not in translations_by_file:
                translations_by_file[file_path] = []
            translations_by_file[file_path].append((idx, viet))

print(f"Files to process: {len(translations_by_file)}")

# Only process first 10 files that SHOULD be in PAK but weren't
target_files = [
    "natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22",
    "natives/stm/_chainsaw/message/mes_main_conv/ch_mes_main_conv_cp11.msg.22",
    "natives/stm/_chainsaw/message/mes_main_cs/ch_mes_main_csa003.msg.22",
    "natives/stm/_chainsaw/message/mes_main_accessory/ch_mes_main_accessory.msg.22",
]

for file_path in target_files:
    edits = translations_by_file.get(file_path, [])
    if not edits:
        print(f"SKIP (no edits): {file_path}")
        continue
    
    original_msg = os.path.join(EXTRACTED_DIR, file_path)
    original_json = original_msg + ".json"

    if not os.path.exists(original_json) or not os.path.exists(original_msg):
        print(f"SKIP (missing): {file_path}")
        continue

    target_msg = os.path.join(MOD_DIR, file_path)
    target_json = target_msg + ".json"
    os.makedirs(os.path.dirname(target_msg), exist_ok=True)

    with open(original_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    for idx, viet_text in edits:
        if idx < len(data["entries"]):
            content = data["entries"][idx]["content"]
            for i in range(len(content)):
                if content[i].strip():
                    content[i] = viet_text

    with open(target_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    shutil.copy2(original_msg, target_msg)
    
    remsg_script = os.path.join(SCRIPT_DIR, "tools", "REMSG_Converter", "src", "main.py")
    cmd = ["python", remsg_script, "-i", target_msg, "-e", target_json, "-m", "json"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    
    new_msg = target_msg + ".new"
    
    print(f"\nFile: {os.path.basename(file_path)}")
    print(f"  returncode: {res.returncode}")
    print(f"  .new exists: {os.path.exists(new_msg)}")
    
    if os.path.exists(new_msg):
        new_size = os.path.getsize(new_msg)
        orig_size = os.path.getsize(original_msg)
        print(f"  .new size: {new_size} (orig: {orig_size})")
        
        # DO the rename
        os.remove(target_msg)
        os.remove(target_json)
        os.rename(new_msg, target_msg)
        print(f"  After rename - .msg exists: {os.path.exists(target_msg)}")
        print(f"  After rename - .new exists: {os.path.exists(new_msg)}")
    else:
        if res.stderr:
            print(f"  STDERR: {res.stderr[:200]}")

# Count final files in MOD_DIR
total = 0
for root, dirs, files in os.walk(MOD_DIR):
    for f in files:
        total += 1
        
print(f"\nTotal files in MOD_DIR after processing {len(target_files)} files: {total}")

# Cleanup
shutil.rmtree(MOD_DIR)
