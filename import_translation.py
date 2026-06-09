import os
import json
import csv
import subprocess
import shutil
import zipfile


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "vietnamese_translation.csv")
    extracted_dir = os.path.join(script_dir, "extracted_msg")
    mod_dir = os.path.join(script_dir, "vietnamese_mod")
    zip_output_path = os.path.join(script_dir, "Resident_Evil_4_Vietnamese_Mod.zip")

    # Game directory and PAK patch output
    game_dir = r"d:\Games\Resident Evil 4"
    pak_output = os.path.join(game_dir, "re_chunk_000.pak.patch_006.pak")

    if not os.path.exists(csv_path):
        print(f"Error: Translation CSV file not found at: {csv_path}")
        return

    # Clean up previous mod directory
    if os.path.exists(mod_dir):
        shutil.rmtree(mod_dir)

    # 1. Read CSV and group translations by file path
    print("Reading translation CSV...")
    translations_by_file = {}
    total_translated = 0

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            file_path = row["File Path"]
            idx = int(row["Entry Index"])
            viet = row["Vietnamese"].strip()

            if viet:
                if file_path not in translations_by_file:
                    translations_by_file[file_path] = []
                translations_by_file[file_path].append((idx, viet))
                total_translated += 1

    print(f"Loaded {total_translated} translations across {len(translations_by_file)} files.")
    if total_translated == 0:
        print("Warning: No Vietnamese translations found in CSV.")
        return

    # 2. Process each file
    processed_count = 0
    for file_path, edits in translations_by_file.items():
        original_msg = os.path.join(extracted_dir, file_path)
        original_json = original_msg + ".json"

        if not os.path.exists(original_json) or not os.path.exists(original_msg):
            print(f"Warning: Original files for {file_path} not found. Skipping.")
            continue

        target_msg = os.path.join(mod_dir, file_path)
        target_json = target_msg + ".json"
        os.makedirs(os.path.dirname(target_msg), exist_ok=True)

        with open(original_json, "r", encoding="utf-8-sig") as f:
            data = json.load(f)

        for idx, viet_text in edits:
            if idx < len(data["entries"]):
                content = data["entries"][idx]["content"]
                # Always overwrite slot 1 (English) so game picks it up even if
                # the English slot was empty. Also overwrite all other non-empty
                # slots so every language gets the Vietnamese text.
                for i in range(len(content)):
                    if content[i].strip() or i == 1:
                        content[i] = viet_text


        with open(target_json, "w", encoding="utf-8-sig") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        shutil.copy2(original_msg, target_msg)

        remsg_script = os.path.join(script_dir, "tools", "REMSG_Converter", "src", "main.py")
        cmd = ["python", remsg_script, "-i", target_msg, "-e", target_json, "-m", "json"]

        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error compiling {file_path}: {res.stderr}")
            continue

        new_msg = target_msg + ".new"
        if os.path.exists(new_msg):
            os.remove(target_msg)
            os.remove(target_json)
            os.rename(new_msg, target_msg)
        else:
            print(f"Error: Compiled .new file not generated for {file_path}")

        processed_count += 1
        if processed_count % 50 == 0:
            print(f"Compiled {processed_count}/{len(translations_by_file)} files...")

    print(f"Finished compiling {processed_count} files.")

    if processed_count == 0:
        print("No files compiled. Aborting.")
        return

    # 3. Build PAK patch_006 and deploy directly to game
    if os.path.exists(game_dir):
        pak_output = os.path.join(game_dir, "re_chunk_000.pak.patch_006.pak")
        print(f"Building PAK patch -> {pak_output}")
        pak_script = os.path.join(script_dir, "pak_builder.py")
        res = subprocess.run(
            ["python", pak_script, mod_dir, pak_output],
            capture_output=False,
            text=True
        )
        if res.returncode == 0:
            print("PAK patch installed to game successfully!")
            print(f"  -> {pak_output}")

            # 4. Deploy ALL loose files directly to game directory
            print("\nDeploying ALL translated loose files directly to game directory...")
            try:
                shutil.copytree(mod_dir, game_dir, dirs_exist_ok=True)
                print(f"Successfully copied all loose files to {game_dir}")
            except Exception as e:
                print(f"Error copying loose files: {e}")
        else:
            print("Error building PAK patch.")


    else:
        print(f"Game directory not found: {game_dir}")
        print("Building ZIP for manual install instead...")
        with zipfile.ZipFile(zip_output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(mod_dir):
                for file in files:
                    fp = os.path.join(root, file)
                    arcname = os.path.relpath(fp, mod_dir)
                    zipf.write(fp, arcname)
        print(f"ZIP saved to: {zip_output_path}")

    # Cleanup mod directory
    shutil.rmtree(mod_dir)


if __name__ == "__main__":
    main()
