import threading
import time
import logging

log = logging.getLogger("pipeline")

class MockDB:
    def summary(self):
        return {
            "total_vehicles": 1420,
            "total_violations": 42,
            "total_plates": 890
        }
    def counts_by_category(self):
        return {"car": 850, "truck": 210, "bike": 310, "bus": 50}
    def hourly_counts(self, hours=24):
        return [10, 20, 15, 30, 45, 60, 55, 40, 35, 20, 25, 30]
    def recent_violations(self, limit=20):
        return [{"id": 1, "type": "Speeding", "vehicle": "Car", "time": "Just now"}]

class Pipeline:
    def __init__(self, config):
        self.config = config
        self.db = MockDB()
        self.running = False

    def start_async(self):
        self.running = True
        log.info("Mock Analytics Pipeline started successfully.")

    def get_latest_frame(self):
        # UI testing ke liye dummy blank frame return karega (agar cv2 installed hai)
        try:
            import numpy as np
            import cv2
            img = np.zeros((480, 640, 3), np.uint8)
            cv2.putText(img, "Live Road Analytics Stream", (120, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            return img
        except ImportError:
            return None

    def get_stats(self):
        return {
            "count_up": 12,
            "count_down": 8,
            "total": 20,
            "density_state": "Normal",
            "occupancy": 35.5,
            "fps": 29.7
        }