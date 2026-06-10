import os
import csv
import json
import shutil
import urllib.request
import time
import sys
import re

# Force stdout to UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# NVIDIA API Configuration
NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
# Sử dụng model Qwen 3 Next 80B (phiên bản mới nhất trên NIM, tối ưu cho Tiếng Việt)
MODEL_NAME = "qwen/qwen3-next-80b-a3b-instruct" 

CSV_PATH = "vietnamese_translation.csv"
BACKUP_DIR = "backup_original_lang"

BATCH_SIZE = 15  # Translate 15 lines at once to keep conversation context
SLEEP_BETWEEN_BATCHES = 3.0  # Slower to avoid rate limits since we don't care about time

SYSTEM_PROMPT = """You are a master translator for the survival horror game Resident Evil 4 Remake (RE4). Translate the given English dialogue to Vietnamese.

You will receive a JSON array of dialogue lines. Each line has an "id", "speaker_id", and "text".
You MUST return a JSON array of the exact same size, containing objects with "id" and "translation".
Example Input: [{"id": 120, "speaker_id": "cha000", "text": "That's where I need to go."}]
Example Output: [{"id": 120, "translation": "Đó là nơi tôi cần đến."}]

[STORY AND TONE]
Resident Evil 4 is a dark, gritty survival horror game. The tone is intense, desperate, but occasionally features action-movie "cheesy" one-liners from Leon. 
- Cult members (Saddler, Salazar, Mendez) speak with religious, archaic, majestic, and arrogant language.
- Krauser is a hardened military veteran, speaking harshly and combatively.

[SPEAKER IDS (CRITICAL FOR PRONOUNS)]
You will receive 'speaker_id' in the JSON input. Use it to determine who is talking and apply the correct pronouns:
- cha000: Leon S. Kennedy
- cha100: Ashley Graham
- cha200: Ada Wong
- cha300: Luis Sera
- cha600: Albert Wesker
- cha700: Merchant

[STRICT PRONOUN RULES (XƯNG HÔ)]
GLOBAL RULE: ABSOLUTELY DO NOT USE "Tớ", "Cậu", "Mình", "Bạn" (unless Merchant). These words are too childish/friendly for a horror game. Use "Tôi", "Ta", "Anh", "Cô", "Ngươi".
- cha000 (Leon S. Kennedy): Uses "tôi" with adults. Calls Ashley "em". Calls Hunnigan/Ada "cô". Calls Luis/Krauser "anh".
- cha100 (Ashley Graham): Calls Leon "anh", refers to herself as "em".
- cha200 (Ada Wong): Refers to herself as "tôi" (NEVER "tớ"). Calls Leon "Leon" or "anh". Professional/flirtatious tone.
- cha300 (Luis Sera): Uses "tôi", calls Leon "anh bạn" or "anh". Calls Ashley "Senorita" (cô nương).
- cha600 (Albert Wesker): Refers to himself as "ta" or "tôi". Arrogant, authoritative.
- cha700 (Merchant): Calls Leon "khách hàng" or "bạn", refers to himself as "ta" or "tôi".
- Saddler/Salazar/Mendez: Uses "ta", calls Leon "ngươi" or "kẻ ngoại đạo".
- Krauser: Uses "ta" or "tôi", calls Leon "tân binh" (rookie) or "nhóc".

[TRANSLATION QUALITY & STYLE RULES (CRITICAL)]
1. DO NOT TRANSLATE WORD-FOR-WORD (Literal translation). You must adapt English idioms, slang, and phrasal verbs into natural, colloquial Vietnamese that real gamers use.
2. Example of BAD literal translation: "Stick to the high ground" -> "Dính vào vùng cao", "Things are heating up" -> "Mọi thứ đang trở nên nóng lên", "Fly, my pretty" -> "Bay, cô đẹp của tôi".
3. Example of GOOD natural translation: "Stick to the high ground" -> "Hãy giữ vị trí trên cao", "Things are heating up" -> "Tình hình đang căng thẳng đây", "Fly, my pretty" -> "Bay đi, cục cưng của ta".
4. Use context. "This could use some cleaning" should be "Chỗ này cần dọn dẹp" (not "Điều này"). "Did Luis do this?" should be "Luis làm trò này sao?" (not "Luis có làm điều này không?").
5. The language should be gritty, mature, and cinematic. Don't sound like a machine or Google Translate.
6. Fix Countess: "Nữ Bá tước". Fix Earring: "Khuyên tai" or "Bông tai".

[STRICT FORMATTING RULES]
1. Output MUST be ONLY a valid JSON array of objects. Do not wrap in markdown ```json. No explanations.
2. Keep all HTML/XML tags intact (e.g. <COLOR FF0000>...</COLOR>, <REF ...>, <scale ...>).
3. CRITICAL: Preserve every literal '\\n' exactly where it appears in the English text. Do NOT replace with space.
4. Keep all format placeholders (%s, %d, {0}) and escapes (\\t, \\") intact.
5. 100% Vietnamese standard letters (chữ Quốc ngữ). No Chinese/Japanese characters. 
6. DO NOT translate iconic names: 
   - Weapons: SG-09 R, Punisher, Red9, Blacktail, Matilda, Sentinel Nine, W-870, Riot Shotgun, Striker, TMP, LE 5, Bolt Thrower, SR M1903, Stingray, CQ BR, Broken Butterfly, Killer7, Handcannon, Chicago Sweeper, Infinite Rocket Launcher, Combat Knife, Tactical Knife, Primal Knife.
   - Enemies: Ganado, Plaga, Las Plagas, Los Iluminados, Zealot, Soldier, Garrador, Regenerador, Iron Maiden, Novistador, Colmillo, El Gigante, Verdugo, Del Lago, Pesanta.
   - Items: Spinel, Pesetas, Velvet Blue, Red Beryl, Alexandrite, Yellow Diamond, Emerald, Ruby, Sapphire, Blue Medallion, Clockwork Castellan. (General items like "Green Herb" -> "Thảo dược xanh" are fine).
   - Characters: Leon, Ashley, Luis, Ada, Krauser, Saddler, Salazar, Mendez, Hunnigan, Wesker, Mike.
7. Exceptions to translate:
   - "Amber" -> "Hổ Phách"
   - "Church" -> "Nhà thờ"
   - "Glasses" -> "Kính"
   - "Movements" / "moves" -> "Lối di chuyển", "Các động tác"
   - "Evade maneuvers" -> "động tác né tránh"
   - "Ray tracing" -> "dò tia"
8. If the text is purely symbols, keys, or "#Rejected#", return it exactly as is.
"""

def translate_batch(api_key, batch_data, max_retries=5):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(batch_data, ensure_ascii=False)}
        ],
        "temperature": 0.3,
        "top_p": 0.9,
        "max_tokens": 4096,
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
    
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                raw_content = res_data["choices"][0]["message"]["content"].strip()
                
                if raw_content.startswith("```"):
                    start_idx = raw_content.find("[")
                    end_idx = raw_content.rfind("]")
                    if start_idx != -1 and end_idx != -1:
                        raw_content = raw_content[start_idx:end_idx+1]
                
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
                time.sleep(3)
            else:
                return None

SINGLE_SYSTEM_PROMPT = SYSTEM_PROMPT + "\nYou are now translating a single line. Return ONLY the translated Vietnamese text, no JSON."

def translate_single(api_key, english_text, max_retries=4):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SINGLE_SYSTEM_PROMPT},
            {"role": "user", "content": english_text}
        ],
        "temperature": 0.3,
        "max_tokens": 2048,
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
    
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                vietnamese_text = res_data["choices"][0]["message"]["content"].strip()
                if vietnamese_text.startswith('"') and vietnamese_text.endswith('"') and not english_text.startswith('"'):
                    vietnamese_text = vietnamese_text[1:-1].strip()
                return vietnamese_text
        except Exception as e:
            print(f"\n[WARNING] Single translation attempt {attempt} failed: {e}")
            if attempt < max_retries:
                time.sleep(3)
            else:
                return None

def should_skip(english_text):
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
    
    api_key = ""
    key_file = "nvidia_key.txt"
    if os.path.exists(key_file):
        with open(key_file, "r") as kf:
            api_key = kf.read().strip()
            
    if not api_key:
        api_key = os.getenv("NVIDIA_API_KEY", "")
        
    if not api_key:
        print("[ERROR] NVIDIA API key not found in nvidia_key.txt.")
        return

    print("============================================================")
    print("      RE4 VIET HOA - ADVANCED TRANSLATION PIPELINE          ")
    print(f"      Model: {MODEL_NAME}                                  ")
    print("============================================================")
    
    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] {CSV_PATH} not found!")
        return
        
    print("Reading translation CSV and clearing old translations...")
    rows = []
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Force wipe existing translation so it re-translates everything
            row["Vietnamese"] = ""
            rows.append(row)
            
    total_rows = len(rows)
    print(f"Total rows in CSV: {total_rows}")
    
    to_translate_indices = []
    for idx, row in enumerate(rows):
        english = row.get("English", "")
        if not should_skip(english):
            to_translate_indices.append(idx)
            
    to_translate_count = len(to_translate_indices)
    
    if to_translate_count == 0:
        print("All rows skipped! Nothing to do.")
        return

    long_row_indices = []
    normal_row_indices = []
    for idx in to_translate_indices:
        if len(rows[idx]["English"]) > 600:
            long_row_indices.append(idx)
        else:
            normal_row_indices.append(idx)

    print(f"Rows needing translation: {to_translate_count} (Normal: {len(normal_row_indices)}, Long: {len(long_row_indices)})")
    print("Press Ctrl+C at any time to save progress and exit.")
    print("-" * 60)
    
    translated_count = 0
    unsaved_changes = False
    
    batches = []
    current_batch = []
    for idx in normal_row_indices:
        current_batch.append(idx)
        if len(current_batch) == BATCH_SIZE:
            batches.append(current_batch)
            current_batch = []
    if current_batch:
        batches.append(current_batch)
        
    total_batches = len(batches)
    
    try:
        if total_batches > 0:
            print(f"--- Starting Batch Translation ({total_batches} batches) ---")
            for b_idx, batch in enumerate(batches):
                print(f"Translating Batch [{b_idx+1}/{total_batches}] (Rows {batch[0]+1} to {batch[-1]+1})...")
                
                batch_inputs = []
                for idx in batch:
                    entry_name = rows[idx]["Entry Name"]
                    match = re.search(r'cha(\d{3})', entry_name)
                    speaker_code = "cha" + match.group(1) if match else "unknown"
                    batch_inputs.append({"id": idx, "speaker_id": speaker_code, "text": rows[idx]["English"]})
                    
                batch_results = translate_batch(api_key, batch_inputs)
                
                if batch_results is not None:
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
                    print("[WARNING] Batch failed. Falling back to single line translations...")
                    for idx in batch:
                        english = rows[idx]["English"]
                        print(f"  Row {idx+1} | Translating individually...")
                        vietnamese = translate_single(api_key, english)
                        if vietnamese:
                            rows[idx]["Vietnamese"] = vietnamese
                            translated_count += 1
                            unsaved_changes = True
                            print(f"  -> {vietnamese}")
                        time.sleep(1.5)
                    print("-" * 50)
                    
                if unsaved_changes:
                    temp_csv = CSV_PATH + ".tmp"
                    with open(temp_csv, "w", newline="", encoding="utf-8-sig") as f:
                        writer = csv.DictWriter(f, fieldnames=["File Path", "Entry Name", "Entry Index", "English", "Vietnamese"])
                        writer.writeheader()
                        writer.writerows(rows)
                    if os.path.exists(temp_csv):
                        os.replace(temp_csv, CSV_PATH)
                        unsaved_changes = False
                
                time.sleep(SLEEP_BETWEEN_BATCHES)

        if long_row_indices:
            print(f"--- Starting Single Translation for {len(long_row_indices)} long rows ---")
            for l_idx, idx in enumerate(long_row_indices):
                english = rows[idx]["English"]
                print(f"Long Row [{l_idx+1}/{len(long_row_indices)}] (Row {idx+1})...")
                vietnamese = translate_single(api_key, english)
                if vietnamese:
                    rows[idx]["Vietnamese"] = vietnamese
                    translated_count += 1
                    unsaved_changes = True
                    print(f"  -> {vietnamese}")
                
                if unsaved_changes:
                    temp_csv = CSV_PATH + ".tmp"
                    with open(temp_csv, "w", newline="", encoding="utf-8-sig") as f:
                        writer = csv.DictWriter(f, fieldnames=["File Path", "Entry Name", "Entry Index", "English", "Vietnamese"])
                        writer.writeheader()
                        writer.writerows(rows)
                    if os.path.exists(temp_csv):
                        os.replace(temp_csv, CSV_PATH)
                        unsaved_changes = False
                
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
        print(f"Session finished. Translated: {translated_count} new entries.")
        print("============================================================")

if __name__ == "__main__":
    main()
