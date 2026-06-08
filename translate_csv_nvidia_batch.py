import os
import csv
import json
import shutil
import urllib.request
import urllib.error
import sys
import re
import time

# Force stdout to UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# NVIDIA API Configuration
NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
# Default to DeepSeek v4 Flash on NVIDIA Build
MODEL_NAME = "deepseek-ai/deepseek-v4-flash" 
CSV_PATH = "vietnamese_translation.csv"
BACKUP_DIR = "backup_original_lang"

BATCH_SIZE = 15  # Translate 15 lines at once to see the dialogue flow and save RPM
SLEEP_BETWEEN_BATCHES = 2.0  # Safe delay to stay well under the 40 RPM limit

SYSTEM_PROMPT = """You are a professional game translator. Translate the following Resident Evil 4 Remake (RE4) dialogue lines from English to Vietnamese.

You will receive a JSON array of dialogue lines. Each line has an "id" (its row number) and "text" (the English text).
You MUST return a JSON array of the exact same size, containing objects with "id" and "translation" (the translated Vietnamese text).
Example Input:
[{"id": 120, "text": "That's where I need to go."}, {"id": 121, "text": "Stick to the high ground."}]
Example Output:
[{"id": 120, "translation": "Đó là nơi tôi cần đến."}, {"id": 121, "translation": "Hãy đi ở trên cao."}]

To ensure accurate character pronouns (xưng hô) and game vibe, read the lines sequentially as they represent continuous dialogue flow:
- Leon S. Kennedy: Male protagonist, special agent. Uses "tôi" with adults. Calls Ashley "em" or "Ashley". Calls Hunnigan "Hunnigan" or "cô". Calls Luis "Luis". Calls Ada "Ada".
- Ashley Graham: Female, President's daughter. Calls Leon "anh" or "Leon", refers to herself as "em".
- Ingrid Hunnigan: Female support. Calls Leon "Leon", refers to herself as "tôi". Leon calls her "Hunnigan" or "cô".
- Luis Sera: Male researcher. Uses "tôi", calls Leon "Leon", "bạn tôi" (my friend), or "anh".
- Ada Wong: Female agent. Calls Leon "Leon", refers to herself as "tôi".
- Osmund Saddler: Main cult leader. Uses "ta" (majestic), calls Leon/others "ngươi" or "kẻ ngoại đạo" (outsider/heretic).
- Jack Krauser: Former major. Calls Leon "chàng lính mới" (rookie), refers to himself as "ta" or "tôi".
- Merchant: Calls Leon "khách hàng" (stranger) or "bạn" (mate), refers to himself as "ta" or "tôi".

STRICT RULES:
1. Output MUST be ONLY a valid JSON array of objects, containing "id" and "translation". Do not wrap it in markdown code blocks like ```json ... ```, and do not write any meta-explanations, notes, or introductions.
2. Keep all HTML/XML tags intact (e.g. <COLOR FF0000>...</COLOR>, <REF ...>, <scale ...>). Do NOT translate terms inside tags.
3. CRITICAL: Every time you see a literal '\\n' (escape sequence for newline) in the English text, you MUST preserve it in the corresponding position in the Vietnamese translation. Do NOT drop it, do NOT omit it, and do NOT replace it with a space.
   Example:
   English: "Medicine that will help to suppress\\nthe progress of your...problem."
   Vietnamese: "Thuốc sẽ giúp ức chế\\nsự tiến triển của vấn đề...của bạn."
4. Keep other format placeholders (e.g. %s, %d, {0}, {1}) and escape sequences (e.g. \\t, \\", \\\\) intact and in their corresponding positions.
5. The translation must be 100% in Vietnamese. Under no circumstances should you output Chinese characters (like 琥珀, 教会), Japanese, or other foreign scripts.
6. Do NOT mash up English and Vietnamese words (e.g., do NOT output "ĐóLooks" or "KínhWindsor"). Keep words separated.
7. Do NOT translate specific proper nouns, weapon names, boss names, items, collectibles, or organizations iconic to Resident Evil:
   - Weapons: SG-09 R, Punisher, Red9, Blacktail, Matilda, Sentinel Nine, W-870, Riot Shotgun, Striker, TMP, LE 5, Bolt Thrower, SR M1903, Stingray, CQ BR, Broken Butterfly, Killer7, Handcannon, Chicago Sweeper, Infinite Rocket Launcher, Combat Knife, Tactical Knife, Primal Knife.
   - Enemies/Bosses: Ganado, Plaga, Las Plagas, Los Iluminados, Zealot, Soldier, Garrador, Regenerador, Iron Maiden, Novistador, Colmillo, El Gigante, Verdugo, Del Lago, Pesanta.
   - Items/Currencies/Collectibles: Spinel, Pesetas, Velvet Blue, Red Beryl, Alexandrite, Yellow Diamond, Emerald, Ruby, Sapphire, Blue Medallion, Clockwork Castellan. (General items like "Green Herb" -> "Thảo dược xanh", "First Aid Spray" -> "Bình xịt sơ cứu" are fine to translate).
   - Character names: Leon, Ashley, Luis, Ada, Krauser, Saddler, Salazar, Hunnigan, Wesker.
   - Exceptions to translate:
     * Translate "Amber" to "Hổ Phách" (do NOT output 琥珀).
     * Translate "Church" to "Nhà thờ" or "Thánh đường" (do NOT output 教会).
     * Translate "Glasses" to "Kính".
"""

def backup_original_files():
    """Backup original CSV and extracted_msg directory if backup doesn't exist yet."""
    if not os.path.exists(BACKUP_DIR):
        print(f"Creating backup directory: {BACKUP_DIR}")
        os.makedirs(BACKUP_DIR)
        if os.path.exists(CSV_PATH):
            shutil.copy2(CSV_PATH, os.path.join(BACKUP_DIR, CSV_PATH))
            print(f"Backed up {CSV_PATH} to {BACKUP_DIR}")
        extracted_dir = "extracted_msg"
        if os.path.exists(extracted_dir):
            shutil.copytree(extracted_dir, os.path.join(BACKUP_DIR, extracted_dir))
            print(f"Backed up {extracted_dir} folder to {BACKUP_DIR}")

def translate_batch(api_key, batch_data, max_retries=3):
    """Sends a batch of lines to NVIDIA API for translation.
    
    Returns a dictionary of {id: translation_text} or None if failed.
    """
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(batch_data, ensure_ascii=False)}
        ],
        "temperature": 1.0,
        "top_p": 0.95,
        "max_tokens": 16384,
        "chat_template_kwargs": {
            "thinking": True,
            "reasoning_effort": "high"
        },
        "stream": False
    }
    
    # Enable JSON mode or structured outputs if supported, but a strict prompt + low temp is very reliable
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        NVIDIA_API_URL,
        data=data,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
    )
    
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=180) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                raw_content = res_data["choices"][0]["message"]["content"].strip()
                
                # Strip potential markdown code blocks
                if raw_content.startswith("```"):
                    # Find first [ and last ]
                    start_idx = raw_content.find("[")
                    end_idx = raw_content.rfind("]")
                    if start_idx != -1 and end_idx != -1:
                        raw_content = raw_content[start_idx:end_idx+1]
                
                # Parse JSON array
                translations_list = json.loads(raw_content)
                result = {}
                for item in translations_list:
                    item_id = int(item["id"])
                    trans = item["translation"].strip()
                    result[item_id] = trans
                return result
        except Exception as e:
            print(f"\n[WARNING] Batch translation attempt {attempt} failed: {e}")
            if attempt < max_retries:
                time.sleep(2)
            else:
                return None

def translate_single_fallback(api_key, english_text):
    """Fallback row-by-row translation in case batch JSON parsing fails."""
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT + "\nOutput ONLY the raw translation, not JSON."},
            {"role": "user", "content": english_text}
        ],
        "temperature": 1.0,
        "top_p": 0.95,
        "max_tokens": 16384,
        "chat_template_kwargs": {
            "thinking": True,
            "reasoning_effort": "high"
        },
        "stream": False
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        NVIDIA_API_URL,
        data=data,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            vietnamese_text = res_data["choices"][0]["message"]["content"].strip()
            
            # Clean potential quotes
            if (vietnamese_text.startswith('"') and vietnamese_text.endswith('"') and 
                not (english_text.startswith('"') and english_text.endswith('"'))):
                vietnamese_text = vietnamese_text[1:-1].strip()
            return vietnamese_text
    except Exception as e:
        print(f"Fallback translation failed: {e}")
        return None

def should_skip(english_text):
    """Check if the text should be skipped from translation."""
    text_stripped = english_text.strip()
    if not text_stripped:
        return True
    if "#Rejected#" in english_text:
        return True
    if text_stripped.startswith("<REF ") and text_stripped.endswith(">"):
        return True
    if text_stripped == "<END>":
        return True
        
    text_no_tags = re.sub(r"<[^>]+>", "", text_stripped).strip()
    if not any(c.isalpha() for c in text_no_tags):
        return True
        
    return False

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Read API Key
    api_key = ""
    key_file = "nvidia_key.txt"
    if os.path.exists(key_file):
        with open(key_file, "r") as kf:
            api_key = kf.read().strip()
            
    if not api_key:
        api_key = os.getenv("NVIDIA_API_KEY", "")
        
    if not api_key:
        print("[ERROR] NVIDIA API key not found.")
        print(f"Please paste your API Key from build.nvidia.com into a file named '{key_file}' in this folder.")
        return

    print("============================================================")
    print(f"Translating via NVIDIA NIM Batch API (Model: {MODEL_NAME})")
    print("============================================================")
    
    backup_original_files()
    
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
    
    to_translate_indices = []
    for idx, row in enumerate(rows):
        viet = row.get("Vietnamese", "").strip()
        english = row.get("English", "")
        if not viet and not should_skip(english):
            to_translate_indices.append(idx)
            
    to_translate_count = len(to_translate_indices)
    print(f"Rows needing translation: {to_translate_count}")
    
    if to_translate_count == 0:
        print("All rows are already translated or skipped! Nothing to do.")
        return

    print(f"Running in BATCH Mode: {BATCH_SIZE} lines/request.")
    print("Press Ctrl+C at any time to save progress and exit.")
    print("-" * 60)
    
    translated_count = 0
    unsaved_changes = False
    
    # Group into batches
    batches = []
    current_batch = []
    for idx in to_translate_indices:
        current_batch.append(idx)
        if len(current_batch) == BATCH_SIZE:
            batches.append(current_batch)
            current_batch = []
    if current_batch:
        batches.append(current_batch)
        
    total_batches = len(batches)
    
    try:
        for b_idx, batch in enumerate(batches):
            print(f"Translating Batch [{b_idx+1}/{total_batches}] (Rows {batch[0]+1} to {batch[-1]+1})...")
            
            # Format inputs
            batch_inputs = []
            for idx in batch:
                batch_inputs.append({
                    "id": idx,  # Use index as unique ID
                    "text": rows[idx]["English"]
                })
            
            # Translate batch
            batch_results = translate_batch(api_key, batch_inputs)
            
            if batch_results is not None:
                # Update rows
                for idx in batch:
                    translated_text = batch_results.get(idx)
                    if translated_text:
                        rows[idx]["Vietnamese"] = translated_text
                        translated_count += 1
                        unsaved_changes = True
                        print(f"  Row {idx+1} | EN: {repr(rows[idx]['English'])}")
                        print(f"         | VI: {repr(translated_text)}")
                print("-" * 50)
            else:
                # Fallback to single row translation if batch fails
                print("[WARNING] Batch failed. Falling back to single line translations for this batch...")
                for idx in batch:
                    english = rows[idx]["English"]
                    print(f"  Fallback Row {idx+1} Translating: {repr(english)}...")
                    vietnamese = translate_single_fallback(api_key, english)
                    if vietnamese:
                        rows[idx]["Vietnamese"] = vietnamese
                        translated_count += 1
                        unsaved_changes = True
                        print(f"  -> Translated: {vietnamese}")
                    else:
                        print(f"  -> [ERROR] Failed.")
                    time.sleep(1)
                print("-" * 50)
                
            # Intermittent checkpoint saving
            if unsaved_changes:
                temp_csv = CSV_PATH + ".tmp"
                with open(temp_csv, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.DictWriter(f, fieldnames=["File Path", "Entry Name", "Entry Index", "English", "Vietnamese"])
                    writer.writeheader()
                    writer.writerows(rows)
                if os.path.exists(temp_csv):
                    os.replace(temp_csv, CSV_PATH)
                    unsaved_changes = False
                    print(f"** Checkpoint saved! Translated {translated_count} entries. **")
                    print("-" * 50)
            
            # Rate limit guard sleep
            time.sleep(SLEEP_BETWEEN_BATCHES)
            
    except KeyboardInterrupt:
        print("\n\nTranslation paused by user. Saving progress...")
    finally:
        if unsaved_changes:
            temp_csv = CSV_PATH + ".tmp"
            with open(temp_csv, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["File Path", "Entry Name", "Entry Index", "English", "Vietnamese"])
                writer.writeheader()
                writer.writerows(rows)
            if os.path.exists(temp_csv):
                os.replace(temp_csv, CSV_PATH)
                print("** Final progress saved! **")
        print(f"Session finished. Translated: {translated_count} new entries.")
        print("============================================================")

if __name__ == "__main__":
    main()
