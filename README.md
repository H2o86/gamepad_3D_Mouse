# SolidMouse - Unified 3D SpaceMouse Control Center

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-brightgreen.svg)]()
[![SolidWorks](https://img.shields.io/badge/SolidWorks-2019%2B-orange.svg)]()
[![Languages](https://img.shields.io/badge/languages-EN%20%7C%20VI%20%7C%20JA%20%7C%20KO%20%7C%20ZH-purple.svg)]()

Convert your **Flydigi Dune Fox**, **Xbox**, or **PlayStation (PS4 DualShock 4 / PS5 DualSense)** gamepad into a dedicated **3D SpaceMouse for SolidWorks**!

![SolidMouse App Icon](assets/icon.png)

---

## 🌐 Supported Languages / 言語 / 언어 / 语言 / Ngôn Ngữ

SolidMouse supports 5 international languages with live in-app switching:
- 🇺🇸 **English (EN)**
- 🇻🇳 **Tiếng Việt (VI)**
- 🇯🇵 **日本語 (JA)**
- 🇰🇷 **한국어 (KO)**
- 🇨🇳 **中文 (ZH)**

---

## 📖 In-App User Guide & About Section

SolidMouse now features a dedicated **`📖 About & User Guide`** tab directly inside the software interface.
Switching your language automatically updates the user guide, default control map diagrams, connection steps, and troubleshooting tips!

---

## 🌟 Key Features

1. **Unified Multi-Controller Engine:**
   - **Xbox & Flydigi Dune Fox Controllers:** Powered by Native Windows `XInput` with ~1ms ultra-low latency.
   - **PlayStation PS4 / PS5 Controllers:** Powered by DirectInput & HID Engine.
   - **Auto Device Detection:** Seamlessly switches profiles depending on connected gamepad.

2. **6-Axis Gyroscope Navigation (PS4 / PS5 Motion Control):**
   - Tilt and rotate your PS4 DualShock 4 or PS5 DualSense controller to rotate 3D CAD models in SolidWorks naturally in physical space!

3. **Smooth Cursor Edge Wrapping (Anti-Border Drift):**
   - Keeps 3D viewport rotation 100% smooth without cursor border collisions or stuttering. Automatically restores cursor to initial position when releasing joysticks.

4. **SOLIDWORKS Window Focus Filtering:**
   - Automatically activates 3D navigation only when the **SOLIDWORKS** window is active, avoiding interference with other applications.

5. **Customizable Key Mapper & Preset Library:**
   - Built-in SolidWorks 2019 shortcut catalog from `SW Shortkey.pdf` (Isometric `Ctrl+7`, Normal To `Ctrl+8`, Smart Dimension `D`, Line `L`, Extrude `E`, Rebuild `Ctrl+B`, Undo `Ctrl+Z`, Hide Component `TAB`, etc.).
   - Rebind all 14 controller buttons with custom key combinations.

---

## 🚀 Download & Installation

### Option 1: Automatic Windows Installer (Recommended for end-users)
Download and run **[`installer_dist/SolidMouse_Setup_v1.0.0.exe`](installer_dist/SolidMouse_Setup_v1.0.0.exe)**.
- Installs to `C:\Program Files\SolidMouse`.
- Creates Desktop & Start Menu shortcuts.
- Optional Windows Startup autostart.

### Option 2: Standalone Executable
Directly run **[`dist/SolidMouse.exe`](dist/SolidMouse.exe)** (No Python installation required).

### Option 3: Run from Python Source
```bash
python gui.py
```
