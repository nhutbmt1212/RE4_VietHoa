import os
import sys
import json
import subprocess
import shutil

# Force stdout to use UTF-8 to prevent encoding errors on Windows terminal
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACTED_DIR = os.path.join(SCRIPT_DIR, "extracted_msg")
MOD_DIR = os.path.join(SCRIPT_DIR, "tmp_title_mod")

GAME_DIR = r"d:\Games\Resident Evil 4"
PAK_OUTPUT = os.path.join(GAME_DIR, "re_chunk_000.pak.patch_006.pak")

# Target translation strings
START_GAME_VN = "BẮT ĐẦU CHƠI"
MAIN_STORY_VN = "PHẦN CHƠI CHÍNH"

# File configurations mapping files to target entries and their translations
CONFIG = {
    # 1. Start Game
    "natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22": {
        "entries": {
            "Dev1_Term_Menu_StartMenu_StartGame_01": START_GAME_VN
        }
    },
    "natives/stm/_mercenaries/message/mes_main_sys/mc_mes_main_sys_mainmenu.msg.22": {
        "entries": {
            "MC_Mes_Main_Sys_MainMenu_Start": START_GAME_VN
        }
    },
    # 2. Main Story
    "natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_mainmenu.msg.22": {
        "entries": {
            "CH_Mes_Main_Sys_MainMenu_Play": MAIN_STORY_VN
        }
    },
    "natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_bonus.msg.22": {
        "entries": {
            "CH_Mes_Main_Sys_Bonus_Record_Category03": MAIN_STORY_VN
        }
    }
}


def compile_files():
    """Compile all patched msg files into MOD_DIR. Returns list of compiled relative paths."""
    if os.path.exists(MOD_DIR):
        shutil.rmtree(MOD_DIR)

    compiled = []

    for file_rel_path, patch_info in CONFIG.items():
        original_msg = os.path.join(EXTRACTED_DIR, file_rel_path)
        original_json = original_msg + ".json"

        if not os.path.exists(original_json) or not os.path.exists(original_msg):
            print(f"[ERROR] Source files not found: {file_rel_path}")
            continue

        target_msg = os.path.join(MOD_DIR, file_rel_path)
        target_json = target_msg + ".json"
        os.makedirs(os.path.dirname(target_msg), exist_ok=True)

        with open(original_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        modified = False
        for entry in data["entries"]:
            if entry["name"] in patch_info["entries"]:
                vn_text = patch_info["entries"][entry["name"]]
                content = entry["content"]
                print(f"  Patching '{entry['name']}' -> '{vn_text}'")
                for i in range(len(content)):
                    if content[i].strip() and content[i].strip() != "<END>":
                        content[i] = vn_text
                modified = True

        if not modified:
            print(f"[WARNING] No entries matched in: {file_rel_path}")
            continue

        with open(target_json, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        shutil.copy2(original_msg, target_msg)

        remsg_script = os.path.join(SCRIPT_DIR, "tools", "REMSG_Converter", "src", "main.py")
        cmd = ["python", remsg_script, "-i", target_msg, "-e", target_json, "-m", "json"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[ERROR] Compile failed for {file_rel_path}:\n{res.stderr}")
            continue

        new_msg = target_msg + ".new"
        if os.path.exists(new_msg):
            os.remove(target_msg)
            os.remove(target_json)
            os.rename(new_msg, target_msg)
            compiled.append(file_rel_path)
            print(f"  [OK] Compiled: {os.path.basename(file_rel_path)}")
        else:
            print(f"[ERROR] No output file generated for: {file_rel_path}")

    return compiled


def main():
    print("=" * 60)
    print("   RE4 REMAKE - TITLE SCREEN PATCH (PAK mode)")
    print("=" * 60)

    if not os.path.exists(GAME_DIR):
        print(f"[ERROR] Game directory not found: {GAME_DIR}")
        return

    # Remove any existing patch_006 from a previous run of this script
    if os.path.exists(PAK_OUTPUT):
        os.remove(PAK_OUTPUT)
        print(f"[OK] Removed old patch file.")

    print("\nStep 1: Compiling patched message files...")
    compiled = compile_files()

    if not compiled:
        print("[ERROR] No files compiled. Aborting.")
        if os.path.exists(MOD_DIR):
            shutil.rmtree(MOD_DIR)
        return

    print(f"\nStep 2: Building PAK patch ({len(compiled)} files)...")
    sys.path.insert(0, SCRIPT_DIR)
    from pak_builder import build_pak

    try:
        build_pak(MOD_DIR, PAK_OUTPUT)
    except Exception as e:
        print(f"[ERROR] PAK build failed: {e}")
        if os.path.exists(MOD_DIR):
            shutil.rmtree(MOD_DIR)
        return

    if os.path.exists(MOD_DIR):
        shutil.rmtree(MOD_DIR)

    print("\n" + "=" * 60)
    print(f"[DONE] PAK patch deployed: {os.path.basename(PAK_OUTPUT)}")
    print(f"       Location: {PAK_OUTPUT}")
    print("       Restart the game to see the changes.")
    print("=" * 60)


if __name__ == "__main__":
    main()
