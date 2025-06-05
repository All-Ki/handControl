import numpy as np
import pyautogui  # You can replace this with other media control libraries if needed

class MediaControl:
    def __init__(self, threshold=0.05):
        self.threshold = threshold
        self.playing = False
        self.toggled = False

    def distance(self, lm1, lm2):
        return np.sqrt((lm1.x - lm2.x) ** 2 + (lm1.y - lm2.y) ** 2 + (lm1.z - lm2.z) ** 2)

    def check_play_pause(self, hand_data):
        if len(hand_data) < 2:
            self.toggled = False
            return {}

        left_hand = next((h for h in hand_data if h["label"] == "Left"), None)
        right_hand = next((h for h in hand_data if h["label"] == "Right"), None)
        if not left_hand or not right_hand:
            self.toggled = False
            return {}

        # Require index and middle fingers to be extended on both hands
        required_fingers = ["index_extended", "middle_extended"]
        if not all(left_hand.get(f, False) for f in required_fingers):
            self.toggled = False
            return {}
        if not all(right_hand.get(f, False) for f in required_fingers):
            self.toggled = False
            return {}

        # Check if the index and middle fingertips are close between hands
        close_index = self.distance(left_hand["landmarks"][8], right_hand["landmarks"][8]) < self.threshold
        close_middle = self.distance(left_hand["landmarks"][12], right_hand["landmarks"][12]) < self.threshold

        if close_index and close_middle:
            print("Play/Pause toggled")
            if not self.toggled:
                pyautogui.press('playpause')  # Send play/pause media key
                self.playing = not self.playing
                self.toggled = True
                return {"Media": "Play" if self.playing else "Pause"}
        else:
            self.toggled = False

        return {}
