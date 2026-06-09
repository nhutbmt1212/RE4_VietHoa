"""Fix CSV entries with invalid file paths (.edited, .new suffixes)"""
import csv
import os
import shutil

csv_path = 'vietnamese_translation.csv'
backup_path = csv_path + '.bak_paths'

# Read all rows
with open(csv_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

print(f"Total rows: {len(rows)}")

# Find rows with bad paths
bad_suffixes = ('.edited', '.new')
good_rows = []
bad_rows = []

for row in rows:
    fp = row['File Path'].strip()
    fp_norm = fp.replace('\\', '/').lower()
    # Check if the path (after stripping .json) has bad extension
    if fp_norm.endswith('.json'):
        fp_check = fp_norm[:-5]
    else:
        fp_check = fp_norm
    
    is_bad = any(fp_check.endswith(s) for s in bad_suffixes)
    if is_bad:
        bad_rows.append(row)
    else:
        good_rows.append(row)

print(f"Bad rows to remove: {len(bad_rows)}")
for r in bad_rows:
    print(f"  Path: {r['File Path']} | Viet: {r.get('Vietnamese','')[:30]}")

# Backup original
shutil.copy2(csv_path, backup_path)
print(f"\nBacked up to: {backup_path}")

# Write cleaned CSV
with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(good_rows)

print(f"Cleaned CSV written: {len(good_rows)} rows (removed {len(bad_rows)} bad rows)")
