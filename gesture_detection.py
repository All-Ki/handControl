import cv2
import numpy as np
import mediapipe as mp
from collections import deque
from hand_utils import init_mediapipe

mp_draw = mp.solutions.drawing_utils

state_buffers = {
    "right_index": deque(maxlen=5),
    "right_thumb": deque(maxlen=5),
    "left_middle": deque(maxlen=5),
    "left_index": deque(maxlen=5)
}

def vector_3d(a, b):
    return np.array([b.x - a.x, b.y - b.y, b.z - a.z])

def is_finger_extended(lm, tip_id, pip_id, threshold=1.1):
    wrist = lm[0]
    tip = lm[tip_id]
    pip = lm[pip_id]
    return distance_3d(wrist, tip) > distance_3d(wrist, pip) * threshold

def distance_3d(a, b):
    return np.linalg.norm(np.array([a.x - b.x, a.y - b.y, a.z - b.z]))

def process_hands(frame, hands):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    hand_data = []

    if result.multi_hand_landmarks and result.multi_handedness:
        for lm, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
            label = handedness.classification[0].label
            mp_draw.draw_landmarks(frame, lm, mp.solutions.hands.HAND_CONNECTIONS)

            landmarks = lm.landmark
            index_ext = is_finger_extended(landmarks, 8, 6)
            thumb_ext = is_finger_extended(landmarks, 4, 3)
            ring_ext = is_finger_extended(landmarks, 16, 14)
            pinky_ext = is_finger_extended(landmarks, 20, 18)
            hand_data.append({
                "label": label,
                "landmarks": landmarks,
                "index_extended": index_ext,
                "thumb_extended": thumb_ext,
                "ring_extended": ring_ext,
                "pinky_extended": pinky_ext,
            })

    return frame, hand_data
