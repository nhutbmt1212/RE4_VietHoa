import os
import sys
import json
import csv
import time
import subprocess
import shutil
import zipfile
import argparse

# Inject workspace path to import build_pak from pak_builder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from pak_builder import build_pak

CSV_PATH = os.path.join(SCRIPT_DIR, "vietnamese_translation.csv")
EXTRACTED_DIR = os.path.join(SCRIPT_DIR, "extracted_msg")
MOD_DIR = os.path.join(SCRIPT_DIR, "vietnamese_mod")
ZIP_OUTPUT_PATH = os.path.join(SCRIPT_DIR, "Resident_Evil_4_Vietnamese_Mod.zip")
STATUS_FILE = os.path.join(SCRIPT_DIR, "mod_status.json")

# Game directory configuration
GAME_DIR = r"d:\Games\Resident Evil 4"
PAK_OUTPUT = os.path.join(GAME_DIR, "re_chunk_000.pak.patch_006.pak")


def check_status():
    """Retrieve current mod installation status."""
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                status = json.load(f)
            if status.get("installed"):
                # Double-check if files are actually present
                target = status.get("target", "loose")
                if target == "loose":
                    installed_files = status.get("files", [])
                    if installed_files and any(os.path.exists(os.path.join(GAME_DIR, f)) for f in installed_files):
                        return "Installed", status.get("mode"), "loose"
                elif target == "pak":
                    if os.path.exists(PAK_OUTPUT):
                        return "Installed", status.get("mode"), "pak"
        except:
            pass

    # Fallback checks if status file is missing but files exist
    if os.path.exists(PAK_OUTPUT):
        return "Installed (Unknown Mode)", "unknown", "pak"
        
    # Check if some translation files exist in game natives/ directory
    sample_path = os.path.join(GAME_DIR, "natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22")
    if os.path.exists(sample_path):
        return "Installed (Unknown Mode)", "unknown", "loose"
        
    return "Not Installed", None, None


def get_status_summary():
    """Returns a readable status string."""
    status, mode, target = check_status()
    if status == "Installed":
        mode_str = "Dedicated Option Mode (Italian slot)" if mode == "option" else "Always-On Mode"
        target_str = "REFramework Loose Files" if target == "loose" else "PAK Patch"
        return f"\033[92mInstalled ({mode_str} via {target_str})\033[0m"
    elif status == "Installed (Unknown Mode)":
        target_str = "REFramework Loose Files" if target == "loose" else "PAK Patch"
        return f"\033[93mInstalled (Unknown Mode via {target_str})\033[0m"
    else:
        return "\033[90mNot Installed / Clean Game\033[0m"


def clean_empty_directories(path, base_dir):
    """Recursively delete empty directories up to base_dir."""
    if not os.path.isdir(path) or path == base_dir:
        return
    if not os.listdir(path):
        try:
            os.rmdir(path)
            clean_empty_directories(os.path.dirname(path), base_dir)
        except:
            pass


def restore_game():
    """Restore the game to the original state by removing the patch/loose files."""
    print("\n" + "=" * 50)
    print("RESTORE ACTION: Uninstalling Vietnamese Mod...")
    print("=" * 50)
    
    status, _, target = check_status()
    removed_files = 0
    
    # 1. Clean up loose files if status file exists
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                status_data = json.load(f)
            
            if status_data.get("target") == "loose":
                files_to_remove = status_data.get("files", [])
                print(f"Removing {len(files_to_remove)} loose file(s)...")
                for rel_path in files_to_remove:
                    full_path = os.path.join(GAME_DIR, rel_path)
                    if os.path.exists(full_path):
                        try:
                            os.remove(full_path)
                            removed_files += 1
                            # Clean up empty parent directories
                            clean_empty_directories(os.path.dirname(full_path), GAME_DIR)
                        except Exception as e:
                            print(f"  [ERROR] Failed to delete: {rel_path} - {e}")
        except Exception as e:
            print(f"[ERROR] Failed to parse status file for uninstallation: {e}")

    # 2. Hard check: scan the entire game natives/ folder and remove any .msg.22 loose files
    # This catches all loose files regardless of how they were installed
    game_natives = os.path.join(GAME_DIR, "natives")
    fallback_paths = []
    if os.path.exists(game_natives):
        for root, dirs, files in os.walk(game_natives):
            for fname in files:
                if fname.endswith(".msg.22"):
                    full = os.path.join(root, fname)
                    rel = os.path.relpath(full, GAME_DIR).replace("\\", "/")
                    fallback_paths.append(rel)
    for rel_path in fallback_paths:
        full_path = os.path.join(GAME_DIR, rel_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                removed_files += 1
                clean_empty_directories(os.path.dirname(full_path), GAME_DIR)
            except:
                pass

    # 3. Clean up PAK patch
    if os.path.exists(PAK_OUTPUT):
        try:
            os.remove(PAK_OUTPUT)
            print(f"[OK] Removed mod patch file: {os.path.basename(PAK_OUTPUT)}")
        except Exception as e:
            print(f"[ERROR] Failed to delete patch file: {e}")

    # Clean up status file
    if os.path.exists(STATUS_FILE):
        try:
            os.remove(STATUS_FILE)
        except:
            pass

    print(f"\n\033[92m[SUCCESS] Mod uninstalled. Removed {removed_files} loose files and/or PAK patch. Game restored!\033[0m")
    return True


def inject_mod(mode="option", target="loose"):
    """
    Compile translation CSV and inject into game directory.
    - mode: 'always-on' (overwrites all) or 'option' (overwrites Italian/index 3)
    - target: 'loose' (direct to natives/ folder) or 'pak' (build patch_006.pak)
    """
    print("\n" + "=" * 50)
    print(f"INJECT ACTION: Compiling & Installing ({mode.upper()} mode via {target.upper()})...")
    print("=" * 50)

    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] Translation CSV file not found at:\n        {CSV_PATH}")
        return False

    # First run restore to clean any existing installation of either type
    restore_game()

    # 1. Clean previous mod directory
    if os.path.exists(MOD_DIR):
        try:
            shutil.rmtree(MOD_DIR)
        except Exception as e:
            print(f"[ERROR] Failed to clean temp mod directory: {e}")
            return False

    # 2. Read CSV and group translations by normalized file path
    print("Reading translation CSV...")
    translations_by_file = {}
    total_translated = 0

    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            file_path = row["File Path"].replace("\\", "/").strip()
            if file_path.endswith(".json"):
                file_path = file_path[:-5]
                
            entry_idx_str = row["Entry Index"].strip()
            if not entry_idx_str:
                continue
            idx = int(entry_idx_str)
            viet = row["Vietnamese"].strip()

            if viet:
                if file_path not in translations_by_file:
                    translations_by_file[file_path] = []
                translations_by_file[file_path].append((idx, viet))
                total_translated += 1

    print(f"Loaded {total_translated} translations across {len(translations_by_file)} files.")
    
    # In 'option' mode, force core UI settings files to be processed
    if mode == "option":
        extra_files = [
            "natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22",
            "natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_common.msg.22"
        ]
        for ef in extra_files:
            if ef not in translations_by_file:
                translations_by_file[ef] = []

    # 3. Process and translate each file
    processed_count = 0
    compiled_count = 0
    copied_files = []
    
    print("\nProcessing and translating message files...")
    for file_path, edits in translations_by_file.items():
        original_msg = os.path.join(EXTRACTED_DIR, file_path)
        original_json = original_msg + ".json"

        if not os.path.exists(original_json) or not os.path.exists(original_msg):
            if edits:
                print(f"  [Warning] Original file not found, skipping: {file_path}")
            continue

        target_msg = os.path.join(MOD_DIR, file_path)
        target_json = target_msg + ".json"
        os.makedirs(os.path.dirname(target_msg), exist_ok=True)

        with open(original_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Apply translations based on mode
        for idx, viet_text in edits:
            if idx < len(data["entries"]):
                content = data["entries"][idx]["content"]
                if mode == "always-on":
                    for i in range(len(content)):
                        if content[i].strip():
                            content[i] = viet_text
                else:  # mode == "option"
                    if len(content) > 3:
                        content[3] = viet_text

        # Dedicated option menu customizations
        if mode == "option":
            # Rename "Italiano" to "Tiếng Việt" in all settings languages
            if file_path == "natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22":
                for entry in data["entries"]:
                    if entry["name"] == "Dev1_Term_Menu_Language_Italiano":
                        content = entry["content"]
                        for i in range(len(content)):
                            if content[i].strip() and content[i].strip() != "<END>":
                                content[i] = "Tiếng Việt"
                    elif entry["name"] == "Dev1_Term_Menu_Language_Display_Desc":
                        content = entry["content"]
                        if len(content) > 3:
                            content[3] = "Thay đổi ngôn ngữ hiển thị văn bản và menu."
            
            # Change developer option labels in common message files
            elif file_path == "natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_common.msg.22":
                for entry in data["entries"]:
                    if entry["name"] == "CH_Mes_Main_Sys_Common_Italian":
                        content = entry["content"]
                        if len(content) > 26:
                            content[26] = "Vietnamese [vi]"

        # Save JSON
        with open(target_json, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Copy original message file to target directory to run recompiler
        shutil.copy2(original_msg, target_msg)

        # Compile JSON back to binary .msg
        remsg_script = os.path.join(SCRIPT_DIR, "tools", "REMSG_Converter", "src", "main.py")
        cmd = ["python", remsg_script, "-i", target_msg, "-e", target_json, "-m", "json"]

        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if res.returncode != 0:
            print(f"  [ERROR] Compiling failed for {file_path}: {res.stderr}")
            continue

        new_msg = target_msg + ".new"
        # Retry check a few times in case of Windows file-lock (e.g., antivirus)
        for attempt in range(3):
            if os.path.exists(new_msg):
                break
            time.sleep(0.1)
        
        if os.path.exists(new_msg):
            try:
                os.remove(target_msg)
                os.remove(target_json)
                # Use shutil.copy2 + remove instead of os.rename to avoid file lock issues on Windows
                shutil.copy2(new_msg, target_msg)
                os.remove(new_msg)
                compiled_count += 1
            except Exception as e:
                print(f"  [ERROR] Failed to finalize compiled file {file_path}: {e}")
                continue
            
            # If target is loose, copy directly to game directory
            if target == "loose" and os.path.exists(GAME_DIR):
                game_dest_path = os.path.join(GAME_DIR, file_path)
                os.makedirs(os.path.dirname(game_dest_path), exist_ok=True)
                shutil.copy2(target_msg, game_dest_path)
                copied_files.append(file_path)
        else:
            print(f"  [ERROR] Compiled file (.new) not generated for {file_path}")
            if res.stderr:
                print(f"          Compiler stderr: {res.stderr[:200]}")

        processed_count += 1
        if processed_count % 50 == 0:
            print(f"  Processed {processed_count} files...")

    print(f"Successfully compiled {compiled_count}/{processed_count} message files.")
    if compiled_count == 0:
        print("[ERROR] No files were compiled. Installation aborted.")
        return False

    success = False
    
    # 4. Packaging or deployment finalized
    if target == "loose" and os.path.exists(GAME_DIR):
        print(f"\n[OK] Copied {len(copied_files)} loose file(s) into: {os.path.join(GAME_DIR, 'natives')}")
        print("\033[92m[SUCCESS] Installed via REFramework Loose Files! Mod active without Mod Manager.\033[0m")
        success = True
    elif target == "pak" and os.path.exists(GAME_DIR):
        # For PAK mode: also deploy dev1_term_* and mes_main_sys files as loose files so they
        # override the startup-locked PAK entries (REFramework loads loose files
        # after PAK, so these will always win regardless of language setting).
        LOOSE_OVERRIDE_PREFIXES = (
            "natives/stm/_chainsaw/message/dev1_term/",
            "natives/stm/_chainsaw/message/mes_main_sys/",
            "natives/stm/_anotherorder/message/mes_main_sys/",
            "natives/stm/_mercenaries/message/mes_main_sys/",
        )
        loose_override_count = 0
        for root, dirs, files in os.walk(MOD_DIR):
            for fname in files:
                full = os.path.join(root, fname)
                rel = os.path.relpath(full, MOD_DIR).replace("\\", "/")
                if any(rel.startswith(p) for p in LOOSE_OVERRIDE_PREFIXES):
                    game_dest = os.path.join(GAME_DIR, rel)
                    os.makedirs(os.path.dirname(game_dest), exist_ok=True)
                    shutil.copy2(full, game_dest)
                    copied_files.append(rel)
                    loose_override_count += 1
        if loose_override_count:
            print(f"[OK] Deployed {loose_override_count} dev1_term loose override file(s) to game directory.")

        print(f"\nBuilding PAK patch and installing to game directory:\n{PAK_OUTPUT}")
        try:
            build_pak(MOD_DIR, PAK_OUTPUT)
            print("\n\033[92m[SUCCESS] PAK patch installed successfully!\033[0m")
            success = True
        except Exception as e:
            print(f"[ERROR] Failed to build and install PAK patch: {e}")
    else:
        # Fallback to ZIP package creation
        print(f"\n[WARNING] Game directory not found or invalid deployment target.")
        print(f"Building ZIP archive for manual installation: {ZIP_OUTPUT_PATH}")
        try:
            with zipfile.ZipFile(ZIP_OUTPUT_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(MOD_DIR):
                    for file in files:
                        fp = os.path.join(root, file)
                        arcname = os.path.relpath(fp, MOD_DIR)
                        zipf.write(fp, arcname)
            print(f"\n\033[92m[SUCCESS] ZIP package saved successfully to:\n          {ZIP_OUTPUT_PATH}\033[0m")
            success = True
        except Exception as e:
            print(f"[ERROR] Failed to write ZIP: {e}")

    # Cleanup temp directory
    try:
        shutil.rmtree(MOD_DIR)
    except:
        pass

    # Save status
    if success:
        status_data = {
            "installed": True,
            "mode": mode,
            "target": target,
            "files": copied_files if (target == "loose" or copied_files) else [os.path.relpath(PAK_OUTPUT, GAME_DIR)]
        }
        try:
            with open(STATUS_FILE, "w") as f:
                json.dump(status_data, f, indent=2)
        except:
            pass
        return True
        
    return False


def run_interactive():
    """Main interactive text-based interface loop."""
    while True:
        status_str = get_status_summary()
        print("\n" + "=" * 60)
        print("          RESIDENT EVIL 4 REMAKE - VIETNAMESE MOD MANAGER")
        print("=" * 60)
        print(f" Current Status: {status_str}")
        print("-" * 60)
        print(" 1. Inject Mod (Dedicated Option - Italian Slot - Loose Files)")
        print("    - Replaces Italian display language settings with 'Tiếng Việt'.")
        print("    - Installs directly to natives/ folder (Uses REFramework).")
        print("    - DOES NOT require Fluffy Mod Manager.")
        print()
        print(" 2. Inject Mod (Always-On Mode - Loose Files)")
        print("    - Replaces ALL language texts with Vietnamese.")
        print("    - Installs directly to natives/ folder (Uses REFramework).")
        print("    - DOES NOT require Fluffy Mod Manager.")
        print()
        print(" 3. Inject Mod (PAK Patch mode)")
        print("    - Builds patch_006.pak in the game directory.")
        print("    - Uses Italian slot option menu (Dedicated Option).")
        print()
        print(" 4. Restore Game (Uninstall Mod)")
        print("    - Safely removes all translation loose files and PAK patches.")
        print()
        print(" 5. Exit")
        print("=" * 60)
        
        try:
            choice = input("Select an option (1-5): ").strip()
        except KeyboardInterrupt:
            print("\nExiting.")
            break
            
        if choice == "1":
            inject_mod(mode="option", target="loose")
        elif choice == "2":
            inject_mod(mode="always-on", target="loose")
        elif choice == "3":
            inject_mod(mode="option", target="pak")
        elif choice == "4":
            restore_game()
        elif choice == "5":
            print("Exiting. Goodbye!")
            break
        else:
            print("\033[91mInvalid choice. Please select 1, 2, 3, 4, or 5.\033[0m")
            
        input("\nPress Enter to return to menu...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resident Evil 4 Vietnamese Translation Mod Manager")
    parser.add_argument("--action", choices=["inject", "restore"], help="Action to perform")
    parser.add_argument("--mode", choices=["option", "always-on"], default="option", 
                        help="Injection mode (option = Italian slot, always-on = replace all)")
    parser.add_argument("--target", choices=["loose", "pak"], default="loose",
                        help="Installation target (loose = natives folder, pak = PAK patch)")
    args = parser.parse_args()

    if args.action == "inject":
        success = inject_mod(mode=args.mode, target=args.target)
        sys.exit(0 if success else 1)
    elif args.action == "restore":
        success = restore_game()
        sys.exit(0 if success else 1)
    else:
        run_interactive()
