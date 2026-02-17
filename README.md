# 🚀 Productivity Tracker

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/UI-PySide6-green.svg)](https://pypi.org/project/PySide6/)
[![MediaPipe](https://img.shields.io/badge/AI-MediaPipe-orange.svg)](https://mediapipe.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Productivity Tracker** is a powerful, AI-driven desktop application designed to give you deep insights into your work habits. By combining computer vision with global input monitoring, it captures not just *what* you do, but *when* you are actually present and engaged.

---

### 📥 Download Latest Release

| Package | Type | Link | Description |
| :--- | :--- | :--- | :--- |
| **AppImage** | Portable | [**Download**](https://github.com/rahul713rk/Productivity_tracker/releases/download/v1.0/ProductivityTracker-x86_64.AppImage) | Run instantly. No install needed. |
| **DEB** | Installer | [**Download**](https://github.com/rahul713rk/Productivity_tracker/releases/download/v1.0/productivity-tracker_1.0_amd64.deb) | Native install for Ubuntu/Debian. |

### 💿 Installation Guide

**Option 1: AppImage (Recommended)**
```bash
chmod +x ProductivityTracker-x86_64.AppImage
./ProductivityTracker-x86_64.AppImage
```

**Option 2: DEB Package**
```bash
sudo dpkg -i productivity-tracker_1.0_amd64.deb
# If you get dependency errors:
sudo apt-get install -f
```

---

## ✨ Key Features

### 🤖 AI-Powered Presence Detection
*   **Face Tracking**: Automatically starts/stops the productivity timer using MediaPipe's BlazeFace model when it detects you at your desk.
*   **Privacy First**: All processing happens locally. No video is ever stored or transmitted.

### ⌨️ Deep Activity Insights
*   **Global Input Tracking**: Monitors keystrokes and mouse clicks relative to your focus time.
*   **Wayland & X11 Support**: Built-in support for modern Linux desktops using `evdev` and `pynput`.

### 📝 Integrated TODO Management
*   **Task Lifecycle**: Create, update, and categorize tasks.
*   **Smart Status**: Seamlessly move tasks between Pending, Working, and Completed.

### 📊 Data Analytics & Visualization
*   **Interactive Graphs**: View your productivity trends over time with Plotly-powered charts.
*   **Exportable Updates**: Automatically generates a `README.md` log of your daily achievements.

### 🌐 Cloud Sync
*   **GitHub Integration**: Automatically commits and pushes your daily logs to a remote repository to keep your portfolio active.

---

## 📸 Screenshots

<p align="center">
  <img src="assets/images/1.png" alt="Activity Tracking" width="800">
  <br>
  <em>Real-time Activity & Face Tracking</em>
</p>

<p align="center">
  <img src="assets/images/2.png" alt="Analytics" width="800">
  <br>
  <em>Detailed Analytics & Graphs</em>
</p>

<p align="center">
  <img src="assets/images/3.png" alt="GitHub Integration" width="800">
  <br>
  <em>GitHub Integration</em>
</p>

---

## 🛠️ Tech Stack

- **Core**: Python 3.9+
- **GUI**: PySide6 (Qt for Python)
- **Computer Vision**: OpenCV & MediaPipe
- **Data**: SQLite3 & Pandas
- **Visualization**: Plotly
- **Tracking**: Pynput & Evdev (for Linux/Wayland)

---

## 🚀 Getting Started

### Prerequisites

For Ubuntu/Debian users:
```bash
sudo apt update
sudo apt install python3-venv libxcb-cursor0 libgl1-mesa-glx
```

*Note: For Wayland activity tracking, your user must be in the `input` group:*
```bash
sudo usermod -aG input $USER
# Log out and log back in for changes to take effect
```

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/rahul713rk/Productivity_tracker.git
    cd Productivity_tracker
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python main.py
    ```

---

## 📦 Distribution & Building

The project is optimized for Linux distribution using **Nuitka**.

### Build a Standalone Binary
```bash
bash nuitka_build.sh
```
This creates a portable folder in `build/main.dist/`.

### Create an AppImage
```bash
bash create_appimage.sh
```
This downloads `appimagetool` (if missing) and packages the application into a single `.AppImage` file.

### Create a DEB Package (Debian/Ubuntu)
```bash
bash create_deb.sh
```
This creates a `.deb` installer. You can install it using:
```bash
sudo dpkg -i productivity-tracker_1.0_amd64.deb
```

---

## 📂 Project Structure

```text
├── assets/             # Assets (Icons, AI Models, Logs)
├── controller/         # Application Logic & Helpers
│   ├── path_manager.py # Cross-platform path handling
│   ├── camera_model.py # Face detection logic
│   └── activity_tracker.py # Input monitoring
├── model/              # Data Layer & External API
│   ├── database.py     # SQLite Management
│   └── git_model.py    # GitHub Sync Logic
├── view/               # PySide6 UI Components
├── main.py             # Entry point
└── requirements.txt    # Python dependencies
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📞 Contact

Rahul - [Your GitHub Profile](https://github.com/rahul713rk)

Project Link: [https://github.com/rahul713rk/Productivity_tracker](https://github.com/rahul713rk/Productivity_tracker)
