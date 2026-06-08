"""
test_packaging.py
-----------------
Test the full pipeline by injecting sample Vietnamese translations into the
first few rows of the CSV, then running import_translation.py to package the mod.
After the test, the original empty CSV is restored.
"""

import csv
import shutil
import os
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "vietnamese_translation.csv")
CSV_BACKUP = os.path.join(SCRIPT_DIR, "vietnamese_translation.csv.bak")

# Sample translations for the first 5 entries (items / accessories)
SAMPLE_TRANSLATIONS = {
    0: "Kính (Chữ Nhật)",
    1: "Kính (Windsor)",
    2: "Kính (Tròn)",
    3: "Kính Mát (Windsor)",
    4: "Kính Mát (Oversized)",
}

def inject_translations():
    """Write sample translations into the first few rows of the CSV."""
    print("[1] Backing up original CSV...")
    shutil.copy2(CSV_PATH, CSV_BACKUP)

    rows = []
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for i, row in enumerate(reader):
            if i < len(SAMPLE_TRANSLATIONS):
                row["Vietnamese"] = list(SAMPLE_TRANSLATIONS.values())[i]
            rows.append(row)

    with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[1] Injected {len(SAMPLE_TRANSLATIONS)} sample translations.")


def run_import():
    """Run import_translation.py to compile and package the mod."""
    print("\n[2] Running import_translation.py...")
    result = subprocess.run(
        ["python", os.path.join(SCRIPT_DIR, "import_translation.py")],
        capture_output=False,  # print live output
        text=True,
    )
    return result.returncode


def restore_csv():
    """Restore the original empty CSV."""
    if os.path.exists(CSV_BACKUP):
        shutil.copy2(CSV_BACKUP, CSV_PATH)
        os.remove(CSV_BACKUP)
        print("\n[3] Original CSV restored (backup removed).")


def main():
    zip_path = os.path.join(SCRIPT_DIR, "Resident_Evil_4_Vietnamese_Mod.zip")

    inject_translations()
    rc = run_import()
    restore_csv()

    print("\n" + "=" * 60)
    if rc == 0 and os.path.exists(zip_path):
        size = os.path.getsize(zip_path)
        print(f"[OK] SUCCESS! Mod ZIP created: {zip_path}")
        print(f"   Size: {size:,} bytes")
        print()
        print("Để cài mod:")
        print("  1. Copy file ZIP vào thư mục Mods của Fluffy Mod Manager")
        print("     (thường là: Games\\RE4R\\Mods\\)")
        print("  2. Bật mod trong Fluffy Mod Manager.")
        print("  3. Chạy game, chọn ngôn ngữ English trong Options.")
    else:
        print("[FAIL] FAILED! Check errors above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
