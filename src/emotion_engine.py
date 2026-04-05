"""
SpaceScream — Emotion Engine (Producer Thread)
Webcam capture + FER analysis in a background thread.
Communicates with the main game thread via shared numpy array (FR-018, FR-019).
Uses double-buffering: expensive work outside lock, swap under lock.
"""
import threading
import time
import numpy as np

from settings import EMOTION_KEYS, EMOTION_ARRAY_SIZE, FACE_DETECTED_IDX, TIMESTAMP_IDX, FACE_LOST_DECAY_TIME, FACE_DECAY_RATE


class EmotionEngine:
    """Producer/consumer emotion system using shared numpy array."""

    def __init__(self):
        # Shared front buffer — consumer reads this
        self._front_buffer = np.zeros(EMOTION_ARRAY_SIZE, dtype=np.float64)
        self._front_buffer[6] = 1.0  # neutral = 1.0 default

        self._lock = threading.Lock()
        self._running = False
        self._thread = None
        self.is_ready = False  # FR-021: False until first successful read
        self.webcam_available = False
        self._last_face_time = 0.0

    def start(self):
        """Start the producer thread."""
        self._running = True
        self._thread = threading.Thread(target=self._producer_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Signal the producer thread to stop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def get_emotions(self):
        """Consumer read: acquire lock, copy front buffer, release (FR-019)."""
        with self._lock:
            return self._front_buffer.copy()

    def get_dominant_emotion(self):
        """Return the name of the dominant emotion."""
        data = self.get_emotions()
        emotion_scores = data[:7]
        idx = int(np.argmax(emotion_scores))
        return EMOTION_KEYS[idx]

    def _producer_loop(self):
        """Producer thread: capture webcam, run FER, write to shared array (FR-018, FR-019, FR-021)."""
        import cv2

        # Try to open webcam
        cap = None
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("[EmotionEngine] No webcam found — using neutral fallback.")
                self.webcam_available = False
                self.is_ready = True
                return
            self.webcam_available = True
        except Exception as e:
            print(f"[EmotionEngine] Webcam init error: {e} — using neutral fallback.")
            self.webcam_available = False
            self.is_ready = True
            return

        # Initialize FER (FR-021: this happens entirely on producer thread)
        fer_detector = None
        try:
            from fer.fer import FER
            fer_detector = FER(mtcnn=False)  # Use default OpenCV cascade (faster)
            print("[EmotionEngine] FER model loaded successfully.")
        except Exception as e:
            print(f"[EmotionEngine] FER init error: {e} — using neutral fallback.")
            self.is_ready = True
            if cap:
                cap.release()
            return

        self.is_ready = True
        self._last_face_time = time.time()

        while self._running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.05)
                continue

            # --- EXPENSIVE WORK OUTSIDE LOCK (FR-019) ---
            back_buffer = np.zeros(EMOTION_ARRAY_SIZE, dtype=np.float64)
            back_buffer[6] = 1.0  # default neutral
            
            try:
                results = fer_detector.detect_emotions(frame)
                if results and len(results) > 0:
                    # Use the first/largest face
                    emotions = results[0]["emotions"]
                    for i, key in enumerate(EMOTION_KEYS):
                        back_buffer[i] = emotions.get(key, 0.0)
                    back_buffer[FACE_DETECTED_IDX] = 1.0
                    back_buffer[TIMESTAMP_IDX] = time.time()
                    self._last_face_time = time.time()
                else:
                    # No face detected
                    back_buffer[FACE_DETECTED_IDX] = 0.0
                    back_buffer[TIMESTAMP_IDX] = time.time()

                    # Hold the last face (DEPRECATED)
                    with self._lock:
                        prev = self._front_buffer.copy()
                    back_buffer[:7] = prev[:7]

                    # Face-lost decay (FR: decay toward neutral after timeout)
                    elapsed = time.time() - self._last_face_time
                    if elapsed > FACE_LOST_DECAY_TIME:
                        # Decay is applied to the previous front buffer values
                        decay = FACE_DECAY_RATE * 0.1  # per-iteration decay
                        for i in range(7):
                            target = 1.0 if i == 6 else 0.0  # decay toward neutral
                            prev[i] += (target - prev[i]) * decay
                        back_buffer[:7] = prev[:7]

            except Exception:
                back_buffer[6] = 1.0  # fallback to neutral on any error

            # --- ATOMIC SWAP UNDER LOCK (FR-019) ---
            with self._lock:
                self._front_buffer, back_buffer = back_buffer, self._front_buffer

            # Throttle to ~10 FPS for CV
            time.sleep(0.05)

        if cap:
            cap.release()
