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
BACKUP_PATH = "vietnamese_translation.csv.bak"

cjk_regex = re.compile(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]')

def is_mashed_word(word, english_text):
    # Skip XML/HTML tags
    if word.startswith('<') and word.endswith('>'):
        return False
    # Skip brackets and HTML formatting leftovers
    word_clean = word.strip("[](){}\"',.?!;:*<>@®™")
    
    # If the word is already in the English text, it's not a translation error
    if word_clean.lower() in english_text.lower():
        return False
        
    # Technical identifiers/keys typically contain underscores (e.g. Dev1_Term...)
    if "_" in word_clean:
        return False
        
    # Exclude common camelCase proper nouns
    word_lower = word_clean.lower()
    allowed_terms = ["playstation", "directx", "steamvr", "microsd", "geforce", "raytracing", "quicktime", "fidelityfx"]
    for term in allowed_terms:
        if term in word_lower:
            return False
            
    # Check for lowercase followed directly by uppercase
    for i in range(1, len(word_clean)):
        if word_clean[i-1].islower() and word_clean[i].isupper():
            # Exclude specific safe acronym patterns if necessary, e.g., pH
            if word_clean[i-1:i+1] == "pH":
                continue
            return True
    return False

def extract_tags(text):
    # Extract HTML/XML tags
    tags = re.findall(r"<[^>]+>", text)
    # Normalize: strip internal spaces and uppercase the tag name
    normalized = []
    for t in tags:
        t_clean = re.sub(r'\s+', ' ', t).strip().upper()
        normalized.append(t_clean)
    return sorted(normalized)

def extract_placeholders(text):
    # Extract format specifiers like %s, %d, {0}, {1}
    placeholders = re.findall(r"%[0-9\.\-]*[a-zA-Z]|\{\d+\}", text)
    normalized = [p.strip().lower() for p in placeholders]
    return sorted(normalized)

def check_row_error(english, vietnamese):
    if not vietnamese:
        return None
        
    # 1. Check for CJK characters
    english_no_tags = re.sub(r"<[^>]+>", "", english)
    vietnamese_no_tags = re.sub(r"<[^>]+>", "", vietnamese)
    en_cjk = set(cjk_regex.findall(english_no_tags))
    vi_cjk = set(cjk_regex.findall(vietnamese_no_tags))
    new_cjk = vi_cjk - en_cjk
    if new_cjk:
        return f"Contains CJK characters not in English: {new_cjk}"
        
    # 2. Check for leaked JSON formatting
    if vietnamese.startswith('[') or vietnamese.startswith('{'):
        if '"id"' in vietnamese or '"translation"' in vietnamese or '"text"' in vietnamese:
            return "Leaked JSON format"
            
    # 3. Check for tag mismatches
    en_tags = extract_tags(english)
    vi_tags = extract_tags(vietnamese)
    if en_tags != vi_tags:
        return f"Tag mismatch (EN: {en_tags} vs VI: {vi_tags})"
        
    # 4. Check for placeholder mismatches
    en_placeholders = extract_placeholders(english)
    vi_placeholders = extract_placeholders(vietnamese)
    if en_placeholders != vi_placeholders:
        return f"Placeholder mismatch (EN: {en_placeholders} vs VI: {vi_placeholders})"
        
    # 5. Check for mashed words (camelCase/PascalCase)
    words = vietnamese.split()
    for word in words:
        if is_mashed_word(word, english):
            return f"Mashed word: '{word}'"
            
    # 6. Specific game term translation overrides (from original clean_csv.py)
    if "Giấy phép" in vietnamese and "Glasses" in english:
        return "Translated 'Glasses' as 'Giấy phép' (should be 'Kính')"
        
    return None

def main():
    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] CSV not found at {CSV_PATH}")
        return

    # Backup the original translation CSV
    if not os.path.exists(BACKUP_PATH):
        print(f"Creating backup of CSV at {BACKUP_PATH}...")
        import shutil
        shutil.copy2(CSV_PATH, BACKUP_PATH)

    print("Scanning CSV for translation errors...")
    print("-" * 70)

    rows = []
    cleaned_count = 0
    total_rows = 0

    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for idx, row in enumerate(reader):
            total_rows += 1
            english = row.get("English", "")
            vietnamese = row.get("Vietnamese", "")
            row_num = idx + 2
            
            error_reason = check_row_error(english, vietnamese)
            if error_reason:
                print(f"Row {row_num}: Error detected: {error_reason}")
                print(f"  EN: {repr(english)}")
                print(f"  VI: {repr(vietnamese)}")
                print(f"  -> Resetting to empty for re-translation.")
                print("-" * 50)
                row["Vietnamese"] = ""
                cleaned_count += 1
                
            rows.append(row)

    print(f"Scan complete. Reset {cleaned_count} rows out of {total_rows} total rows.")
    
    if cleaned_count > 0:
        print(f"Saving cleaned CSV to {CSV_PATH}...")
        with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print("Save complete!")
    else:
        print("No errors found. CSV remains unchanged.")

if __name__ == "__main__":
    main()
