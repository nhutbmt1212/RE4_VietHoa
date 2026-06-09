"""
Kiểm tra: file .msg.22 trong extracted_msg sau khi compile có đúng không?
REMSG_Converter compile ra file mới - xem nó có đúng content không
"""
import json, os, sys, subprocess, shutil, zlib, struct
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

EXTRACTED  = r'd:\RE4_VietHoa\extracted_msg'
SCRIPT_DIR = r'd:\RE4_VietHoa'
GAME_DIR   = r'd:\Games\Resident Evil 4'

# Test với ch_mes_main_sys_common
src_msg  = os.path.join(EXTRACTED, r'natives\stm\_chainsaw\message\mes_main_sys\ch_mes_main_sys_common.msg.22')
src_json = src_msg + '.json'

print("=== Test compile ch_mes_main_sys_common ===")
print(f"msg  exists: {os.path.exists(src_msg)}")
print(f"json exists: {os.path.exists(src_json)}")

# Đọc json gốc và sửa entry 191
with open(src_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

entry = data['entries'][191]
print(f"\nEntry 191 TRƯỚC khi sửa:")
print(f"  content[0] = {repr(entry['content'][0])}")
print(f"  content[1] = {repr(entry['content'][1])}")

# Áp dụng logic import_translation
VIET = 'ĐƯỢC HỖ TRỢ'
content = entry['content']
for i in range(len(content)):
    if content[i].strip() or i == 1:
        content[i] = VIET

print(f"\nEntry 191 SAU khi sửa:")
print(f"  content[0] = {repr(entry['content'][0])}")
print(f"  content[1] = {repr(entry['content'][1])}")

# Lưu json tạm
tmp_dir = r'd:\RE4_VietHoa\tmp_test_compile'
os.makedirs(tmp_dir, exist_ok=True)
tmp_msg  = os.path.join(tmp_dir, 'ch_mes_main_sys_common.msg.22')
tmp_json = tmp_msg + '.json'

shutil.copy2(src_msg, tmp_msg)
with open(tmp_json, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Compile với REMSG_Converter
remsg_script = os.path.join(SCRIPT_DIR, 'tools', 'REMSG_Converter', 'src', 'main.py')
print(f"\nCompiling with: {remsg_script}")
cmd = ['python', remsg_script, '-i', tmp_msg, '-e', tmp_json, '-m', 'json']
res = subprocess.run(cmd, capture_output=True, text=True)
print(f"Return code: {res.returncode}")
if res.stderr:
    print(f"STDERR: {res.stderr[:500]}")
if res.stdout:
    print(f"STDOUT: {res.stdout[:500]}")

new_msg = tmp_msg + '.new'
print(f"\n.new file exists: {os.path.exists(new_msg)}")

if os.path.exists(new_msg):
    # Đọc file mới và kiểm tra nội dung
    with open(new_msg, 'rb') as f:
        raw = f.read()
    
    print(f"File size: {len(raw)} bytes")
    print(f"Magic: {raw[:4].hex()}")
    
    # Tìm chuỗi tiếng Việt
    viet_utf16 = VIET.encode('utf-16-le')
    viet_utf8  = VIET.encode('utf-8')
    eng_utf16  = 'ASSISTED'.encode('utf-16-le')
    
    print(f"\nSearch in compiled .msg.22:")
    print(f"  'ĐƯỢC HỖ TRỢ' (UTF-16-LE): {'FOUND' if viet_utf16 in raw else 'NOT FOUND'}")
    print(f"  'ĐƯỢC HỖ TRỢ' (UTF-8):     {'FOUND' if viet_utf8 in raw else 'NOT FOUND'}")
    print(f"  'ASSISTED' (UTF-16-LE):    {'FOUND' if eng_utf16 in raw else 'NOT FOUND'}")
    
    # So sánh với file gốc
    with open(src_msg, 'rb') as f:
        orig_raw = f.read()
    print(f"\nOriginal msg size: {len(orig_raw)} bytes")
    print(f"Compiled msg size: {len(raw)} bytes")
    print(f"  'ASSISTED' in original: {'FOUND' if eng_utf16 in orig_raw else 'NOT FOUND'}")

# Cleanup
shutil.rmtree(tmp_dir, ignore_errors=True)

# Cũng kiểm tra REMSG_Converter version
print()
print("=== REMSG_Converter info ===")
remsg_dir = os.path.join(SCRIPT_DIR, 'tools', 'REMSG_Converter', 'src')
if os.path.exists(remsg_dir):
    for f in os.listdir(remsg_dir):
        print(f"  {f}")
