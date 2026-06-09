import json
path = r'C:\Users\nhutb\.gemini\antigravity-ide\brain\bc5d2e92-e63b-462f-8380-23df422fa2a8\.system_generated\logs\transcript.jsonl'
with open(path, 'r', encoding='utf-8') as f, open('logs_output.txt', 'w', encoding='utf-8') as out:
    for line in f:
        data = json.loads(line)
        if data.get('type') in ('USER_INPUT', 'PLANNER_RESPONSE', 'MODEL_RESPONSE'):
            content = data.get('content', '')
            if content:
                out.write(f"[{data.get('type')}] {content[:1000]}...\n")
