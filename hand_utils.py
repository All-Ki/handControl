import mediapipe as mp
import cv2
import numpy as np
from mediapipe.framework.formats import landmark_pb2

alpha = 0.3  # smoothing factor; closer to 0 means more smoothing, 1 means no smoothing

import math

class LandmarkSmoother:
    def __init__(self, alpha=0.3, deadzone=0.003):
        self.alpha = alpha
        self.smoothed_landmarks = None
        self.deadzone = deadzone  # threshold for minimal vector movement

    def smooth(self, landmarks):
        if self.smoothed_landmarks is None:
            self.smoothed_landmarks = landmarks
            return landmarks

        smoothed = []
        for i, lm in enumerate(landmarks):
            prev = self.smoothed_landmarks[i]

            dx = lm.x - prev.x
            dy = lm.y - prev.y
            dz = lm.z - prev.z

            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist < self.deadzone:
                # Movement too small, keep previous smoothed coordinate
                new_x, new_y, new_z = prev.x, prev.y, prev.z
            else:
                # Smooth normally
                new_x = self.alpha * lm.x + (1 - self.alpha) * prev.x
                new_y = self.alpha * lm.y + (1 - self.alpha) * prev.y
                new_z = self.alpha * lm.z + (1 - self.alpha) * prev.z

            smoothed.append(landmark_pb2.NormalizedLandmark(
                x=new_x, y=new_y, z=new_z
            ))

        self.smoothed_landmarks = smoothed
        return smoothed

def init_mediapipe():
    return mp.solutions.hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=0
    )


# Create a dictionary to store smoothers per hand label
smoothers = {
    "Left": LandmarkSmoother(alpha=0.3),
    "Right": LandmarkSmoother(alpha=0.3),
}

def process_hands(frame, hands):
    mp_drawing = mp.solutions.drawing_utils
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    hand_data = []
    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            label = handedness.classification[0].label

            # Use the new LandmarkSmoother here!
            current_landmarks = hand_landmarks.landmark
            smoothed_landmarks = smoothers[label].smooth(current_landmarks)

            fingers = get_fingers_extended(smoothed_landmarks)

            hand_data.append({
                "label": label,
                "landmarks": smoothed_landmarks,
                **fingers
            })

            mp_drawing.draw_landmarks(
                frame,
                landmark_pb2.NormalizedLandmarkList(landmark=smoothed_landmarks),
                mp.solutions.hands.HAND_CONNECTIONS
            )

    return frame, hand_data
def get_angle(a, b, c):
    ab = np.array([a.x - b.x, a.y - b.y, a.z - b.z])
    cb = np.array([c.x - b.x, c.y - b.y, c.z - b.z])
    dot_product = np.dot(ab, cb)
    norm_ab = np.linalg.norm(ab)
    norm_cb = np.linalg.norm(cb)
    if norm_ab == 0 or norm_cb == 0:
        return 0
    cosine_angle = dot_product / (norm_ab * norm_cb)
    angle = math.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))
    return angle

def is_thumb_extended(landmarks):
    angle = get_angle(landmarks[2], landmarks[3], landmarks[4])
    return angle > 100  # Threshold, tweak if needed
def get_fingers_extended(landmarks):
    def is_finger_extended(base, mid, tip, threshold=160):
        return get_angle(landmarks[base], landmarks[mid], landmarks[tip]) > threshold

    return {
        "thumb_extended": get_angle(landmarks[2], landmarks[3], landmarks[4]) > 150,
        "index_extended": is_finger_extended(6, 7, 8),
        "middle_extended": is_finger_extended(10, 11, 12),
        "ring_extended": is_finger_extended(14, 15, 16),
        "pinky_extended": is_finger_extended(18, 19, 20),
    }