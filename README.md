# 🖐️ AI Hand Gesture Controller

A real-time system to control your computer using hand gestures, powered by **MediaPipe**, **OpenCV**, and **Python**. Control your mouse, volume, scrolling, and media playback — all without touching your keyboard.

---

## ✨ Features

- 🖱️ **Mouse Control** – Move your cursor with your right index finger.
- 👆 **Clicking** – Tap your thumb while pointing to click.
- 🔊 **Volume Control** – Pinch with your left hand to raise/lower volume.
- 🖱️ **Scrolling** – Scroll by moving your left index and middle fingers.
- ⏯️ **Play/Pause** – Bring both hands together with index, middle, and thumb fingers extended.
- 🧠 **Smoothing & Deadzone** – Prevents jitter and small unintended movements.
- 🔍 **Debug Overlay** – Shows which gestures are detected in real time.

---

## 🗂️ Project Structure

```

handControl/
├── main.py # Entry point for the app
├── hand_utils.py # Hand landmark smoothing, finger state logic
├── mouse_control.py # Cursor movement and click detection
├── volume_control.py # Volume adjustment via pinch gesture
├── scroll_control.py # Scrolling via hand movement
├── media_control.py # Play/pause gesture logic
├── debug_info.py # Overlay for gesture feedback
├── requirements.txt # Python dependencies

```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8–3.11
- Windows OS (volume control uses Pycaw)

### Installation

1. Clone the repo:

   ```bash
   git clone https://github.com/yourusername/hand-gesture-controller.git
   cd hand-gesture-controller
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Running the App

```bash
python main.py
```

### Controls

| Gesture                              | Action         |
| ------------------------------------ | -------------- |
| Right index extended                 | Move cursor    |
| Right index + thumb tap              | Click          |
| Left thumb + index pinch             | Volume control |
| Left index + middle swipe            | Scroll up/down |
| Both hands: thumb/index/middle close | Play/Pause     |

Press `ESC` to exit the app.

---

## 🧪 How It Works

- MediaPipe detects hand landmarks in real time.
- Smoothing + deadzone filters applied to reduce jitter.
- Finger states are checked to infer gestures.
- Actions sent to OS using `pyautogui` and `pycaw`.

---

## 🛠 Customization

- Adjust smoothing factor in `hand_utils.py`
- Add new gestures in `gesture_detection.py` or similar
- Modify sensitivity or deadzones to suit your needs

---

## 📸 Demo

_(Include a GIF or video of your hand controlling the desktop here)_

---

## 🙏 Credits

- [Google MediaPipe](https://github.com/google/mediapipe)
- [PyAutoGUI](https://github.com/asweigart/pyautogui)
- [Pycaw](https://github.com/AndreMiras/pycaw)

---

## 📝 License

This project is licensed under the MIT License.
