"""
SpaceScream — HUD Face Module
Vector-drawn digital face that reflects player emotions (FR-010, FR-011, FR-017).
Procedural rendering using Pygame primitives — no image assets.
"""
import math
import pygame
from settings import (
    EMOTION_KEYS, EMOTION_IDX,
    FACE_SKIN, FACE_SKIN_ANGRY, FACE_SKIN_FEAR, FACE_SKIN_DAMAGE,
    FACE_EYE_WHITE, FACE_PUPIL, FACE_MOUTH, FACE_EYEBROW,
    FACE_TRANSITION_SPEED, DAMAGE_FLASH_DURATION,
)


# Emotion geometry parameters: control points for each expression
# Format: {mouth_curve, eyebrow_angle, eye_height, pupil_dy, skin_color}
EMOTION_PARAMS = {
    "neutral":  {"mouth_curve": 0.0,  "brow_angle": 0,   "eye_h": 1.0, "pupil_dy": 0, "skin": FACE_SKIN},
    "happy":    {"mouth_curve": 0.5,  "brow_angle": -5,  "eye_h": 0.85, "pupil_dy": 0, "skin": FACE_SKIN},
    "sad":      {"mouth_curve": -0.4, "brow_angle": 15,  "eye_h": 0.8, "pupil_dy": 2, "skin": FACE_SKIN},
    "angry":    {"mouth_curve": -0.2, "brow_angle": -20, "eye_h": 0.7, "pupil_dy": 0, "skin": FACE_SKIN_ANGRY},
    "surprise": {"mouth_curve": 0.0,  "brow_angle": 15,  "eye_h": 1.4, "pupil_dy": -1, "skin": FACE_SKIN},
    "fear":     {"mouth_curve": -0.1, "brow_angle": 20,  "eye_h": 1.3, "pupil_dy": 1, "skin": FACE_SKIN_FEAR},
    "disgust":  {"mouth_curve": -0.3, "brow_angle": -10, "eye_h": 0.7, "pupil_dy": 0, "skin": FACE_SKIN},
    "damage":   {"mouth_curve": -0.5, "brow_angle": -25, "eye_h": 0.5, "pupil_dy": 0, "skin": FACE_SKIN_DAMAGE},
    "low_health": {"mouth_curve": -0.3, "brow_angle": 18, "eye_h": 1.1, "pupil_dy": 1, "skin": FACE_SKIN_FEAR},
}


def _lerp(a, b, t):
    return a + (b - a) * t


def _lerp_color(c1, c2, t):
    return (
        int(_lerp(c1[0], c2[0], t)),
        int(_lerp(c1[1], c2[1], t)),
        int(_lerp(c1[2], c2[2], t)),
    )


class HUDFace:
    def __init__(self):
        self.current_params = dict(EMOTION_PARAMS["neutral"])
        self.target_emotion = "neutral"
        self.blend_t = 1.0
        self.damage_timer = 0.0
        self.low_health = False
        self._prev_params = dict(EMOTION_PARAMS["neutral"])

    def set_emotion(self, emotion_name):
        """Set target emotion for smooth transition (FR-011)."""
        if emotion_name == self.target_emotion:
            return
        self._prev_params = dict(self.current_params)
        self.target_emotion = emotion_name
        self.blend_t = 0.0

    def trigger_damage(self):
        """Flash damage face override (FR-012)."""
        self.damage_timer = DAMAGE_FLASH_DURATION

    def set_low_health(self, is_low):
        self.low_health = is_low

    def update(self, dt):
        # Advance damage timer
        if self.damage_timer > 0:
            self.damage_timer -= dt

        # Advance transition blend
        if self.blend_t < 1.0:
            self.blend_t = min(1.0, self.blend_t + FACE_TRANSITION_SPEED * dt)

        # Determine target params
        if self.damage_timer > 0:
            target = EMOTION_PARAMS["damage"]
        elif self.low_health:
            # Blend between camera emotion and low_health worry
            base = EMOTION_PARAMS.get(self.target_emotion, EMOTION_PARAMS["neutral"])
            worry = EMOTION_PARAMS["low_health"]
            target = {}
            for key in base:
                if key == "skin":
                    target[key] = _lerp_color(base[key], worry[key], 0.5)
                else:
                    target[key] = _lerp(base[key], worry[key], 0.5)
        else:
            target = EMOTION_PARAMS.get(self.target_emotion, EMOTION_PARAMS["neutral"])

        # Interpolate current params toward target
        t = self.blend_t
        for key in self.current_params:
            if key == "skin":
                self.current_params[key] = _lerp_color(self._prev_params[key], target[key], t)
            else:
                self.current_params[key] = _lerp(self._prev_params[key], target[key], t)

    def draw(self, surface, cx, cy, size):
        """Draw the vector face at center (cx, cy) with given size.
        
        All rendering uses pygame.draw primitives per FR-017.
        """
        p = self.current_params
        r = size // 2

        # Head circle
        skin_color = p["skin"] if isinstance(p["skin"], tuple) else FACE_SKIN
        pygame.draw.circle(surface, skin_color, (cx, cy), r)
        pygame.draw.circle(surface, (180, 150, 120), (cx, cy), r, 2)

        # Eyes
        eye_spacing = r * 0.35
        eye_y = cy - r * 0.15
        eye_w = r * 0.22
        eye_h_base = r * 0.18
        eye_h = eye_h_base * p["eye_h"]

        for side in [-1, 1]:
            ex = cx + side * eye_spacing
            # Eye white (ellipse via rect)
            eye_rect = pygame.Rect(
                ex - eye_w, eye_y - eye_h,
                eye_w * 2, eye_h * 2
            )
            pygame.draw.ellipse(surface, FACE_EYE_WHITE, eye_rect)
            pygame.draw.ellipse(surface, (100, 80, 60), eye_rect, 1)

            # Pupil
            pupil_r = max(2, int(eye_w * 0.5))
            pupil_y = int(eye_y + p["pupil_dy"])
            pygame.draw.circle(surface, FACE_PUPIL, (int(ex), pupil_y), pupil_r)

        # Eyebrows
        brow_angle = p["brow_angle"]
        brow_y = eye_y - eye_h - r * 0.08
        brow_len = r * 0.28

        for side in [-1, 1]:
            bx = cx + side * eye_spacing
            rad = math.radians(brow_angle * side)
            x1 = bx - brow_len * math.cos(rad)
            y1 = brow_y - brow_len * math.sin(rad)
            x2 = bx + brow_len * math.cos(rad)
            y2 = brow_y + brow_len * math.sin(rad)
            pygame.draw.line(surface, FACE_EYEBROW, (int(x1), int(y1)), (int(x2), int(y2)), max(1, r // 12))

        # Mouth (arc approximation using line segments)
        mouth_y = cy + r * 0.35
        mouth_w = r * 0.4
        curve = p["mouth_curve"]  # positive = smile, negative = frown
        segments = 12
        points = []
        for i in range(segments + 1):
            t = i / segments
            mx = cx - mouth_w + 2 * mouth_w * t
            # Parabolic curve
            offset = curve * r * 0.3
            my = mouth_y + offset * 4 * t * (1 - t)
            points.append((int(mx), int(my)))

        if len(points) > 1:
            pygame.draw.lines(surface, FACE_MOUTH, False, points, max(1, r // 10))

        # Nose (small line)
        nose_len = r * 0.1
        pygame.draw.line(surface, (160, 130, 100),
                         (cx, int(cy + r * 0.05)),
                         (cx, int(cy + r * 0.05 + nose_len)), 1)
