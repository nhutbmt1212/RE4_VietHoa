import csv
import re
import sys

# Force stdout to UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

CSV_PATH = "vietnamese_translation.csv"
cjk_regex = re.compile(r'[\u4e00-\u9fff]')

print("Scanning translation CSV for potential errors...")
print("-" * 60)

cjk_count = 0
mixed_count = 0
empty_viet = 0
total_translated = 0

with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for idx, row in enumerate(reader):
        english = row.get("English", "")
        vietnamese = row.get("Vietnamese", "").strip()
        row_num = idx + 2
        
        if vietnamese:
            total_translated += 1
            
            # 1. Check for CJK characters
            if cjk_regex.search(vietnamese):
                cjk_count += 1
                print(f"Row {row_num}: Chinese characters found!")
                print(f"  EN: {english}")
                print(f"  VI: {vietnamese}")
                print("-" * 40)
                
            # 2. Check for weird English/Vietnamese mashups (e.g. "ĐóLooks", "KínhWindsor")
            words = vietnamese.split()
            for word in words:
                # If word has mixed English case like "ĐóLooks" or "KínhWindsor"
                # specifically checking for a combination of Vietnamese special chars + English letters
                if re.search(r'[ĂÂĐÊÔƠƯăâđêôơư][a-zA-Z]{3,}', word) or re.search(r'[a-zA-Z]{3,}[ĂÂĐÊÔƠƯăâđêôơư]', word):
                    mixed_count += 1
                    print(f"Row {row_num}: Mixed language word found in '{word}'!")
                    print(f"  EN: {english}")
                    print(f"  VI: {vietnamese}")
                    print("-" * 40)
                    break
        else:
            empty_viet += 1

print("Scan complete.")
print(f"Total entries: {idx + 2}")
print(f"Total translated: {total_translated}")
print(f"Chinese character errors: {cjk_count}")
print(f"Mixed language word errors: {mixed_count}")
