import threading
import time
import cProfile
import pstats
import io

from hand_utils import init_mediapipe, process_hands
from mouse_control import handle_mouse_control
from volume_control import handle_volume_control
from scroll_control import handle_scroll_control

class ProcessingThread(threading.Thread):
    def __init__(self, frame_source):
        super().__init__(daemon=True)
        self.frame_source = frame_source
        self.processed_frame = None
        self.hand_data = None
        self.extra_info = {}
        self.stopped = False
        self.lock = threading.Lock()

        self.hands = init_mediapipe()

        # For profiling mouse control
        self.profiler = cProfile.Profile()
        self.profile_interval = 5.0  # seconds
        self.last_profile_time = time.time()

    def run(self):
        while not self.stopped:
            grabbed, frame = self.frame_source.read()
            if not grabbed or frame is None:
                time.sleep(0.001)
                continue

            frame_flipped = frame[:, ::-1, :].copy()  # flip horizontally

            processed_frame, hand_data = process_hands(frame_flipped, self.hands)

            # Profile mouse control selectively every profile_interval seconds
            now = time.time()
            mouse_info = {}

            mouse_info = handle_mouse_control(hand_data, frame)

            volume_info = handle_volume_control(hand_data, processed_frame)
            scroll_info = handle_scroll_control(hand_data, processed_frame)

            extra_info = {**mouse_info, **volume_info, **scroll_info}

            with self.lock:
                self.processed_frame = processed_frame
                self.hand_data = hand_data
                self.extra_info = extra_info

    def get_processed(self):
        with self.lock:
            return self.processed_frame, self.hand_data, self.extra_info

    def stop(self):
        self.stopped = True
