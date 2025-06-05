import numpy as np
import time
from collections import deque
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

from config_loader import load_config

volume_speed = load_config()["volume_speed_factor"]
volume_ctrl = cast(AudioUtilities.GetSpeakers().Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None), POINTER(IAudioEndpointVolume))

vol_min, vol_max = volume_ctrl.GetVolumeRange()[:2]
pinch_buffer = deque(maxlen=10)

_min_direction_hold_time = 0.5  # seconds; minimum stable motion duration

# State tracking for direction and time
last_direction = 0  # +1 for increasing pinch distance, -1 for decreasing, 0 for start
last_direction_change_time = 0

def get_vol():
    return (volume_ctrl.GetMasterVolumeLevel() - vol_min) / (vol_max - vol_min)

def set_vol(level):
    volume_ctrl.SetMasterVolumeLevel(vol_min + level * (vol_max - vol_min), None)

def handle_volume_control(hand_data, frame):
    global last_direction, last_direction_change_time
    volume_changed = False

    for hand in hand_data:
        if hand["label"] != "Left":
            continue
        if hand.get("middle_extended"):  # Don't adjust volume if middle finger is raised
            continue

        lm = hand["landmarks"]
        pinch_dist = np.linalg.norm([
            lm[4].x - lm[8].x,
            lm[4].y - lm[8].y,
            lm[4].z - lm[8].z
        ])
        pinch_buffer.append(pinch_dist)

        if len(pinch_buffer) == 10:
            speed = (pinch_buffer[-1] - pinch_buffer[0]) / 10
            vol = get_vol()

            # Determine current direction of motion
            current_direction = 0
            if speed > 0.0015:
                current_direction = 1
            elif speed < -0.0015:
                current_direction = -1

            now = time.time()
            if current_direction != 0:
                # Check if direction changed
                if current_direction != last_direction:
                    # Direction changed - check how quickly
                    time_since_change = now - last_direction_change_time
                    if time_since_change < _min_direction_hold_time:
                        # Ignore this change because it happened too fast
                        continue
                    # Accept the change
                    last_direction = current_direction
                    last_direction_change_time = now
                else:
                    # Direction stable - update last change time
                    last_direction_change_time = now

                # Apply volume change only if direction stable
                if current_direction == 1:
                    set_vol(min(1.0, vol + 0.01 * volume_speed))
                    volume_changed = True
                elif current_direction == -1:
                    set_vol(max(0.0, vol - 0.01 * volume_speed))
                    volume_changed = True

    return {"Volume": f"{int(get_vol() * 100)}%" if volume_changed else "Idle"}
