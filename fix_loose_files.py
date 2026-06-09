"""
fix_loose_files.py
Rebuild và deploy các loose file mes_main_sys bị thiếu
để override PAK patch (loose file > PAK trong RE Engine load order).
"""
import os, csv, json, subprocess, shutil, time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "vietnamese_translation.csv")
EXTRACTED_DIR = os.path.join(SCRIPT_DIR, "extracted_msg")
GAME_DIR = r"d:\Games\Resident Evil 4"
REMSG = os.path.join(SCRIPT_DIR, "tools", "REMSG_Converter", "src", "main.py")
TMPDIR = os.path.join(SCRIPT_DIR, "_fix_tmp")

# Files currently deployed as loose that are NOT dev1_term (they came from old inject)
# We need to rebuild them with always-on mode and redeploy
TARGETS = [
    "natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_mainmenu.msg.22",
    "natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_bonus.msg.22",
]

print("Loading translations...")
translations_by_file = {}
with open(CSV_PATH, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        fp = row["File Path"].replace("\\", "/").strip()
        if fp.endswith(".json"): fp = fp[:-5]
        idx = int(row["Entry Index"].strip())
        viet = row["Vietnamese"].strip()
        if viet:
            if fp not in translations_by_file:
                translations_by_file[fp] = []
            translations_by_file[fp].append((idx, viet))

os.makedirs(TMPDIR, exist_ok=True)

for file_path in TARGETS:
    print(f"\nProcessing: {file_path}")
    edits = translations_by_file.get(file_path, [])
    print(f"  Translations: {len(edits)}")

    original_msg = os.path.join(EXTRACTED_DIR, file_path)
    original_json = original_msg + ".json"

    if not os.path.exists(original_json):
        print(f"  SKIP: JSON not found")
        continue

    with open(original_json, encoding="utf-8") as f:
        data = json.load(f)

    # Apply always-on: overwrite all slots with content
    applied = 0
    for idx, viet_text in edits:
        if idx < len(data["entries"]):
            content = data["entries"][idx]["content"]
            for i in range(len(content)):
                if content[i].strip():
                    content[i] = viet_text
            applied += 1

    print(f"  Applied {applied} translations (always-on mode)")

    # Save to tmp
    fname = os.path.basename(file_path)
    tmp_msg = os.path.join(TMPDIR, fname)
    tmp_json = tmp_msg + ".json"

    shutil.copy2(original_msg, tmp_msg)
    with open(tmp_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Compile
    cmd = ["python", REMSG, "-i", tmp_msg, "-e", tmp_json, "-m", "json"]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    new_msg = tmp_msg + ".new"
    for _ in range(3):
        if os.path.exists(new_msg): break
        time.sleep(0.1)

    if os.path.exists(new_msg):
        shutil.copy2(new_msg, tmp_msg)
        os.remove(new_msg)
        os.remove(tmp_json)

        # Deploy as loose file
        dest = os.path.join(GAME_DIR, file_path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(tmp_msg, dest)
        print(f"  Deployed to: {dest}")
    else:
        print(f"  ERROR: Compile failed - {res.stderr[:100]}")

shutil.rmtree(TMPDIR, ignore_errors=True)
print("\nDone!")
