import cv2
import time
from video_capture import VideoCaptureAsync
from processing_thread import ProcessingThread
from debug_info import DebugDrawThread
import numpy as np

def main():
    cap = VideoCaptureAsync().start()
    processing_thread = ProcessingThread(cap)
    processing_thread.start()
    
    debug_thread = DebugDrawThread()
    debug_thread.start()
    while True:
        processed_frame, hand_data, extra_info = processing_thread.get_processed()

        if processed_frame is None:
            # Wait until processing thread produces a frame
            time.sleep(0.005)
            continue

        debug_thread.update_data(processed_frame, hand_data, extra_info)
        # Defensive check for frame validity
        if not isinstance(processed_frame, np.ndarray) or processed_frame.ndim != 3:
            print(f"[Warning] Invalid frame type or shape detected:")
            print(f"Type: {type(processed_frame)}")
            print(f"Shape/Attributes: {getattr(processed_frame, 'shape', 'N/A')}")
            time.sleep(0.01)
            continue

        
        debug_frame = debug_thread.get_debug_frame()


        if debug_frame is not None and debug_frame.size > 0:
            cv2.imshow("Hand Gesture Control", debug_frame)
        else:
            print("Warning: Empty frame received for display")
        if cv2.waitKey(1) & 0xFF == 27:
            break

    processing_thread.stop()
    processing_thread.join()
    cap.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
