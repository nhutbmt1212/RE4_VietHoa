"""Check for any .edited files and .new files that might cause issues"""
import os

EXTRACTED_DIR = 'extracted_msg'

edited_files = []
new_files = []

for root, dirs, files in os.walk(EXTRACTED_DIR):
    for f in files:
        if f.endswith('.edited'):
            edited_files.append(os.path.join(root, f))
        if f.endswith('.new'):
            new_files.append(os.path.join(root, f))

print(f"=== .edited files in extracted_msg ===")
for f in edited_files:
    print(f"  {f}")
    
print(f"\n=== .new files in extracted_msg ===")
for f in new_files:
    print(f"  {f}")

print(f"\nTotal .edited: {len(edited_files)}")
print(f"Total .new: {len(new_files)}")
