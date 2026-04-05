"""
SpaceScream — HUD Face Module
Vector-drawn digital face that reflects player emotions (FR-010, FR-011, FR-017).
Procedural rendering using Pygame primitives — with holographic and glitch effects.
"""
import math
import random
import pygame
from settings import (
    EMOTION_KEYS, EMOTION_IDX,
    FACE_SKIN, FACE_SKIN_ANGRY, FACE_SKIN_FEAR, FACE_SKIN_DAMAGE,
    FACE_EYE_WHITE, FACE_PUPIL, FACE_MOUTH, FACE_EYEBROW,
    FACE_TRANSITION_SPEED, DAMAGE_FLASH_DURATION,
    HOLO_CYAN, HOLO_BLUE, HOLO_RED, HOLO_GLOW_ALPHA,
    SCANLINE_SPACING, GLITCH_MAX_OFFSET,
)


# Emotion geometry parameters: control points for each expression
# Format: {mouth_curve, eyebrow_angle, eye_height, pupil_dy, skin_color}
EMOTION_PARAMS = {
    "neutral":  {"mouth_curve": 0.0,  "brow_angle": 0,   "eye_h": 1.0, "pupil_dy": 0, "skin": HOLO_BLUE},
    "happy":    {"mouth_curve": 0.5,  "brow_angle": -5,  "eye_h": 0.85, "pupil_dy": 0, "skin": HOLO_CYAN},
    "sad":      {"mouth_curve": -0.4, "brow_angle": 15,  "eye_h": 0.8, "pupil_dy": 2, "skin": HOLO_BLUE},
    "angry":    {"mouth_curve": -0.2, "brow_angle": -20, "eye_h": 0.7, "pupil_dy": 0, "skin": HOLO_RED},
    "surprise": {"mouth_curve": 0.0,  "brow_angle": 15,  "eye_h": 1.4, "pupil_dy": -1, "skin": HOLO_CYAN},
    "fear":     {"mouth_curve": -0.1, "brow_angle": 20,  "eye_h": 1.3, "pupil_dy": 1, "skin": HOLO_BLUE},
    "disgust":  {"mouth_curve": -0.3, "brow_angle": -10, "eye_h": 0.7, "pupil_dy": 0, "skin": HOLO_BLUE},
    "damage":   {"mouth_curve": -0.5, "brow_angle": -25, "eye_h": 0.5, "pupil_dy": 0, "skin": HOLO_RED},
    "low_health": {"mouth_curve": -0.3, "brow_angle": 18, "eye_h": 1.1, "pupil_dy": 1, "skin": HOLO_RED},
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
        
        # Aesthetic effects state
        self.glitch_timer = 0.0
        self.glitch_intensity = 0.0
        self.flicker_t = 0.0

    def set_emotion(self, emotion_name):
        """Set target emotion for smooth transition (FR-011)."""
        if emotion_name == self.target_emotion:
            return
        self._prev_params = dict(self.current_params)
        self.target_emotion = emotion_name
        self.blend_t = 0.0
        
        # Minimal glitch burst on shift (US 4)
        self.glitch_timer = 0.1
        self.glitch_intensity = 0.3

    def trigger_damage(self):
        """Flash damage face override (FR-012) and glitch."""
        self.damage_timer = DAMAGE_FLASH_DURATION
        self.glitch_timer = 0.4
        self.glitch_intensity = 1.0

    def set_low_health(self, is_low):
        self.low_health = is_low

    def update(self, dt):
        # Timers
        if self.damage_timer > 0:
            self.damage_timer -= dt
        if self.glitch_timer > 0:
            self.glitch_timer -= dt
        else:
            self.glitch_intensity *= 0.9  # Decay

        self.flicker_t += dt * 10
        
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
        """Draw the holographic face with glitches. (US 1 & 4)"""
        p = self.current_params
        r = size // 2
        
        # Flicker base opacity
        base_alpha = 180 + int(math.sin(self.flicker_t) * 30)
        if self.glitch_timer > 0:
            base_alpha = random.randint(100, 255)
            
        # ─── Glitch Offsets (US 4) ────────────────────────
        dx, dy = 0, 0
        if self.glitch_timer > 0:
            dx = random.randint(-GLITCH_MAX_OFFSET, GLITCH_MAX_OFFSET) * self.glitch_intensity
            dy = random.randint(-GLITCH_MAX_OFFSET, GLITCH_MAX_OFFSET) * self.glitch_intensity
            
        # Draw layers for color separation effect on heavy glitch
        if self.glitch_intensity > 0.5:
            self._render_face_instance(surface, cx + dx + 2, cy + dy, size, base_alpha // 2, color_override=HOLO_RED)
            self._render_face_instance(surface, cx + dx - 2, cy + dy, size, base_alpha // 2, color_override=HOLO_CYAN)

        self._render_face_instance(surface, cx + dx, cy + dy, size, base_alpha)

    def _render_face_instance(self, surface, cx, cy, size, alpha, color_override=None):
        """Helper to draw the face components with optional color separation."""
        p = self.current_params
        r = size // 2

        # Final skin color
        skin_color = color_override if color_override else p["skin"]
        
        # Create a temp surface for alpha transparency
        temp_surf = pygame.Surface((size + 40, size + 40), pygame.SRCALPHA)
        tcx, tcy = (size + 40) // 2, (size + 40) // 2
        
        # ─── Hologram Glow (US 1) ────────────────────────
        for i in range(3):
            glow_r = r + (i + 1) * 4
            glow_alpha = HOLO_GLOW_ALPHA // (i + 1)
            pygame.draw.circle(temp_surf, skin_color + (glow_alpha,), (tcx, tcy), glow_r)

        # Head circle
        pygame.draw.circle(temp_surf, skin_color + (alpha,), (tcx, tcy), r)
        pygame.draw.circle(temp_surf, (180, 150, 120, alpha), (tcx, tcy), r, 2)

        # Eyes
        eye_spacing = r * 0.35
        eye_y = tcy - r * 0.15
        eye_w = r * 0.22
        eye_h_base = r * 0.18
        eye_h = eye_h_base * p["eye_h"]

        eye_rects = []
        for side in [-1, 1]:
            ex = tcx + side * eye_spacing
            eye_rect = pygame.Rect(ex - eye_w, eye_y - eye_h, eye_w * 2, eye_h * 2)
            eye_rects.append(eye_rect)
            
            pygame.draw.ellipse(temp_surf, FACE_EYE_WHITE + (alpha,), eye_rect)
            pygame.draw.ellipse(temp_surf, (100, 80, 60, alpha), eye_rect, 1)

            # Pupil
            pupil_r = max(2, int(eye_w * 0.5))
            pupil_y = int(eye_y + p["pupil_dy"])
            pygame.draw.circle(temp_surf, FACE_PUPIL + (alpha,), (int(ex), pupil_y), pupil_r)

        # Eyebrows
        brow_angle = p["brow_angle"]
        brow_y = eye_y - eye_h - r * 0.08
        brow_len = r * 0.28
        for side in [-1, 1]:
            bx = tcx + side * eye_spacing
            rad = math.radians(brow_angle * side)
            x1, y1 = bx - brow_len * math.cos(rad), brow_y - brow_len * math.sin(rad)
            x2, y2 = bx + brow_len * math.cos(rad), brow_y + brow_len * math.sin(rad)
            pygame.draw.line(temp_surf, FACE_EYEBROW + (alpha,), (int(x1), int(y1)), (int(x2), int(y2)), max(1, r // 12))

        # Mouth
        mouth_y, mouth_w = tcy + r * 0.35, r * 0.4
        curve = p["mouth_curve"]
        segments = 12
        points = []
        for i in range(segments + 1):
            t = i / segments
            mx = tcx - mouth_w + 2 * mouth_w * t
            offset = curve * r * 0.3
            my = mouth_y + offset * 4 * t * (1 - t)
            points.append((int(mx), int(my)))
        if len(points) > 1:
            pygame.draw.lines(temp_surf, FACE_MOUTH + (alpha,), False, points, max(1, r // 10))

        # ─── Scanlines (US 1) (Do not cover eyes!) ────────
        self._draw_scanlines(temp_surf, tcx, tcy, r, eye_rects, alpha // 6)

        surface.blit(temp_surf, (cx - tcx, cy - tcy))

    def _draw_scanlines(self, surface, cx, cy, r, eye_rects, alpha):
        """Draw holographic scanlines skipping the eye regions."""
        for y in range(cy - r, cy + r, SCANLINE_SPACING):
            # Check if y is within the eye ocular region (vertical)
            eye_region = any(rect.top - 2 <= y <= rect.bottom + 2 for rect in eye_rects)
            
            # Intersection of y-line with circle (simple width calculation)
            dy = abs(y - cy)
            if dy >= r: continue
            half_w = int(math.sqrt(r*r - dy*dy))
            
            if eye_region:
                # Split line to avoid eyes
                # Assume eye regions are centered around cx +- eye_spacing
                # We can just skip the eyes entirely or draw segments
                # For simplicity, if we are in eye y-height, we draw from edge until eye_x_start
                # Left part
                left_eye_x = eye_rects[0].left
                right_eye_x = eye_rects[1].right
                
                # Line segment from cx-half_w to left_eye_x-2
                if cx - half_w < left_eye_x - 2:
                    pygame.draw.line(surface, (255, 255, 255, alpha), 
                                     (cx - half_w, y), (left_eye_x - 2, y), 1)
                # Middle part (between eyes)
                if eye_rects[0].right + 2 < eye_rects[1].left - 2:
                    pygame.draw.line(surface, (255, 255, 255, alpha), 
                                     (eye_rects[0].right + 2, y), (eye_rects[1].left - 2, y), 1)
                # Right part
                if right_eye_x + 2 < cx + half_w:
                    pygame.draw.line(surface, (255, 255, 255, alpha), 
                                     (right_eye_x + 2, y), (cx + half_w, y), 1)
            else:
                # Full line inside circle
                pygame.draw.line(surface, (255, 255, 255, alpha), (cx - half_w, y), (cx + half_w, y), 1)
