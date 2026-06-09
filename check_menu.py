import csv

count = 0
files = set()
with open('vietnamese_translation.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        fp = row['File Path'].replace('\\', '/').strip()
        if 'dev1_term_menu' in fp:
            viet = row['Vietnamese'].strip()
            if viet:
                count += 1
            files.add(fp)

print(f'Files: {files}')
print(f'Translated entries: {count}')

# Also check for Start Game specific entries
print("\n--- Sample entries ---")
with open('vietnamese_translation.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        fp = row['File Path'].replace('\\', '/').strip()
        if 'dev1_term_menu' in fp:
            entry = row.get('Entry Name', row.get('Entry Index', ''))
            viet = row['Vietnamese'].strip()
            orig = row.get('English', row.get('Original', '')).strip()[:50]
            if 'start' in orig.lower() or 'new game' in orig.lower() or not viet:
                print(f"  idx={row['Entry Index']} | orig={orig[:40]} | viet={viet[:40] if viet else '[EMPTY]'}")
