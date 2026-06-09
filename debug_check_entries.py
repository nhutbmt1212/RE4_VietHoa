"""
Kiểm tra:
1. ASSISTED/STANDARD/HARDCORE (ch_mes_main_sys_common idx=191-193) - trong CSV có không?
2. Subtitle 'See what's taking so long' (ch_mes_main_sys_purpose idx=3) - trong CSV có không?
3. Subtitle "C'mon, what's taking so long" (ch_mes_main_conv_cp51 idx=57) - trong CSV?
"""
import csv, os, sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

CSV = r'd:\RE4_VietHoa\vietnamese_translation.csv'

targets = [
    ('ch_mes_main_sys_common', 191),
    ('ch_mes_main_sys_common', 192),
    ('ch_mes_main_sys_common', 193),
    ('ch_mes_main_sys_purpose', 3),
    ('ch_mes_main_conv_cp51', 57),
]

print("=== Kiểm tra CSV cho các entry chưa dịch ===")
results = {t: None for t in targets}

with open(CSV, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        fname = os.path.basename(row['File Path'])
        idx = int(row['Entry Index'])
        for t_name, t_idx in targets:
            if t_name in fname and idx == t_idx:
                viet = row.get('Vietnamese', '').strip()
                orig = row.get('English', row.get('Original', '')).strip()
                results[(t_name, t_idx)] = (orig, viet, row['File Path'])

for (name, idx), val in results.items():
    if val is None:
        print(f"  [NOT IN CSV] {name} idx={idx}")
    else:
        orig, viet, fp = val
        status = 'OK' if viet else 'MISSING'
        print(f"  [{status}] {name} idx={idx}")
        print(f"    Orig: {orig[:60]}")
        print(f"    Viet: {viet[:60] if viet else '[EMPTY - CHƯA DỊCH]'}")
        print(f"    File: {fp}")
    print()

# Kiểm tra thêm: ch_mes_main_sys_mainmenu idx=70,71 (mô tả ASSISTED)
print("=== ch_mes_main_sys_mainmenu - ASSISTED description ===")
with open(CSV, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        fname = os.path.basename(row['File Path'])
        idx = int(row['Entry Index'])
        if 'ch_mes_main_sys_mainmenu' in fname and idx in [70, 71, 72, 73, 74, 75]:
            viet = row.get('Vietnamese', '').strip()
            orig = row.get('English', row.get('Original', '')).strip()
            status = 'OK' if viet else 'MISSING'
            print(f"  [{status}] idx={idx} orig={orig[:50]} viet={viet[:50] if viet else '[EMPTY]'}")
