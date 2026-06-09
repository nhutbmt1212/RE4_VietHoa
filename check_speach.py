"""Check if the subtitle text is in speach files"""
import json, os, csv

search_text = "cop inside me died"

EXTRACTED = 'extracted_msg'

# Check speach files
print("=== Checking mes_main_speach files ===")
for root, dirs, files in os.walk(EXTRACTED):
    for fname in files:
        if not fname.endswith('.json'):
            continue
        if 'speach' not in fname and 'speech' not in fname and 'soundsupport' not in fname:
            continue
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for i, entry in enumerate(data.get('entries', [])):
                for slot_idx, c in enumerate(entry.get('content', [])):
                    if c and search_text.lower() in c.lower():
                        rel = os.path.relpath(fpath, EXTRACTED).replace('\\', '/')
                        print(f"  File: {rel}")
                        print(f"  Entry idx={i} slot={slot_idx}")
                        print(f"  Text: {c[:100]}")
        except:
            pass

# Also check camdemo (cutscene demo)
print("\n=== Checking mes_main_camdemo files ===")
for root, dirs, files in os.walk(EXTRACTED):
    for fname in files:
        if not fname.endswith('.json'):
            continue
        if 'camdemo' not in fname:
            continue
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for i, entry in enumerate(data.get('entries', [])):
                for slot_idx, c in enumerate(entry.get('content', [])):
                    if c and search_text.lower() in c.lower():
                        rel = os.path.relpath(fpath, EXTRACTED).replace('\\', '/')
                        print(f"  File: {rel}")
                        print(f"  Entry idx={i} slot={slot_idx}")
                        print(f"  Text: {c[:100]}")
        except:
            pass

# Check soundsupport
print("\n=== Checking soundsupport files ===")
for root, dirs, files in os.walk(EXTRACTED):
    for fname in files:
        if not fname.endswith('.json'):
            continue
        if 'soundsupport' not in fname:
            continue
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for i, entry in enumerate(data.get('entries', [])):
                for slot_idx, c in enumerate(entry.get('content', [])):
                    if c and search_text.lower() in c.lower():
                        rel = os.path.relpath(fpath, EXTRACTED).replace('\\', '/')
                        print(f"  File: {rel}")
                        print(f"  Entry idx={i} slot={slot_idx}")  
                        print(f"  Text: {c[:100]}")
        except:
            pass

print("\nDone.")
