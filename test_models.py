import urllib.request
import urllib.error
import json
import ssl
import sys

# Force stdout to UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://integrate.api.nvidia.com/v1/chat/completions"
api_key = "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"

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
7. Do NOT translate specific proper nouns, weapon names, boss/enemy names, items, collectibles, or organization names that are iconic to the Resident Evil series, as translating them makes them hard to recognize. Keep them in English.
8. If the text is a technical key, rejected code, or purely symbols (e.g. #Rejected#, <REF ...>), return it exactly as it is without translation.
9. No Chinese characters/scripts. Output exclusively standard Vietnamese text using only Vietnamese letters, spaces, numbers, common English terms as allowed, and standard punctuation.
"""

test_sentences = [
    "An interesting choice.\nI-I mean it in a good way, of course.",
    "A modest church located on top of a small hill. Its purpose has been warped by the sinister teachings of a local cult, leaving it a shadow of its former self.",
    "Luis has good firepower but weak close-quarter abilities.\nDuring Mayhem Mode, he can set dynamite with<ICON CP12_BR_ACTION>,\nwhich explodes after a certain amount of time or when shot."
]

models = [
    "meta/llama-3.3-70b-instruct",
    "mistralai/mistral-large-2-instruct",
    "google/gemma-3-12b-it",
    "nvidia/llama-3.1-nemotron-70b-instruct"
]

for model in models:
    print(f"\n=== Testing Model: {model} ===")
    for sentence in test_sentences:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": sentence}
            ],
            "temperature": 0.1,
            "max_tokens": 512
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                result = res_data["choices"][0]["message"]["content"].strip()
                print(f"EN: {repr(sentence)}")
                print(f"VI: {repr(result)}")
                print("-" * 30)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8')
            print(f"EN: {repr(sentence)} -> HTTP Error {e.code}: {e.reason}\nBody: {err_body}")
            print("-" * 30)
        except Exception as e:
            print(f"EN: {repr(sentence)} -> Error: {e}")
            print("-" * 30)
