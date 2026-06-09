"""
Hash không khớp với patch_001~005 -> cần tìm hash đúng từ game PAK
Chiến lược: 
1. Lấy file msg.22 gốc từ main pak (extracted_msg đã có sẵn)
2. Tính hash theo cách KHÁC và so sánh với PAK

Thử các biến thể hash path khác nhau:
- Có/không có dấu /
- Uppercase/lowercase toàn bộ
- Với extension khác nhau
- Thêm null terminator
"""
import struct, sys, os, zlib
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
sys.path.insert(0, r'd:\RE4_VietHoa')
from pak_builder import murmur3_32, get_filename_hash

GAME_DIR  = r'd:\Games\Resident Evil 4'
EXTRACTED = r'd:\RE4_VietHoa\extracted_msg'

# Đọc PAK gốc (main) để tìm hash thực sự
# Main PAK quá lớn (57GB), thay vào đó đọc patch_005 và lấy một file ta biết để reverse engineer hash

# Cách khác: đọc một file gốc từ extracted_msg,
# tính sha/hash của nó và tìm trong PAK
# -> Nhưng PAK dùng filename hash, không phải content hash

# Thử: dùng test_hash.exe hoặc test_hash.cs nếu có
test_hash_exe = r'd:\RE4_VietHoa\test_hash.exe'
if os.path.exists(test_hash_exe):
    print("test_hash.exe found!")
    import subprocess
    # Test với path đã biết
    result = subprocess.run([test_hash_exe, '/natives/stm/_chainsaw/message/mes_main_sys/ch_mes_main_sys_common.msg.22'],
                          capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
else:
    print("test_hash.exe not found")

print()

# Đọc test_hash.cs để biết thuật toán
test_hash_cs = r'd:\RE4_VietHoa\test_hash.cs'
print("=== test_hash.cs ===")
with open(test_hash_cs, 'r', encoding='utf-8') as f:
    content = f.read()
print(content[:3000])
