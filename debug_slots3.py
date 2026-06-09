"""
DEBUG STEP 3: Tìm hiểu tại sao SEPARATE WAYS, THE MERCENARIES, EXIT vẫn hiện tiếng Anh
Mặc dù trong CSV đã dịch NHƯNG trên màn hình vẫn thấy English

PHÁT HIỆN QUAN TRỌNG:
- ao_mes_main_sys_mainmenu idx=0 "SEPARATE WAYS":
  slot[0]=Japanese, slot[1]=English, ..., slot[8]=EMPTY (Dutch?), slot[9]=EMPTY
- Import script ghi đè TẤT CẢ slot != empty -> slot 8,9 KHÔNG được ghi

GIẢ THUYẾT: Game fallback xuống slot 1 (English) khi slot tiếng Việt (nếu có) là empty
Hoặc: Game RE4 không có Vietnamese language -> fallback sang English (slot 1)

Kiểm tra xem Vietnamese thuộc slot nào:
"""
import json, os, csv
import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

EXTRACTED = r'd:\RE4_VietHoa\extracted_msg'
CSV = r'd:\RE4_VietHoa\vietnamese_translation.csv'

# Xem cấu trúc đầy đủ của REMSG format
# Languages array: [0,1,2,...,32] - cần biết slot nào = gì
# Dựa vào EXIT entry:
# slot[0]='EXIT'(Jpn?), [1]='Quit', [2]='Quitter'(FR), [3]='Esci'(IT), [4]='Beenden'(DE)
# [5]='SALIR'(ES), [6]='Выйти'(RU), [7]='Wyjdź'(PL), [8-9]=empty, [10]='Sair'(PT)
# [11]=Korean, [12]=Trad.Chinese, [13]=Simp.Chinese, [21]=Arabic

LANG_NAMES = {
    0: "Japanese",
    1: "English",
    2: "French",
    3: "Italian",
    4: "German",
    5: "Spanish",
    6: "Russian",
    7: "Polish",
    8: "Dutch?/Czech?",
    9: "Unknown",
    10: "Portuguese-BR",
    11: "Korean",
    12: "Traditional Chinese",
    13: "Simplified Chinese",
    14: "Unknown14",
    15: "Unknown15",
    16: "Unknown16",
    17: "Unknown17",
    18: "Unknown18",
    19: "Unknown19",
    20: "Unknown20",
    21: "Arabic",
    22: "Unknown22",
    23: "Unknown23",
    24: "Unknown24",
    25: "Unknown25",
    26: "Unknown26",
    27: "Unknown27",
    28: "Unknown28",
    29: "Unknown29",
    30: "Unknown30",
    31: "Unknown31",
    32: "Latin-American Spanish",
}

print("=== PHÂN TÍCH: Slot nào được sử dụng trong bản mod? ===")
print()
print("Mapping slot -> Language (dựa theo EXIT entry):")
for i, name in LANG_NAMES.items():
    print(f"  slot[{i:2d}] = {name}")

print()
print("=== ĐIỂM MẤU CHỐT ===")
print("Game RE4 Remake KHÔNG có slot tiếng Việt riêng.")
print("Cách mod phổ biến: ghi tiếng Việt vào slot 1 (English)")
print("  hoặc vào một slot empty để game fallback sang.")
print()

# Kiểm tra: Import script hiện tại ghi vào slot nào cho SEPARATE WAYS?
# CSV: ao_mes_main_sys_mainmenu idx=0 "SEPARATE WAYS" -> "CÁCH LY"
# entry content: slot[0]='SEPARATE WAYS', slot[1]='SEPARATE WAYS', [2-7]=ngôn ngữ khác

p = os.path.join(EXTRACTED, r'natives\stm\_anotherorder\message\mes_main_sys\ao_mes_main_sys_mainmenu.msg.22.json')
with open(p, 'r', encoding='utf-8') as f:
    ao_menu = json.load(f)

entry = ao_menu['entries'][0]
print(f"ao_mes_main_sys_mainmenu idx=0 '{entry.get('name','')}' content:")
for i, slot in enumerate(entry['content']):
    mark = " <-- SẼ ĐƯỢC GHI ĐÈ" if slot and slot.strip() else " <-- EMPTY (BỎ QUA)"
    lang = LANG_NAMES.get(i, f"Unknown{i}")
    print(f"  slot[{i:2d}]({lang}): {repr(slot[:40]) if slot else '(empty)'}{mark}")

print()
print("=== VẤN ĐỀ PHÁT HIỆN ===")
print("Import script ghi đè TẤT CẢ slot != empty.")
print("Với ao_mes_main_sys_mainmenu idx=0 'SEPARATE WAYS':")
print("  slot[0]='SEPARATE WAYS' -> GHI: 'CÁCH LY'")
print("  slot[1]='SEPARATE WAYS' -> GHI: 'CÁCH LY'")
print("  slot[2]='UNE AUTRE VOIE' -> GHI: 'CÁCH LY'")
print("  ... tất cả ngôn ngữ đều bị ghi đè thành 'CÁCH LY'")
print()
print("Điều này ĐÚNG về lý thuyết.")
print("Vậy tại sao game vẫn hiện 'SEPARATE WAYS'?")
print()
print("=== KIỂM TRA PAK: File có nằm trong PAK patch không? ===")

# Kiểm tra xem pak_builder có bao gồm file ao_mes_main_sys_mainmenu không
# bằng cách xem trong vietnamese_translation.csv file đó có path đúng không
print()
with open(CSV, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    ao_rows = [row for row in reader if 'ao_mes_main_sys_mainmenu' in row.get('File Path','')]

print(f"ao_mes_main_sys_mainmenu trong CSV: {len(ao_rows)} entries")
for row in ao_rows[:5]:
    print(f"  File Path: {row['File Path']}")
    print(f"  Idx: {row['Entry Index']}, Orig: {row.get('English','')[:50]}")
    print(f"  Viet: {row.get('Vietnamese','')[:50]}")
    print()

# So sánh File Path trong CSV với đường dẫn thực tế trong extracted_msg
print("Đường dẫn thực trong extracted_msg:")
print(f"  natives\\stm\\_anotherorder\\message\\mes_main_sys\\ao_mes_main_sys_mainmenu.msg.22")
