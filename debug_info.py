import threading
import cv2
import time
import numpy as np

# Internal FPS tracking state
_prev_time = time.time()
_fps_buffer = []
_last_volume = 0.0
def draw_text_with_outline(img, text, pos, font=cv2.FONT_HERSHEY_SIMPLEX, 
                           font_scale=0.6, thickness=2, text_color=(0,255,0), outline_color=(0,0,0)):
    x, y = pos
    # Draw thicker outline (black)
    cv2.putText(img, text, (x, y), font, font_scale, outline_color, thickness + 2, cv2.LINE_AA)
    # Draw thinner text (green)
    cv2.putText(img, text, (x, y), font, font_scale, text_color, thickness, cv2.LINE_AA)


def draw_volume_bar(frame, volume, pos=(180, 60), size=(150, 20)):
    x, y = pos
    w, h = size
    
    # Draw bar background (gray)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 50), -1)
    
    # Calculate width of filled bar
    fill_w = int(w * volume)
    
    # Draw filled volume bar (green)
    cv2.rectangle(frame, (x, y), (x + fill_w, y + h), (0, 255, 0), -1)
    
    # Draw bar border (white)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
    
    # Draw volume percentage text
    vol_text = f"{int(volume * 100)}%"
    # Use outlined text function for clarity
    draw_text_with_outline(frame, vol_text, (x + w + 10, y + h - 5), font_scale=0.7)

def draw_debug_info(frame, hand_data, extra_info):
    global _prev_time, _fps_buffer, _last_volume
    if frame is None:
        return None

    if not isinstance(frame, np.ndarray):
        print(f"[Debug] Frame is not a numpy array: {type(frame)}")
        return frame

    if not frame.flags['C_CONTIGUOUS']:
        frame = np.ascontiguousarray(frame)

    if frame.dtype != np.uint8:
        frame = frame.astype(np.uint8)

    # --- Calculate FPS ---
    current_time = time.time()
    fps = 1 / (current_time - _prev_time) if current_time != _prev_time else 0
    _prev_time = current_time

    _fps_buffer.append(fps)
    if len(_fps_buffer) > 10:
        _fps_buffer.pop(0)
    smoothed_fps = sum(_fps_buffer) / len(_fps_buffer)

    info = {"FPS": f"{int(smoothed_fps)}"}
    info.update(extra_info)

    y = 20
    for label, value in info.items():
        draw_text_with_outline(frame, f"{label}: {value}", (10, y))
        y += 25

    # Draw volume bar if volume info exists in extra_info
    if "Volume" in extra_info:
        # Convert "Volume" string "45%" to float 0.45
        vol_str = extra_info["Volume"]
        if vol_str.endswith("%"):
            try:
                _last_volume  = float(vol_str[:-1]) / 100
            except Exception:
                pass  # just skip if parsing fails
    draw_volume_bar(frame, _last_volume)

    for hand in hand_data:
        for lm in hand["landmarks"]:
            cx, cy = int(lm.x * frame.shape[1]), int(lm.y * frame.shape[0])
            cv2.circle(frame, (cx, cy), 3, (255, 0, 0), -1)

    return frame

class DebugDrawThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.raw_frame = None
        self.hand_data = None
        self.extra_info = None
        self.lock = threading.Lock()
        self.debug_frame = None
        self.stopped = False

    def update_data(self, frame, hand_data, extra_info):
        with self.lock:
            self.raw_frame = frame
            self.hand_data = hand_data
            self.extra_info = extra_info

    def get_debug_frame(self):
        with self.lock:
            if self.debug_frame is None:
                return None
            return self.debug_frame.copy()

    def run(self):
        while not self.stopped:
            with self.lock:
                if self.raw_frame is None:
                    time.sleep(0.01)
                    continue

                # Prepare debug frame by drawing debug info
                # Use your existing draw_debug_info function here:
                self.debug_frame = draw_debug_info(self.raw_frame.copy(), 
                                                   self.hand_data if self.hand_data else [],
                                                   self.extra_info if self.extra_info else {})

            time.sleep(0.01)

    def stop(self):
        self.stopped = True