# Luồng Hoạt Động Của Dự Án Việt Hóa Resident Evil 4

Tài liệu này ghi chú lại luồng đi (workflow) chi tiết của toàn bộ hệ thống Việt hóa Resident Evil 4, từ khâu quản lý dữ liệu gốc đến quá trình biên dịch và tiêm (inject) dữ liệu vào game.

## 1. Quản Lý Dữ Liệu Dịch Thuật (CSV)
Toàn bộ dữ liệu hội thoại, menu, và giao diện đều được quản lý trong file `vietnamese_translation.csv`.
- **Nguồn dữ liệu**: Được trích xuất từ các file `.msg.22.json` gốc nằm trong thư mục `extracted_msg/`.
- **Chỉnh sửa/Thêm mới**: Khi phát hiện các dòng text chưa được dịch (như *Crouch / Stand*, *Crude Charm*), script `append_csv_fixed.py` sẽ được dùng để tìm đúng Entry ID, File Path và thêm trực tiếp vào file CSV dưới chuẩn bảng mã `UTF-8-SIG`.

## 2. Tiêm Bản Dịch Vào File JSON Gốc (`import_translation.py`)
Mỗi khi có thay đổi trong bản dịch, script `import_translation.py` sẽ đảm nhiệm việc nạp dữ liệu:
- Đọc từng dòng của `vietnamese_translation.csv`.
- Mở file `.msg.22.json` gốc tương ứng.
- **Can thiệp Slot**: Ghi đè chuỗi tiếng Việt vào **Slot 1 (Ngôn ngữ tiếng Anh)** và các slot ngôn ngữ đang kích hoạt khác. Việc này đảm bảo cho dù người chơi đang set ngôn ngữ gì trong game thì cũng sẽ hiển thị tiếng Việt.
- Dữ liệu JSON sau khi tiêm được lưu tạm vào thư mục `vietnamese_mod/`.

## 3. Đóng Gói Và Mã Hóa Lại Thành Định Dạng RE Engine (`REMSG_Converter`)
RE Engine không đọc trực tiếp file JSON mà sử dụng định dạng nhị phân `.msg.22` đã được mã hóa XOR.
- Script sẽ gọi công cụ `REMSG_Converter/src/main.py`.
- Công cụ này lấy file JSON đã được chỉnh sửa ở bước 2, biên dịch và mã hóa ngược lại thành file `.msg.22` (có khả năng game RE4 đọc).
- Tổng cộng có khoảng **508 files** được biên dịch mỗi lần chạy.

## 4. Phương Pháp Inject (Tiêm) Vào Game

Có hai luồng inject được xây dựng trong dự án, nhưng luồng thứ hai là luồng quyết định sự thành công:

> **Luồng 1: Build PAK File (`pak_builder.py`)**
> Đây là cơ chế gốc của RE Engine. File `.msg.22` được đóng gói lại thành `re_chunk_000.pak.patch_006.pak`. Script dùng thuật toán `MurmurHash64A` để mã hóa đường dẫn ảo (Virtual Path) sao cho khớp với Index của game. 
> Tuy nhiên, do xung đột với mod **REFramework**, cách này không hoạt động hiệu quả 100%.

> **Luồng 2: LooseFileLoader (Luồng chính & Quyết định)**
> Mod REFramework mà game đang sử dụng tích hợp một tính năng tên là `LooseFileLoader`. Tính năng này buộc game **ưu tiên tải file "thả rông" (loose files) trực tiếp từ thư mục `natives/`**, bỏ qua các file `patch_xxx.pak`.
>
> **Quy trình hoạt động:**
> Ngay sau khi biên dịch xong 508 file `.msg.22`, script `import_translation.py` sẽ chép thẳng (copytree) toàn bộ thư mục `vietnamese_mod/natives/` vào thư mục cài game gốc: `d:\Games\Resident Evil 4\natives\`.

## 5. Kết Quả Cuối Cùng
Khi người chơi mở game:
1. REFramework phát hiện các file nằm trong `natives\`.
2. Nó chặn game load từ Main PAK (57GB) và ưu tiên tải các file `.msg.22` của chúng ta.
3. Chữ tiếng Việt xuất hiện một cách hoàn hảo trên tất cả các khía cạnh của game: Main Menu, Subtitle, UI Options, Item Descriptions, v.v.

---
**Tóm tắt Pipeline để bạn dùng sau này:**
Chỉnh sửa CSV $\rightarrow$ Chạy `import_translation.py` $\rightarrow$ Script tự động update JSON $\rightarrow$ Tự động Compile `.msg.22` $\rightarrow$ Tự động chép đè vào thư mục `natives\` của game $\rightarrow$ Mở game và thưởng thức.
