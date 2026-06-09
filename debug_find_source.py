"""
Tìm ĐÚNG nguồn của SEPARATE WAYS, THE MERCENARIES, EXIT trên main menu
bằng cách dùng REFramework accessed_files log và tìm tất cả file có text đó
"""
import json, os, sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

EXTRACTED = r'd:\RE4_VietHoa\extracted_msg'

# Tìm 'Dev1_Term_Menu_MainMenu_QuitGame' trong dev1_term_menu
print("=== Dev1_Term_Menu_MainMenu_QuitGame trong dev1_term_menu ===")
p = os.path.join(EXTRACTED, r'natives\stm\_chainsaw\message\dev1_term\dev1_term_menu.msg.22.json')
with open(p, 'r', encoding='utf-8') as f:
    data = json.load(f)

for i, e in enumerate(data['entries']):
    name = e.get('name', '')
    if 'mainmenu' in name.lower() or 'quitgame' in name.lower():
        print(f"  idx={i} name={name}")
        for si, c in enumerate(e['content'][:6]):
            if c:
                print(f"    slot[{si}]={c[:60]}")
        print()

print()

# Tìm SEPARATE WAYS, THE MERCENARIES trong TẤT CẢ file JSON
print("=== Tìm 'SEPARATE WAYS' trong TẤT CẢ JSON files ===")
for root, dirs, files in os.walk(EXTRACTED):
    for fname in files:
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for i, e in enumerate(data.get('entries', [])):
                for si, c in enumerate(e.get('content', [])):
                    if c and 'SEPARATE WAYS' == c.strip():
                        rel = os.path.relpath(fpath, EXTRACTED)
                        print(f"  EXACT MATCH: {rel}")
                        print(f"    idx={i} slot[{si}] name={e.get('name','')}")
                        # Show all slots
                        for j, slot in enumerate(e['content'][:6]):
                            if slot:
                                print(f"      slot[{j}]={slot[:50]}")
                        print()
        except:
            pass

print()
print("=== Tìm 'THE MERCENARIES' trong TẤT CẢ JSON files ===")
for root, dirs, files in os.walk(EXTRACTED):
    for fname in files:
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for i, e in enumerate(data.get('entries', [])):
                for si, c in enumerate(e.get('content', [])):
                    if c and 'THE MERCENARIES' == c.strip():
                        rel = os.path.relpath(fpath, EXTRACTED)
                        print(f"  EXACT MATCH: {rel}")
                        print(f"    idx={i} slot[{si}] name={e.get('name','')}")
                        for j, slot in enumerate(e['content'][:6]):
                            if slot:
                                print(f"      slot[{j}]={slot[:50]}")
                        print()
        except:
            pass

print()
print("=== Tìm 'EXIT' (exact, as mode name) ===")
for root, dirs, files in os.walk(EXTRACTED):
    for fname in files:
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for i, e in enumerate(data.get('entries', [])):
                name = e.get('name', '')
                if 'mainmenu' in name.lower() and 'quit' in name.lower():
                    rel = os.path.relpath(fpath, EXTRACTED)
                    print(f"  {rel} idx={i} name={name}")
                    for j, slot in enumerate(e['content'][:6]):
                        if slot:
                            print(f"    slot[{j}]={slot[:50]}")
                    print()
        except:
            pass
