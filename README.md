# Unified 3D SpaceMouse Control Center (Flydigi Dune Fox & PlayStation PS4/PS5)

Phần mềm chuyển đổi tay cầm **Flydigi Dune Fox**, **Xbox**, và **PlayStation PS4 (DualShock 4) / PS5 (DualSense)** thành thiết bị **3D SpaceMouse chuyên dụng cho SolidWorks**.

---

## 🌟 Tính Năng Nổi Bật

1. **Hỗ Trợ Đa Tay Cầm (Unified Multi-Controller Support):**
   - **Flydigi Dune Fox / Xbox Controllers:** Chạy qua luồng Native Windows `XInput` với độ trễ siêu thấp (~1ms).
   - **PlayStation PS4 (DualShock 4) & PS5 (DualSense):** Chạy qua luồng DirectInput & HID Engine.
   - **Tự động nhận diện thiết bị (Auto Detect):** Tự chuyển đổi cấu hình phù hợp với loại tay cầm bạn đang cắm.

2. **Cảm Biến Con Quay Hồi Chuyển (6-Axis Gyroscope Navigation):**
   - Trên tay cầm PS4/PS5: Cho phép **giữ nút L2 (hoặc nghiêng tay cầm)** để xoay mô hình 3D trong SolidWorks trực quan theo chuyển động thực tế trong không gian!

3. **Lọc Cửa Sổ SolidWorks (Window Scope Filter):**
   - Chỉ kích hoạt điều khiển khi cửa sổ **SOLIDWORKS** đang mở và được chọn. Tự động tạm dừng khi bạn chuyển sang ứng dụng khác.

4. **Khóa Con Trỏ Chuột Chống Văng Viền (Edge Border Wrapping):**
   - Giữ luồng xoay 3D mượt 100% không bị gián đoạn hay giật khựng. Tự động trả con trỏ chuột về vị trí ban đầu khi thả gạt.

5. **Bộ Gán Phím Chức Năng Tùy Chỉnh (Custom Key Mapper):**
   - Tự do gán phím tắt SolidWorks 2019 từ file `SW Shortkey.pdf` hoặc nhập phím tùy chỉnh cho 14 nút bấm.
   - Tự động thay đổi nhãn nút bấm phù hợp với nhãn tay cầm: Xbox ($A/B/X/Y$) hay PlayStation ($\times/\bigcirc/\square/\Delta$).

---

## 🚀 Hướng Dẫn Sử Dụng

### Khởi chạy Giao diện Quản lý (GUI)
```bash
python gui.py
```
- Trên cùng có menu chọn Profile: `Auto Detect (Tự Động)` | `Xbox / Flydigi` | `PlayStation PS4/PS5`.
- Chỉnh độ nhạy Pan, Rotate, Zoom và Gyroscope theo sở thích.
- Bấm **"💾 Lưu Cài Đặt Tất Cả"**.

### Khởi chạy Service Ngầm (CLI)
```bash
python main.py
```
