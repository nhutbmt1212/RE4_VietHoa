import csv

with open('vietnamese_translation.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        en = row.get("English", "").strip()
        vi = row.get("Vietnamese", "").strip()
        if vi and len(en) > 20 and "#Rejected#" not in en:
            print(f"EN: {en}")
            print(f"VI: {vi}")
            print("---")
            count += 1
            if count >= 10:
                break
