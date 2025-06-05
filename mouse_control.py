from pynput.mouse import Controller, Button
import time

mouse = Controller()

last_pos = None
smoothed_pos = None
click_state = {"thumb": False}
alpha = 0.7  # smoothing factor between 0 (max smoothing) and 1 (no smoothing)
_prev_time = time.time()
_fps_buffer = []

def _measure_fps():
    global _prev_time, _fps_buffer
    current_time = time.time()
    dt = current_time - _prev_time
    _prev_time = current_time

    fps = 1 / dt if dt > 0 else 0
    _fps_buffer.append(fps)

    if len(_fps_buffer) > 10:
        _fps_buffer.pop(0)

    return sum(_fps_buffer) / len(_fps_buffer)

def handle_mouse_control(hand_data, frame):
    global last_pos, smoothed_pos
    height, width = frame.shape[:2]

    for hand in hand_data:
        if hand["label"] != "Right":
            continue
        if(hand["middle_extended"] or hand["ring_extended"] or hand["pinky_extended"] ):
            break
        if hand["index_extended"]:
            idx = hand["landmarks"][8]
            current_pos = (idx.x * width, idx.y * height, idx.z)

            if smoothed_pos is None:
                smoothed_pos = current_pos
            else:
                # Exponential smoothing: new_pos = alpha * current + (1-alpha) * previous
                smoothed_pos = (
                    alpha * current_pos[0] + (1 - alpha) * smoothed_pos[0],
                    alpha * current_pos[1] + (1 - alpha) * smoothed_pos[1],
                    alpha * current_pos[2] + (1 - alpha) * smoothed_pos[2],
                )

            if last_pos is not None:
                dx = (smoothed_pos[0] - last_pos[0]) * 15
                dy = (smoothed_pos[1] - last_pos[1]) * 15

                # pynput's move takes integer values; round the deltas
                mouse.move(int(dx), int(dy))

            last_pos = smoothed_pos
        else:
            last_pos = None
            smoothed_pos = None

        # Thumb click handling
        if hand["thumb_extended"] and not click_state["thumb"]:
            mouse.click(Button.left)
            click_state["thumb"] = True
        elif not hand["thumb_extended"]:
            click_state["thumb"] = False

    fps = _measure_fps()
    return {"Mouse FPS": f"{int(fps)}"}
