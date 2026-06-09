"""
Compare anotherorder vs chainsaw speach files to understand the slot structure.
"""
import json, os

EXTRACTED = r'd:\RE4_VietHoa\extracted_msg'

dirs = {
    'anotherorder': os.path.join(EXTRACTED, 'natives', 'stm', '_anotherorder', 'message', 'mes_main_speach'),
    'chainsaw':     os.path.join(EXTRACTED, 'natives', 'stm', '_chainsaw',     'message', 'mes_main_speach'),
}

for label, path in dirs.items():
    print(f"--- {label} speach ---")
    if not os.path.exists(path):
        print("  NOT FOUND:", path)
        continue
    files = sorted(os.listdir(path))
    for fname in files[:3]:
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(path, fname)
        with open(fpath, encoding='utf-8') as f:
            d = json.load(f)
        if not d['entries']:
            continue
        # Find first entry with real content
        for entry in d['entries']:
            real = [(i, c) for i, c in enumerate(entry['content']) if c.strip() and '#Rejected#' not in c]
            if real:
                print(f"  {fname}: {len(d['entries'])} entries, {len(entry['content'])} slots")
                print(f"  First entry with real content: {entry['name']}")
                for i, c in real[:5]:
                    print(f"    [{i}]: {c[:60]!r}")
                break
        else:
            # No real content - show first entry anyway
            entry = d['entries'][0]
            print(f"  {fname}: ALL #Rejected#, {len(d['entries'])} entries, {len(entry['content'])} slots")
            print(f"  Sample: {entry['content'][0][:60]!r}")
    print()

# Check chainsaw conv files for real content
print("--- chainsaw mes_main_conv ---")
conv_path = os.path.join(EXTRACTED, 'natives', 'stm', '_chainsaw', 'message', 'mes_main_conv')
if os.path.exists(conv_path):
    files = sorted(os.listdir(conv_path))
    found_real = False
    for fname in files:
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(conv_path, fname)
        with open(fpath, encoding='utf-8') as f:
            d = json.load(f)
        for entry in d['entries']:
            real = [(i, c) for i, c in enumerate(entry['content']) if c.strip() and '#Rejected#' not in c]
            if real:
                print(f"  {fname}: has real content!")
                print(f"  Entry: {entry['name']}")
                for i, c in real[:5]:
                    print(f"    [{i}]: {c[:60]!r}")
                found_real = True
                break
        if found_real:
            break
    if not found_real:
        print("  All chainsaw conv files are #Rejected#")

# Check anotherorder conv for real content
print()
print("--- anotherorder mes_main_conv ---")
ao_conv_path = os.path.join(EXTRACTED, 'natives', 'stm', '_anotherorder', 'message', 'mes_main_conv')
if os.path.exists(ao_conv_path):
    files = sorted(os.listdir(ao_conv_path))
    found_real = False
    for fname in files[:3]:
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(ao_conv_path, fname)
        with open(fpath, encoding='utf-8') as f:
            d = json.load(f)
        for entry in d['entries']:
            real = [(i, c) for i, c in enumerate(entry['content']) if c.strip() and '#Rejected#' not in c]
            if real:
                print(f"  {fname}: has real content at slots {[i for i,_ in real[:5]]}")
                found_real = True
                break
        if found_real:
            break
