import json, sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

p = r'd:\RE4_VietHoa\extracted_msg\natives\stm\_chainsaw\message\mes_main_conv\ch_mes_main_conv_cp11.msg.22.json'
with open(p, 'r', encoding='utf-8') as f:
    data = json.load(f)

for e in data['entries']:
    eng = e['content'][1] if len(e['content']) > 1 else ''
    vie = e['content'][0] if len(e['content']) > 0 else ''
    if eng and not eng.startswith('<') and not eng.startswith('#'):
        print(f"EN: {eng[:60].strip()}")
        print(f"VI: {vie[:60].strip()}")
        print('-')
