import os
import csv
import json
import shutil
import urllib.request
import urllib.error
import sys

# Force stdout to UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# ── Provider selection ────────────────────────────────────────────────────────
# Set PROVIDER = "nvidia" to use NVIDIA NIM API (requires openai package)
# Set PROVIDER = "ollama" to use local Ollama
PROVIDER = "nvidia"

# Ollama settings
OLLAMA_BASE = "http://127.0.0.1:11434"
OLLAMA_URL  = f"{OLLAMA_BASE}/api/chat"
OLLAMA_MODEL = "gemma3:12b"   # auto-detected at startup if not available

# NVIDIA NIM settings
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_API_KEY  = "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"
NVIDIA_MODEL    = "meta/llama-3.3-70b-instruct"

# Active model name (set at startup based on PROVIDER)
MODEL_NAME  = NVIDIA_MODEL if PROVIDER == "nvidia" else OLLAMA_MODEL

CSV_PATH      = "vietnamese_translation.csv"
BACKUP_DIR    = "backup_original_lang"
SAVE_INTERVAL = 10  # Save CSV every 10 translations

SYSTEM_PROMPT = """You are a professional game translator. Translate the following Resident Evil 4 Remake (RE4) game text from English to Vietnamese.

Guidelines for pronouns and addressing (xưng hô) based on characters and context:
- Leon S. Kennedy: Male protagonist, special agent. Uses "tôi" with most adults. Calls Ashley "em" or "Ashley". Calls Hunnigan "Hunnigan" or "cô". Calls Luis "Luis". Calls Ada "Ada".
- Ashley Graham: Female, President's daughter. Calls Leon "anh" or "Leon", refers to herself as "em".
- Ingrid Hunnigan: Female support. Calls Leon "Leon", refers to herself as "tôi". Leon calls her "Hunnigan" or "cô".
- Luis Sera: Male researcher. Uses "tôi", calls Leon "Leon", "bạn tôi" (my friend), or "anh".
- Ada Wong: Female agent. Calls Leon "Leon", refers to herself as "tôi".
- Osmund Saddler: Main cult leader. Uses "ta" (religious/majestic), calls Leon/others "ngươi" or "kẻ ngoại đạo" (outsider/heretic).
- Jack Krauser: Former major, Leon's ex-commander. Calls Leon "chàng lính mới" (rookie), refers to himself as "ta" or "tôi".
- Merchant: The mysterious merchant. Calls Leon "khách hàng" (stranger) or "bạn" (mate), refers to himself as "ta" or "tôi".

STRICT RULES:
1. Keep all HTML/XML tags intact (e.g. <COLOR FF0000>...</COLOR>, <REF ...>, <scale ...>). Do NOT translate or modify terms inside tags.
2. Keep all format placeholders intact (e.g. %s, %d, {0}, {1}).
3. Keep escape sequences intact (e.g. \\n, \\t, \\", \\\\).
4. The translation must be 100% in Vietnamese using ONLY the Latin-based Vietnamese alphabet (chữ Quốc ngữ). Under no circumstances should you output Chinese characters, Japanese characters, or other non-Vietnamese scripts. Never mix Chinese characters inside Vietnamese words:
     - Do NOT use Chinese characters for words like "tác" (e.g., write "động tác", "hợp tác", "thao tác" using standard letters).
     - Do NOT use Chinese characters for words like "dụng" (e.g., write "sử dụng", "dùng" using standard letters).
     - Do NOT use Chinese characters for words like "chí mạng" (e.g., write "chí mạng", "chết người" using standard letters).
     - Do NOT use Chinese characters for words like "sự" (e.g., write "sự thực", "sự việc" using standard letters).
     - Do NOT use Chinese characters for words like "đương nhiên" (e.g., write "đương nhiên" using standard letters).
5. Do NOT write any meta-explanations, notes, translation justifications, or commentary about the translation. Output ONLY the raw translated text.
6. Do NOT mash up English and Vietnamese words (e.g., do NOT output things like "ĐóLooks" or "KínhWindsor"). Keep words separated by spaces.
7. Do NOT translate specific proper nouns, weapon names, boss/enemy names, items, collectibles, or organization names that are iconic to the Resident Evil series, as translating them makes them hard to recognize. Keep them in English:
   - Weapons: SG-09 R, Punisher, Red9, Blacktail, Matilda, Sentinel Nine, W-870, Riot Shotgun, Striker, TMP, LE 5, Bolt Thrower, SR M1903, Stingray, CQ BR, Broken Butterfly, Killer7, Handcannon, Chicago Sweeper, Infinite Rocket Launcher, Combat Knife, Tactical Knife, Primal Knife.
   - Enemies, Bosses & Parasites: Ganado, Plaga, Las Plagas, Los Iluminados, Zealot, Soldier, Garrador, Regenerador, Iron Maiden, Novistador, Colmillo, El Gigante, Verdugo, Del Lago, Pesanta.
   - Items, Currencies & Collectibles: Spinel, Pesetas, Velvet Blue, Red Beryl, Alexandrite, Yellow Diamond, Emerald, Ruby, Sapphire, Blue Medallion, Clockwork Castellan. (General items like "Green Herb", "Red Herb", "Yellow Herb", "First Aid Spray", or keys like "Insignia Key" can be translated or kept as is, but try to keep specific names simple and clear, e.g., "First Aid Spray" -> "Bình xịt sơ cứu", "Green Herb" -> "Thảo dược xanh").
   - Character names: Leon, Ashley, Luis, Ada, Krauser, Saddler, Salazar, Hunnigan, Wesker.
   - Exception for key terms that must be translated:
     * Translate "Amber" to "Hổ Phách" (do NOT output Chinese characters).
     * Translate "Church" to "Nhà thờ" or "Thánh đường" (do NOT output Chinese characters).
     * Translate "Glasses" to "Kính" (do NOT translate as "Giấy phép").
     * Translate "Movements" / "moves" (referring to behavior of characters/bosses) to "Lối di chuyển", "Các động tác", "Hành động", or "Các chiêu thức" (do NOT translate as "Phong trào").
     * Translate "Evade maneuvers" to "động tác né tránh" or "cú né tránh".
     * Translate "Thrust attacks" to "đòn tấn công đâm" or "cú đâm".
     * Translate "Sweeping spear attacks" to "đòn quét giáo".
     * Translate "Ray tracing" to "dò tia" (do NOT translate as "tia ánh xạ").
8. If the text is a technical key, rejected code, or purely symbols (e.g. #Rejected#, <REF ...>), return it exactly as it is without translation.
9. No Chinese characters/scripts. Output exclusively standard Vietnamese text using only Vietnamese letters, spaces, numbers, common English terms as allowed, and standard punctuation.
"""

def backup_original_files():
    """Backup original CSV and extracted_msg directory if backup doesn't exist yet."""
    if not os.path.exists(BACKUP_DIR):
        print(f"Creating backup directory: {BACKUP_DIR}")
        os.makedirs(BACKUP_DIR)
        
        # Backup CSV
        if os.path.exists(CSV_PATH):
            shutil.copy2(CSV_PATH, os.path.join(BACKUP_DIR, CSV_PATH))
            print(f"Backed up {CSV_PATH} to {BACKUP_DIR}")
            
        # Backup extracted_msg directory
        extracted_dir = "extracted_msg"
        if os.path.exists(extracted_dir):
            shutil.copytree(extracted_dir, os.path.join(BACKUP_DIR, extracted_dir))
            print(f"Backed up {extracted_dir} folder to {BACKUP_DIR}")
    else:
        print(f"Backup directory already exists at: {BACKUP_DIR}. Skipping backup to prevent overwriting with partially-translated files.")

import time

def _get(url, timeout=5):
    """Simple GET helper, returns parsed JSON or None."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


# ── NVIDIA provider ───────────────────────────────────────────────────────────

def check_nvidia_status():
    """Verify NVIDIA API key is valid and model is accessible. Returns model name or None."""
    global MODEL_NAME
    try:
        from openai import OpenAI
    except ImportError:
        print("[ERROR] 'openai' package not installed. Run: pip install openai")
        return None

    print(f"Checking NVIDIA NIM API ({NVIDIA_MODEL})...")
    try:
        client = OpenAI(base_url=NVIDIA_BASE_URL, api_key=NVIDIA_API_KEY)
        # Lightweight ping — 1 token
        client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=1,
            stream=False,
        )
        MODEL_NAME = NVIDIA_MODEL
        print(f"NVIDIA API OK. Using model: {MODEL_NAME}")
        return MODEL_NAME
    except Exception as e:
        print(f"[ERROR] NVIDIA API check failed: {e}")
        return None


def translate_text_nvidia(english_text, max_retries=3):
    """Translate via NVIDIA NIM using the openai SDK."""
    from openai import OpenAI
    client = OpenAI(base_url=NVIDIA_BASE_URL, api_key=NVIDIA_API_KEY)

    for attempt in range(1, max_retries + 1):
        try:
            completion = client.chat.completions.create(
                model=NVIDIA_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": english_text},
                ],
                temperature=0.3,
                top_p=0.95,
                max_tokens=512,
                stream=False,
            )
            result = completion.choices[0].message.content.strip()
            # Strip hallucinated wrapper quotes
            for q in ('"', "'"):
                if (result.startswith(q) and result.endswith(q)
                        and not (english_text.startswith(q) and english_text.endswith(q))):
                    result = result[1:-1].strip()
            return result
        except Exception as e:
            print(f"\n[WARNING] NVIDIA attempt {attempt}/{max_retries}: {e}")
            if attempt < max_retries:
                time.sleep(2)

    print(f"\n[ERROR] All NVIDIA attempts failed for: {repr(english_text)}")
    return None


# ── Ollama provider ───────────────────────────────────────────────────────────

def check_ollama_status():
    """Verify Ollama is running and pick a model to use. Returns model name or None."""
    global MODEL_NAME, OLLAMA_MODEL
    max_retries = 5
    retry_delay = 2

    for attempt in range(1, max_retries + 1):
        print(f"Checking Ollama at {OLLAMA_BASE} (attempt {attempt}/{max_retries})...")
        data = _get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        if data is not None:
            available = [m["name"] for m in data.get("models", [])]
            if not available:
                print("[ERROR] Ollama is running but no models are installed.")
                print("        Run: ollama pull gemma3:12b")
                return None

            print(f"Ollama is running. Available models: {available}")
            if OLLAMA_MODEL in available:
                print(f"Using model: {OLLAMA_MODEL}")
            else:
                OLLAMA_MODEL = available[0]
                print(f"[INFO] Configured model not found — using '{OLLAMA_MODEL}' instead.")
            MODEL_NAME = OLLAMA_MODEL
            return MODEL_NAME

        if attempt < max_retries:
            print(f"[WARNING] Connection failed. Retrying in {retry_delay}s...")
            time.sleep(retry_delay)

    print(f"[ERROR] Could not connect to Ollama after {max_retries} attempts.")
    print("        Make sure Ollama is running:  ollama serve")
    return None


def translate_text_ollama(english_text, max_retries=3):
    """Translate via local Ollama API."""
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": english_text},
        ],
        "options": {"temperature": 0.1, "num_predict": 512},
        "stream": False,
    }
    data = json.dumps(payload).encode("utf-8")

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(
                OLLAMA_URL,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                result = res_data["message"]["content"].strip()
                for q in ('"', "'"):
                    if (result.startswith(q) and result.endswith(q)
                            and not (english_text.startswith(q) and english_text.endswith(q))):
                        result = result[1:-1].strip()
                return result
        except urllib.error.URLError as e:
            print(f"\n[WARNING] Ollama attempt {attempt}/{max_retries}: {e}")
            if attempt < max_retries:
                time.sleep(2)
        except (KeyError, json.JSONDecodeError) as e:
            print(f"\n[ERROR] Unexpected Ollama response: {e}")
            return None

    print(f"\n[ERROR] All Ollama attempts failed for: {repr(english_text)}")
    return None


# ── Unified dispatcher ────────────────────────────────────────────────────────

def check_api_status():
    """Check whichever provider is selected. Returns model name or None."""
    if PROVIDER == "nvidia":
        return check_nvidia_status()
    return check_ollama_status()


def translate_text(english_text):
    """Translate using the active provider."""
    if PROVIDER == "nvidia":
        return translate_text_nvidia(english_text)
    return translate_text_ollama(english_text)

import re

def should_skip(english_text):
    """Check if the text should be skipped from translation."""
    text_stripped = english_text.strip()
    if not text_stripped:
        return True
    # Skip if it is rejected
    if "#Rejected#" in english_text:
        return True
    # Skip if it's just a raw reference
    if text_stripped.startswith("<REF ") and text_stripped.endswith(">"):
        return True
    # Skip if it is a system placeholder
    if text_stripped == "<END>":
        return True
        
    # Remove all HTML/XML tags (e.g., <COLOR FF0000>, </COLOR>) to check actual text
    text_no_tags = re.sub(r"<[^>]+>", "", text_stripped).strip()
    
    # Skip if the remaining text doesn't contain any alphabetical characters
    if not any(c.isalpha() for c in text_no_tags):
        return True
        
    return False

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("============================================================")
    # 1. Backup original files
    backup_original_files()
    
    # 2. Check API connection
    chosen_model = check_api_status()
    if not chosen_model:
        if PROVIDER == "nvidia":
            print("Check your NVIDIA API key and network connection.")
        else:
            print("Please start Ollama:  ollama serve")
        return

    print(f"Translating with model: {chosen_model}")

    # 3. Read CSV
    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] CSV file not found at: {CSV_PATH}")
        return
        
    print("Reading translation CSV...")
    rows = []
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            
    total_rows = len(rows)
    print(f"Total rows in CSV: {total_rows}")
    
    # Filter rows to translate
    to_translate_indices = []
    for idx, row in enumerate(rows):
        viet = row.get("Vietnamese", "").strip()
        english = row.get("English", "")
        
        # If Vietnamese translation is empty and we shouldn't skip it
        if not viet and not should_skip(english):
            to_translate_indices.append(idx)
            
    to_translate_count = len(to_translate_indices)
    print(f"Rows needing translation: {to_translate_count}")
    
    if to_translate_count == 0:
        print("All rows are already translated or skipped! Nothing to do.")
        return

    # 4. Translation Loop
    print(f"Starting translation using model: {MODEL_NAME}")
    print("Press Ctrl+C at any time to save progress and exit.")
    print("-" * 60)
    
    translated_count = 0
    unsaved_changes = False
    
    try:
        for i, idx in enumerate(to_translate_indices):
            row = rows[idx]
            english = row["English"]
            
            # Print current item progress
            progress_str = f"[{i+1}/{to_translate_count}] (Row {idx+1})"
            print(f"{progress_str} Translating: {repr(english)}", end="\r", flush=True)
            
            vietnamese = translate_text(english)
            
            if vietnamese is not None:
                # If translation is empty (hallucinated empty response), default back to english or skip
                if not vietnamese.strip():
                    vietnamese = english
                
                row["Vietnamese"] = vietnamese
                translated_count += 1
                unsaved_changes = True
                
                # Clear line and print result
                print(" " * 120, end="\r")
                print(f"{progress_str} Translated:")
                print(f"  EN: {english}")
                print(f"  VI: {vietnamese}")
                print("-" * 40)
            else:
                print(" " * 120, end="\r")
                print(f"{progress_str} [WARNING] Skipped row due to Ollama error.")
                print("-" * 40)
                
            # Intermittent checkpoint saving
            if translated_count > 0 and translated_count % SAVE_INTERVAL == 0 and unsaved_changes:
                # Write to temp and rename (safe write)
                temp_csv = CSV_PATH + ".tmp"
                with open(temp_csv, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.DictWriter(f, fieldnames=["File Path", "Entry Name", "Entry Index", "English", "Vietnamese"])
                    writer.writeheader()
                    writer.writerows(rows)
                
                if os.path.exists(temp_csv):
                    os.replace(temp_csv, CSV_PATH)
                    unsaved_changes = False
                    print(f"** Checkpoint saved! Translated {translated_count} entries. **")
                    print("-" * 40)
                    
    except KeyboardInterrupt:
        print("\n\nTranslation paused by user (Ctrl+C). Saving progress...")
        
    finally:
        # Final save if there are unsaved changes
        if unsaved_changes:
            temp_csv = CSV_PATH + ".tmp"
            with open(temp_csv, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["File Path", "Entry Name", "Entry Index", "English", "Vietnamese"])
                writer.writeheader()
                writer.writerows(rows)
            
            if os.path.exists(temp_csv):
                os.replace(temp_csv, CSV_PATH)
                print("** Final progress saved successfully! **")
        else:
            print("No unsaved changes to write.")
            
        print(f"Session finished. Translated: {translated_count} new entries.")
        print(f"CSV location: {os.path.abspath(CSV_PATH)}")
        print("============================================================")

if __name__ == "__main__":
    main()
