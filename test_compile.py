"""Test compilation of dev1_term_menu.msg.22 with always-on mode"""
import json
import subprocess
import os
import shutil
import csv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACTED_DIR = os.path.join(SCRIPT_DIR, "extracted_msg")

file_path = "natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22"
original_msg = os.path.join(EXTRACTED_DIR, file_path)
original_json = original_msg + ".json"

# Load translations
translations = []
with open('vietnamese_translation.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        fp = row['File Path'].replace('\\', '/').strip()
        if fp.endswith('.json'):
            fp = fp[:-5]
        if fp == file_path:
            viet = row['Vietnamese'].strip()
            idx = int(row['Entry Index'].strip())
            if viet:
                translations.append((idx, viet))

print(f"Translations to apply: {len(translations)}")

# Load and modify JSON
with open(original_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

for idx, viet_text in translations:
    if idx < len(data['entries']):
        content = data['entries'][idx]['content']
        for i in range(len(content)):
            if content[i].strip():
                content[i] = viet_text

# Write to temp location
test_dir = os.path.join(SCRIPT_DIR, "test_compile_temp")
os.makedirs(test_dir, exist_ok=True)
test_msg = os.path.join(test_dir, "dev1_term_menu.msg.22")
test_json = test_msg + ".json"

shutil.copy2(original_msg, test_msg)
with open(test_json, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Run compiler
remsg_script = os.path.join(SCRIPT_DIR, "tools", "REMSG_Converter", "src", "main.py")
cmd = ["python", remsg_script, "-i", test_msg, "-e", test_json, "-m", "json"]

print(f"\nRunning: {' '.join(cmd)}")
res = subprocess.run(cmd, capture_output=True, text=True)
print(f"Return code: {res.returncode}")
if res.stdout:
    print(f"STDOUT:\n{res.stdout[:500]}")
if res.stderr:
    print(f"STDERR:\n{res.stderr[:500]}")

new_file = test_msg + ".new"
print(f"\n.new file exists: {os.path.exists(new_file)}")
if os.path.exists(new_file):
    print(f".new file size: {os.path.getsize(new_file)} bytes")

# Cleanup
shutil.rmtree(test_dir)
print("\nDone.")
