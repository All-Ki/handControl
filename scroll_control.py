from pynput.mouse import Controller as MouseController
import numpy as np
from collections import deque
import time

mouse = MouseController()
scroll_buffer = deque(maxlen=5)
_last_time = time.time()
_fps_buffer = []

def _measure_fps():
    global _last_time, _fps_buffer
    current_time = time.time()
    dt = current_time - _last_time
    _last_time = current_time

    fps = 1 / dt if dt > 0 else 0
    _fps_buffer.append(fps)
    if len(_fps_buffer) > 10:
        _fps_buffer.pop(0)
    return sum(_fps_buffer) / len(_fps_buffer)

def handle_scroll_control(hand_data, frame):
    dy = 0  # initialize scroll delta y

    for hand in hand_data:
        if hand["label"] != "Left":
            continue

        if hand.get("index_extended") and hand.get("middle_extended", False):
            lm = hand["landmarks"]
            # Average position between index (8) and middle (12) fingertips
            x = (lm[8].x + lm[12].x) / 2 * frame.shape[1]
            y = (lm[8].y + lm[12].y) / 2 * frame.shape[0]

            scroll_buffer.append((x, y))

            if len(scroll_buffer) == 5:
                dy = scroll_buffer[-1][1] - scroll_buffer[0][1]

                if abs(dy) > 5:
                    # Scroll vertically: positive = scroll up, negative = scroll down
                    # Adjust divisor as needed for sensitivity
                    scroll_amount = int(-dy / 5)
                    mouse.scroll(0, scroll_amount)

    fps = _measure_fps()
    return {"Scroll ΔY": f"{int(dy)}", "Scroll FPS": f"{int(fps)}"}
