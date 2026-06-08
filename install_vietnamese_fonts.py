import os
import sys
import urllib.request
import subprocess
import shutil
import zipfile

# Force stdout to UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CRYPTOR_EXE = os.path.join(SCRIPT_DIR, "tools", "REE.PAK.Tool", "REE.Fonts.Cryptor", "REE.Fonts.Cryptor.exe")
GAME_DIR = r"d:\Games\Resident Evil 4"
FONT_DEST_DIR = os.path.join(GAME_DIR, "natives", "stm", "_chainsaw", "ui", "ui0000", "font")

# Direct TTF URLs
FONT_URLS = {
    "Oswald-Bold.ttf": "https://raw.githubusercontent.com/bradfrost/atomic-design/master/fonts/Oswald-Bold.ttf",
    "RobotoCondensed-Bold.ttf": "https://raw.githubusercontent.com/hrbrmstr/hrbrthemes/master/inst/fonts/roboto-condensed/RobotoCondensed-Bold.ttf",
    "RobotoCondensed-Regular.ttf": "https://raw.githubusercontent.com/hrbrmstr/hrbrthemes/master/inst/fonts/roboto-condensed/RobotoCondensed-Regular.ttf"
}

# Mapping of TTF name to target RE4 font files
MAPPINGS = {
    "Oswald-Bold.ttf": [
        "cs_helveticaltpro-ultcomp.oft.1"  # Title screen font
    ],
    "RobotoCondensed-Bold.ttf": [
        "cs_helveticaneueltw1g-cn.oft.1",
        "cs_helveticaneueltw1g-mdcn.oft.1"
    ],
    "RobotoCondensed-Regular.ttf": [
        "cs_helveticaneueltw1g-roman.oft.1",
        "cs_neuehelveticapro-69cmmd.oft.1",
        "cs_dinnextw1g-regular.oft.1",
        "cs_dinnextslabpro-light.oft.1"
    ]
}


def download_file(url, dest):
    print(f"Downloading: {url} -> {dest}")
    # Add a custom User-Agent to avoid HTTP blocks
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    try:
        with urllib.request.urlopen(req) as response, open(dest, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to download: {e}")
        return False


def extract_font_from_zip(zip_path, font_filename, dest_path):
    """Search for the font_filename inside zip (case-insensitive) and extract it."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file in zip_ref.namelist():
                basename = os.path.basename(file)
                if basename.lower() == font_filename.lower():
                    print(f"Extracting {basename} from {os.path.basename(zip_path)}...")
                    with zip_ref.open(file) as source, open(dest_path, "wb") as target:
                        shutil.copyfileobj(source, target)
                    return True
    except Exception as e:
        print(f"[ERROR] Failed to read ZIP {zip_path}: {e}")
    return False


def main():
    print("=" * 60)
    print("      RE4 REMAKE - VIETNAMESE FONT MOD INSTALLER")
    print("=" * 60)

    if not os.path.exists(GAME_DIR):
        print(f"[ERROR] Game directory not found at: {GAME_DIR}")
        return

    if not os.path.exists(CRYPTOR_EXE):
        print(f"[ERROR] Cryptor executable not found at: {CRYPTOR_EXE}")
        print("Please compile it first.")
        return

    # Create destination font folder
    os.makedirs(FONT_DEST_DIR, exist_ok=True)

    temp_dir = os.path.join(SCRIPT_DIR, "tmp_fonts")
    os.makedirs(temp_dir, exist_ok=True)

    # 1. Download TTF files directly
    downloaded_ttfs = {}
    for name, url in FONT_URLS.items():
        dest_path = os.path.join(temp_dir, name)
        if download_file(url, dest_path):
            downloaded_ttfs[name] = dest_path

    if len(downloaded_ttfs) != len(FONT_URLS):
        print("[ERROR] Failed to download all TTF fonts. Aborting.")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return

    # 2. Encrypt and install fonts
    success_count = 0
    total_count = 0
    
    print("\nProcessing fonts...")
    for ttf_name, target_names in MAPPINGS.items():
        extracted_ttf_path = downloaded_ttfs[ttf_name]
        
        for target_name in target_names:
            total_count += 1
            temp_encrypted_path = os.path.join(temp_dir, target_name)
            
            # Run Cryptor to encrypt .ttf to .oft.1
            cmd = [CRYPTOR_EXE, extracted_ttf_path, temp_encrypted_path]
            res = subprocess.run(cmd, capture_output=True, text=True)
            
            if res.returncode == 0 and os.path.exists(temp_encrypted_path):
                # Copy to game natives/ directory
                game_dest_path = os.path.join(FONT_DEST_DIR, target_name)
                try:
                    shutil.copy2(temp_encrypted_path, game_dest_path)
                    print(f" -> Installed: {target_name}")
                    success_count += 1
                except Exception as e:
                    print(f" -> [ERROR] Failed copying {target_name} to game: {e}")
            else:
                print(f" -> [ERROR] Encryption failed for {target_name}: {res.stderr}")

    # Cleanup temp folder
    shutil.rmtree(temp_dir, ignore_errors=True)

    print("-" * 60)
    print(f"[DONE] Successfully encrypted and installed {success_count}/{total_count} font files.")
    print(f"Destination: {FONT_DEST_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
