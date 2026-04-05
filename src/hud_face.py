"""
SpaceScream — HUD Face Module
Vector-drawn digital face that reflects player emotions (FR-010, FR-011, FR-017).
Procedural rendering using Pygame primitives — with holographic and glitch effects.
"""
import math
import random
import pygame
import numpy as np
from settings import (
    EMOTION_KEYS, EMOTION_IDX,
    FACE_SKIN, FACE_SKIN_ANGRY, FACE_SKIN_FEAR, FACE_SKIN_DAMAGE,
    FACE_EYE_WHITE, FACE_PUPIL, FACE_MOUTH, FACE_EYEBROW,
    FACE_TRANSITION_SPEED, DAMAGE_FLASH_DURATION,
    HOLO_CYAN, HOLO_BLUE, HOLO_RED, HOLO_GLOW_ALPHA,
    SCANLINE_SPACING, GLITCH_MAX_OFFSET,
    EMOTION_BLEND_DOMINANCE,
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

    def trigger_damage(self):
        """Flash damage face override (FR-012) and glitch."""
        self.damage_timer = DAMAGE_FLASH_DURATION
        self.glitch_timer = 0.4
        self.glitch_intensity = 1.0

    def set_low_health(self, is_low):
        self.low_health = is_low

    def update(self, dt, emotion_data):
        """Update face state-blending all detected emotions (US 5)."""
        # --- 1. Update Timers ---
        if self.damage_timer > 0:
            self.damage_timer -= dt
        if self.glitch_timer > 0:
            self.glitch_timer -= dt
        else:
            self.glitch_intensity *= 0.9  # Decay
        self.flicker_t += dt * 10
        
        # --- 2. Calculate Blended Target ---
        # scores: 7 floats in fixed order (happy, sad, angry, surprise, fear, disgust, neutral)
        scores = emotion_data[:7]
        total_score = np.sum(scores)
        if total_score > 0:
            scores = scores / total_score
        else:
            scores = np.zeros(7)
            scores[6] = 1.0 # default to neutral
            
        # A. Weighted Average of all 7 emotions
        weighted_target = {}
        first_key = EMOTION_KEYS[0]
        # Init weighted_target with first emotion scaled by score
        for param_key in EMOTION_PARAMS[first_key]:
            val = EMOTION_PARAMS[first_key][param_key]
            if param_key == "skin":
                weighted_target[param_key] = [val[0] * scores[0], val[1] * scores[0], val[2] * scores[0]]
            else:
                weighted_target[param_key] = val * scores[0]
                
        # Accumulate remaining emotions
        for i in range(1, 7):
            emo_key = EMOTION_KEYS[i]
            score = scores[i]
            params = EMOTION_PARAMS[emo_key]
            for param_key in params:
                val = params[param_key]
                if param_key == "skin":
                    weighted_target[param_key][0] += val[0] * score
                    weighted_target[param_key][1] += val[1] * score
                    weighted_target[param_key][2] += val[2] * score
                else:
                    weighted_target[param_key] += val * score
                    
        # B. Dominant Emotion Target
        dominant_idx = np.argmax(scores)
        dominant_params = EMOTION_PARAMS[EMOTION_KEYS[dominant_idx]]
        
        # Trigger internal glitch pulse if dominant emotion changed significantly
        if EMOTION_KEYS[dominant_idx] != self.target_emotion:
            self.target_emotion = EMOTION_KEYS[dominant_idx]
            self.glitch_timer = max(self.glitch_timer, 0.1)
            self.glitch_intensity = max(self.glitch_intensity, 0.3)
            
        # C. Final Target Merge (using configurable dominance)
        mid_target = {}
        for k in weighted_target:
            if k == "skin":
                mid_target[k] = _lerp_color(weighted_target[k], dominant_params[k], EMOTION_BLEND_DOMINANCE)
            else:
                mid_target[k] = _lerp(weighted_target[k], dominant_params[k], EMOTION_BLEND_DOMINANCE)

        # D. Add Low Health Overlay
        if self.damage_timer > 0:
            target = EMOTION_PARAMS["damage"]
        elif self.low_health:
            worry = EMOTION_PARAMS["low_health"]
            target = {}
            for k in mid_target:
                if k == "skin":
                    target[k] = _lerp_color(mid_target[k], worry[k], 0.5)
                else:
                    target[k] = _lerp(mid_target[k], worry[k], 0.5)
        else:
            target = mid_target

        # --- 3. Apply Temporal Smoothing (transition to target) ---
        # Instead of just snapping to target, we continue to lerp current_params toward target
        # for maximum fluid motion.
        for key in self.current_params:
            if key == "skin":
                self.current_params[key] = _lerp_color(self.current_params[key], target[key], FACE_TRANSITION_SPEED * dt)
            else:
                self.current_params[key] = _lerp(self.current_params[key], target[key], FACE_TRANSITION_SPEED * dt)

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
                left_eye_x = eye_rects[0].left
                right_eye_x = eye_rects[1].right
                if cx - half_w < left_eye_x - 2:
                    pygame.draw.line(surface, (255, 255, 255, alpha), 
                                     (cx - half_w, y), (left_eye_x - 2, y), 1)
                if eye_rects[0].right + 2 < eye_rects[1].left - 2:
                    pygame.draw.line(surface, (255, 255, 255, alpha), 
                                     (eye_rects[0].right + 2, y), (eye_rects[1].left - 2, y), 1)
                if right_eye_x + 2 < cx + half_w:
                    pygame.draw.line(surface, (255, 255, 255, alpha), 
                                     (right_eye_x + 2, y), (cx + half_w, y), 1)
            else:
                pygame.draw.line(surface, (255, 255, 255, alpha), (cx - half_w, y), (cx + half_w, y), 1)
