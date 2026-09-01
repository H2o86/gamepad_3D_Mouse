# SolidMouse - Unified 3D SpaceMouse Control Center

Phần mềm đóng gói độc lập chuyển đổi tay cầm **Flydigi Dune Fox**, **Xbox**, và **PlayStation PS4 (DualShock 4) / PS5 (DualSense)** thành thiết bị **3D SpaceMouse chuyên dụng cho SolidWorks**.

---

## 🌟 Tính Năng Nổi Bật

1. **Bản Đóng Gói Độc Lập `.exe` (No Python Required):**
   - Đã được đóng gói thành file thực thi duy nhất **`dist/SolidMouse.exe`**.
   - Chạy trực tiếp trên mọi máy tính Windows mà **không cần cài đặt Python**.
   - Tích hợp sẵn Icon dự án chuẩn Windows Taskbar và Titlebar.

2. **Hỗ Trợ Đa Tay Cầm (Unified Multi-Controller Support):**
   - **Flydigi Dune Fox / Xbox Controllers:** Chạy qua luồng Native Windows `XInput` với độ trễ siêu thấp (~1ms).
   - **PlayStation PS4 (DualShock 4) & PS5 (DualSense):** Chạy qua luồng DirectInput & HID Engine.
   - **Tự động nhận diện thiết bị (Auto Detect):** Tự chuyển đổi cấu hình phù hợp với loại tay cầm bạn đang cắm.

3. **Cảm Biến Con Quay Hồi Chuyển (6-Axis Gyroscope Navigation):**
   - Trên tay cầm PS4/PS5: Cho phép **giữ nút L2 (hoặc nghiêng tay cầm)** để xoay mô hình 3D trong SolidWorks trực quan theo chuyển động thực tế trong không gian!

4. **Lọc Cửa Sổ SolidWorks (Window Scope Filter):**
   - Chỉ kích hoạt điều khiển khi cửa sổ **SOLIDWORKS** đang mở và được chọn. Tự động tạm dừng khi bạn chuyển sang ứng dụng khác.

5. **Khóa Con Trỏ Chuột Chống Văng Viền (Edge Border Wrapping):**
   - Giữ luồng xoay 3D mượt 100% không bị gián đoạn hay giật khựng. Tự động trả con trỏ chuột về vị trí ban đầu khi thả gạt.

6. **Bộ Gán Phím Chức Năng Tùy Chỉnh (Custom Key Mapper):**
   - Tự do gán phím tắt SolidWorks 2019 từ file `SW Shortkey.pdf` hoặc nhập phím tùy chỉnh cho 14 nút bấm.
   - Tự động thay đổi nhãn nút bấm phù hợp với nhãn tay cầm: Xbox ($A/B/X/Y$) hay PlayStation ($\times/\bigcirc/\square/\Delta$).

---

## 🚀 Hướng Dẫn Sử Dụng

### Cách 1: Chạy File Thực Thi Độc Lập (Được khuyên dùng)
Double click vào file **[`dist/SolidMouse.exe`](file:///g:/My%20Drive/0-My%20Project/gamepad_3D_Mouse/dist/SolidMouse.exe)** để chạy ứng dụng ngay lập tức mà không cần cài đặt Python.

### Cách 2: Chạy Từ Mã Nguồn Python
```bash
python gui.py
```
