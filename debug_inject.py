"""
debug_inject.py
Kiểm tra xem file nào trong CSV có bản dịch nhưng không tìm thấy file gốc,
và xem file nào được inject đúng/sai.
"""
import csv, os, json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "vietnamese_translation.csv")
EXTRACTED_DIR = os.path.join(SCRIPT_DIR, "extracted_msg")

files_ok = 0
files_missing = 0
missing = []
seen = set()

with open(CSV_PATH, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        fp = row["File Path"].replace("\\", "/").strip()
        if fp.endswith(".json"):
            fp = fp[:-5]
        viet = row["Vietnamese"].strip()
        if not viet or fp in seen:
            continue
        seen.add(fp)

        msg_path = os.path.join(EXTRACTED_DIR, fp)
        json_path = msg_path + ".json"

        msg_ok = os.path.exists(msg_path)
        json_ok = os.path.exists(json_path)

        if msg_ok and json_ok:
            files_ok += 1
        else:
            files_missing += 1
            missing.append((fp, msg_ok, json_ok))

print(f"Files OK (both .msg and .json found): {files_ok}")
print(f"Files MISSING: {files_missing}")

if missing:
    print("\nMissing files (first 40):")
    for fp, mo, jo in missing[:40]:
        print(f"  msg={mo} json={jo} -> {fp}")

    # Check if they exist with backslash path (Windows path issue)
    print("\nChecking if backslash paths work:")
    fp2, mo2, jo2 = missing[0]
    bs_path = os.path.join(EXTRACTED_DIR, fp2.replace("/", "\\"))
    print(f"  Backslash path exists? {os.path.exists(bs_path)} -> {bs_path}")

# Also check how many entries are in mode=option (index 3)
print("\n--- MODE CHECK ---")
print("Checking a subtitle file (mes_main_conv) to see language slots:")
conv_files = [fp for fp in seen if "mes_main_conv" in fp and "chainsaw" in fp]
if conv_files:
    sample = conv_files[0]
    json_path = os.path.join(EXTRACTED_DIR, sample) + ".json"
    if os.path.exists(json_path):
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        if data["entries"]:
            entry = data["entries"][0]
            content = entry["content"]
            print(f"File: {sample}")
            print(f"Entry: {entry['name']}")
            print(f"Content slots ({len(content)}):")
            for i, c in enumerate(content):
                print(f"  [{i}]: {repr(c[:60]) if c else '(empty)'}")
else:
    print("No mes_main_conv files found in chainsaw")
