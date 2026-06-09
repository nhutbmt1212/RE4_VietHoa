"""Find any weird file paths in CSV"""
import csv

weird = []
with open('vietnamese_translation.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        fp = row['File Path'].strip()
        if '.edited' in fp or '.new' in fp or '.json.json' in fp:
            weird.append(fp)

weird = list(set(weird))
print(f"Weird paths in CSV: {len(weird)}")
for p in weird[:20]:
    print(f"  {p}")
