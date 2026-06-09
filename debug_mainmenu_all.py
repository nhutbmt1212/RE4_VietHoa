import json, sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

p = r'd:\RE4_VietHoa\extracted_msg\natives\stm\_chainsaw\message\mes_main_sys\ch_mes_main_sys_mainmenu.msg.22.json'
with open(p, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total entries: {len(data['entries'])}")
print()

# Show ALL entries - look for SEPARATE WAYS, MERCENARIES, EXIT
for i, e in enumerate(data['entries']):
    name = e.get('name', '')
    slots = e.get('content', [])
    eng = slots[1] if len(slots) > 1 else ''
    jpn = slots[0] if len(slots) > 0 else ''

    # Print all with actual content
    if eng and not eng.startswith('#Rejected#') and not eng.startswith('<REF'):
        print(f"idx={i:3d} name={name}")
        print(f"  JPN={jpn[:60]}")
        print(f"  ENG={eng[:60]}")
        print()
    elif eng and eng.startswith('<REF'):
        print(f"idx={i:3d} <REF> -> {eng[:80]}")

print()
print("=== Tìm SEPARATE / MERCENARIES / EXIT ===")
for i, e in enumerate(data['entries']):75
    for si, c in enumerate(e.get('content', [])):
        if c and any(kw.lower() in c.lower() for kw in ['separate', 'mercenaries', 'exit', 'quit']):
            print(f"  idx={i} slot[{si}]: {c[:80]}")
