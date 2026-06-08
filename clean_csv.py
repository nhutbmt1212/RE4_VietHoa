import csv
import re
import os
import sys

# Force stdout to UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

CSV_PATH = "vietnamese_translation.csv"
TEMP_PATH = "vietnamese_translation_clean.csv"

cjk_regex = re.compile(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]')

print("Cleaning bad translations in CSV...")
print("-" * 60)

cleaned_count = 0
total_rows = 0

rows = []
with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for idx, row in enumerate(reader):
        total_rows += 1
        english = row.get("English", "")
        vietnamese = row.get("Vietnamese", "").strip()
        row_num = idx + 2
        
        need_clean = False
        reason = ""
        
        if vietnamese:
            # 1. Contains Chinese/Japanese/Korean characters
            english_no_tags = re.sub(r"<[^>]+>", "", english)
            vietnamese_no_tags = re.sub(r"<[^>]+>", "", vietnamese)
            en_cjk = set(cjk_regex.findall(english_no_tags))
            vi_cjk = set(cjk_regex.findall(vietnamese_no_tags))
            if vi_cjk - en_cjk:
                need_clean = True
                reason = f"Contains CJK characters not in English: {vi_cjk - en_cjk}"
                
            # 2. Contains weird merged words like "ĐóLooks" or "KínhWindsor"
            elif "ĐóLooks" in vietnamese or "Looks" in vietnamese or "Windsor" in vietnamese:
                # English words stuck to Vietnamese or weird formatting
                # Let's inspect words
                words = vietnamese.split()
                for word in words:
                    if "Looks" in word and word != "Looks":
                        need_clean = True
                        reason = f"Mixed word: {word}"
                    if "Windsor" in word and word != "Windsor":
                        need_clean = True
                        reason = f"Mixed word: {word}"
                        
            # 3. Bad translation "Giấy phép" for "Glasses"
            elif "Giấy phép" in vietnamese and "Glasses" in english:
                need_clean = True
                reason = "Translated 'Glasses' as 'Giấy phép'"
                
        if need_clean:
            print(f"Row {row_num}: Cleaning translation ({reason})")
            print(f"  EN: {english}")
            print(f"  VI: {vietnamese} -> (RESET TO EMPTY)")
            print("-" * 40)
            row["Vietnamese"] = ""
            cleaned_count += 1
            
        rows.append(row)

# Save the cleaned CSV
with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("Clean complete.")
print(f"Total rows scanned: {total_rows}")
print(f"Total rows reset for re-translation: {cleaned_count}")
