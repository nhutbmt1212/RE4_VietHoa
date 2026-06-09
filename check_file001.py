"""Check translations for ch_mes_main_file_001"""
import csv

rows_001 = []
with open('vietnamese_translation.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        fp = row['File Path'].replace('\\', '/').strip()
        if fp.endswith('.json'):
            fp = fp[:-5]
        if 'ch_mes_main_file_001' in fp:
            rows_001.append(row)

print(f"Rows for ch_mes_main_file_001: {len(rows_001)}")
for r in rows_001[:10]:
    fp = r['File Path']
    viet = r.get('Vietnamese','').strip()[:50]
    print(f"  idx={r['Entry Index']} path={fp} | viet={viet}")
