"""
debug_slots.py
Kiểm tra chi tiết slot ngôn ngữ của các loại file khác nhau
để xác định tại sao subtitle/conv không hiển thị tiếng Việt.
"""
import csv, os, json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "vietnamese_translation.csv")
EXTRACTED_DIR = os.path.join(SCRIPT_DIR, "extracted_msg")

# Đọc CSV để biết slot nào được ghi
print("=== CSV ENTRY INDEX CHECK ===")
slot_counts = {}
file_slots = {}

with open(CSV_PATH, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        fp = row["File Path"].replace("\\", "/").strip()
        if fp.endswith(".json"):
            fp = fp[:-5]
        viet = row["Vietnamese"].strip()
        entry_idx = row.get("Entry Index", "").strip()
        lang_idx = row.get("Language Index", row.get("Lang Index", row.get("Slot", ""))).strip()
        
        if viet and fp not in file_slots:
            file_slots[fp] = {"entry_idx": entry_idx, "lang_idx": lang_idx}

# Print CSV column names
with open(CSV_PATH, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    print("CSV Columns:", reader.fieldnames)
    # Show first 3 rows
    for i, row in enumerate(reader):
        if i >= 3:
            break
        print(f"Row {i}:", dict(row))

print()

# Kiểm tra một file menu (dev1_term) - đây là file nhận được
print("=== MENU FILE (dev1_term) ===")
menu_path = os.path.join(EXTRACTED_DIR, "natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22.json")
if os.path.exists(menu_path):
    with open(menu_path, encoding="utf-8") as f:
        data = json.load(f)
    entry = data["entries"][0]
    print(f"Entry: {entry['name']}")
    content = entry["content"]
    print(f"Slots ({len(content)}):")
    for i, c in enumerate(content[:10]):
        print(f"  [{i}]: {repr(c[:80]) if c else '(empty)'}")
else:
    print("NOT FOUND:", menu_path)

print()

# Kiểm tra file subtitle conv - file không nhận được
print("=== SUBTITLE FILE (mes_main_conv) ===")
# Lấy 1 file conv có content
conv_dir = os.path.join(EXTRACTED_DIR, "natives/stm/_chainsaw/message/mes_main_conv")
if os.path.exists(conv_dir):
    for fname in os.listdir(conv_dir):
        if fname.endswith(".json"):
            json_path = os.path.join(conv_dir, fname)
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
            # Tìm entry có content
            for entry in data["entries"]:
                has_content = any(c.strip() for c in entry["content"])
                if has_content:
                    print(f"File: {fname}")
                    print(f"Entry: {entry['name']}")
                    content = entry["content"]
                    print(f"Slots ({len(content)}):")
                    for i, c in enumerate(content):
                        if c.strip():
                            print(f"  [{i}]: {repr(c[:80])}")
                    break
            else:
                continue
            break
    else:
        print("No conv file with content found")

print()

# Kiểm tra file speach
print("=== SPEACH FILE ===")
speach_dir = os.path.join(EXTRACTED_DIR, "natives/stm/_chainsaw/message/mes_main_speach")
if os.path.exists(speach_dir):
    for fname in os.listdir(speach_dir):
        if fname.endswith(".json"):
            json_path = os.path.join(speach_dir, fname)
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
            for entry in data["entries"]:
                has_content = any(c.strip() for c in entry["content"])
                if has_content:
                    print(f"File: {fname}")
                    print(f"Entry: {entry['name']}")
                    content = entry["content"]
                    print(f"Slots ({len(content)}):")
                    for i, c in enumerate(content):
                        if c.strip():
                            print(f"  [{i}]: {repr(c[:80])}")
                    break
            else:
                continue
            break

print()

# Kiểm tra file tips/hints
print("=== TIPS FILE ===")
tips_dir = os.path.join(EXTRACTED_DIR, "natives/stm/_chainsaw/message/mes_main_tips")
if os.path.exists(tips_dir):
    for fname in os.listdir(tips_dir):
        if fname.endswith(".json"):
            json_path = os.path.join(tips_dir, fname)
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
            for entry in data["entries"]:
                has_content = any(c.strip() for c in entry["content"])
                if has_content:
                    print(f"File: {fname}")
                    print(f"Entry: {entry['name']}")
                    content = entry["content"]
                    print(f"Slots ({len(content)}):")
                    for i, c in enumerate(content):
                        if c.strip():
                            print(f"  [{i}]: {repr(c[:80])}")
                    break
            else:
                continue
            break

print()
print("=== CSV SAMPLE FOR EACH FILE TYPE ===")
types_shown = set()
with open(CSV_PATH, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        fp = row["File Path"].replace("\\", "/").strip()
        viet = row["Vietnamese"].strip()
        if not viet:
            continue
        # Extract folder type
        parts = fp.split("/")
        folder_type = parts[-2] if len(parts) >= 2 else "unknown"
        if folder_type not in types_shown:
            types_shown.add(folder_type)
            print(f"Type: {folder_type}")
            print(f"  File: {fp}")
            print(f"  Row data: {dict(row)}")
            print()
        if len(types_shown) >= 8:
            break
