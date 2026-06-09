import csv

csv_path = r'd:\RE4_VietHoa\vietnamese_translation.csv'
with open(csv_path, 'r', encoding='utf-8-sig') as f, open('check_csv_out.txt', 'w', encoding='utf-8') as out:
    reader = csv.DictReader(f)
    for row in reader:
        eng = row['English']
        if 'Crouch' in eng or 'Crude Charm' in eng or 'SEPARATE WAYS' in eng or 'Judgment is Nigh' in eng:
            out.write(f"File: {row['File Path']} | Index: {row['Entry Index']} | Eng: {eng} | Viet: {row['Vietnamese']}\n")
