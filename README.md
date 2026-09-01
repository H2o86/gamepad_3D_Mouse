# Flydigi Dune Fox -> SolidWorks 3D SpaceMouse & Advanced Control Center

Biến tay cầm **Flydigi Dune Fox** thành thiết bị **3D SpaceMouse chuyên dụng cho SolidWorks** với 2 tính năng cao cấp mới: **Lọc cửa sổ SolidWorks (Window Scope Filter)** và **Khóa con trỏ chuột ở trung tâm màn hình (Cursor Centering Lock)**!

---

## 🌟 Tính Năng Nổi Bật

1. **Lọc Cửa Sổ Cực Kỳ Thông Minh (App Window Scope Filtering):**
   - Chỉ kích hoạt điều khiển tay cầm khi cửa sổ **SOLIDWORKS** đang mở và được chọn (Active Foreground Window).
   - Tự động tạm dừng điều khiển khi bạn chuyển sang duyệt web, Word, Messenger..., giúp gõ phím và dùng máy tính hoàn toàn bình thường mà không lo tay cầm va chạm nhầm.

2. **Khóa Con Trỏ Chuột Tại Trung Tâm Màn Hình (Cursor Centering Lock):**
   - Giải quyết triệt để vấn đề con trỏ chuột bị trôi đụng viền màn hình khi xoay góc 3D liên tục.
   - Khi gạt cần (Rotate/Pan/Zoom), con trỏ chuột được neo cố định tại trung tâm màn hình (`SetCursorPos`).
   - Khi thả tay cầm ra, con trỏ chuột tự động trả về đúng vị trí ban đầu bạn đang thao tác!

3. **Tự Do Gán Phím Chức Năng (Custom Keybinding Engine):**
   - Thư viện phím tắt chuẩn SolidWorks 2019 từ file `SW Shortkey.pdf` (Isometric `Ctrl+7`, Normal To `Ctrl+8`, Smart Dimension `D`, Line `L`, Extrude `E`, Rebuild `Ctrl+B`, Undo `Ctrl+Z`, Hide Component `TAB`...).
   - Chọn từ menu thả xuống hoặc tự nhập phím tùy ý (`Ctrl+Alt+S`, `F5`...).

4. **Độ Trễ Siêu Thấp (~1ms):** Sử dụng trực tiếp Native Windows Ctypes `XInput` & `SendInput` API với tần số quét 120Hz.

---

## 🚀 Hướng Dẫn Sử Dụng

### Khởi chạy Giao diện Quản lý (GUI)
```bash
python gui.py
```
- **Tab 1 ("Gán Phím Chức Năng"):** Chọn phím tắt hoặc gõ phím tùy ý cho 14 nút bấm.
- **Tab 2 ("Cửa Sổ SolidWorks & Con Trỏ Chuột"):**
  - Tick chọn **"Chỉ kích hoạt khi mở SolidWorks"**.
  - Tick chọn **"Khóa con trỏ chuột tại trung tâm màn hình"**.
  - Bấm **"💾 Lưu Cài Đặt Tất Cả"**.
- **Tab 3 ("Monitor Tín Hiệu"):** Xem tên cửa sổ đang active và trạng thái nút bấm real-time.
