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

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:7b"
CSV_PATH = "vietnamese_translation.csv"
BACKUP_DIR = "backup_original_lang"
SAVE_INTERVAL = 10  # Save CSV every 10 translations

SYSTEM_PROMPT = """You are a professional game translator. Translate the following Resident Evil 4 Remake (RE4) game text from English to Vietnamese.

Guidelines for pronouns and addressing (xưng hô) based on characters and context:
- Leon S. Kennedy: Male protagonist, special agent. Uses "tôi" with most adults. Calls Ashley "em" or "Ashley". Calls Hunnigan "Hunnigan" or "cô". Calls Luis "Luis". Calls Ada "Ada".
- Ashley Graham: Female, President's daughter. Calls Leon "anh" or "Leon", refers to herself as "em".
- Ingrid Hunnigan: Female support. Calls Leon "Leon", refers to herself as "tôi" / "tôi (phía Hunnigan)". Leon calls her "Hunnigan" or "cô".
- Luis Sera: Male researcher. Uses "tôi", calls Leon "Leon", "bạn tôi" (my friend), or "anh".
- Ada Wong: Female agent. Calls Leon "Leon", refers to herself as "tôi".
- Osmund Saddler: Main cult leader. Uses "ta" (religious/majestic), calls Leon/others "ngươi" or "kẻ ngoại đạo" (outsider/heretic).
- Jack Krauser: Former major, Leon's ex-commander. Calls Leon "chàng lính mới" (rookie), refers to himself as "ta" or "tôi".
- Merchant: The mysterious merchant. Calls Leon "khách hàng" (stranger) or "bạn" (mate), refers to himself as "ta" or "tôi".

STRICT RULES:
1. Keep all HTML/XML tags intact (e.g. <COLOR FF0000>...</COLOR>, <REF ...>, <scale ...>). Do NOT translate or modify terms inside tags.
2. Keep all format placeholders intact (e.g. %s, %d, {0}, {1}).
3. Keep escape sequences intact (e.g. \\n, \\t, \\", \\\\).
4. Do NOT translate specific proper nouns, weapon names, boss/enemy names, items, collectibles, or organization names that are iconic to the Resident Evil series, as translating them makes them hard to recognize. Keep them in English:
   - Weapons: SG-09 R, Punisher, Red9, Blacktail, Matilda, Sentinel Nine, W-870, Riot Shotgun, Striker, TMP, LE 5, Bolt Thrower, SR M1903, Stingray, CQ BR, Broken Butterfly, Killer7, Handcannon, Chicago Sweeper, Infinite Rocket Launcher, Combat Knife, Tactical Knife, Primal Knife.
   - Enemies, Bosses & Parasites: Ganado, Plaga, Las Plagas, Los Iluminados, Zealot, Soldier, Garrador, Regenerador, Iron Maiden, Novistador, Colmillo, El Gigante, Verdugo, Del Lago, Pesanta.
   - Items, Currencies & Collectibles: Spinel, Pesetas, Velvet Blue, Red Beryl, Alexandrite, Yellow Diamond, Emerald, Ruby, Sapphire, Blue Medallion, Clockwork Castellan. (General items like "Green Herb", "Red Herb", "Yellow Herb", "First Aid Spray", or keys like "Insignia Key" can be translated or kept as is, but try to keep specific names simple and clear, e.g., "First Aid Spray" -> "Bình xịt sơ cứu", "Green Herb" -> "Thảo dược xanh").
   - Character names: Leon, Ashley, Luis, Ada, Krauser, Saddler, Salazar, Hunnigan, Wesker.
5. If the text is a technical key, rejected code, or purely symbols (e.g. #Rejected#, <REF ...>), return it exactly as it is without translation.
6. Output ONLY the translated Vietnamese text. Do not write explanations, quotes, or notes.
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

def check_ollama_status():
    """Verify if Ollama is running and has the model loaded."""
    print(f"Checking Ollama connection on {OLLAMA_URL}...")
    # Simple check on localhost:11434
    try:
        req = urllib.request.Request(
            "http://localhost:11434/",
            method="GET"
        )
        with urllib.request.urlopen(req, timeout=3) as res:
            if res.status == 200:
                print("Ollama is running!")
                return True
    except Exception as e:
        print(f"[ERROR] Could not connect to Ollama. Please make sure Ollama is running on port 11434. Error: {e}")
        return False

def translate_text(english_text):
    """Call local Ollama to translate english_text into Vietnamese."""
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": english_text}
        ],
        "options": {
            "temperature": 0.1,  # Low temperature for highly deterministic translations
            "num_predict": 256   # Restrict token count to prevent runaways
        },
        "stream": False
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            vietnamese_text = res_data["message"]["content"].strip()
            
            # Clean up potential LLM prefix/suffix quotes if model hallucinated them
            if (vietnamese_text.startswith('"') and vietnamese_text.endswith('"') and 
                not (english_text.startswith('"') and english_text.endswith('"'))):
                vietnamese_text = vietnamese_text[1:-1].strip()
            if (vietnamese_text.startswith("'") and vietnamese_text.endswith("'") and 
                not (english_text.startswith("'") and english_text.endswith("'"))):
                vietnamese_text = vietnamese_text[1:-1].strip()
                
            return vietnamese_text
    except Exception as e:
        print(f"\n[ERROR] Failed to translate: {e}")
        return None

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
    
    # 2. Check Ollama
    if not check_ollama_status():
        print("Please start Ollama and make sure the model 'qwen2.5:7b' is pulled.")
        print("Run: ollama pull qwen2.5:7b")
        return

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
