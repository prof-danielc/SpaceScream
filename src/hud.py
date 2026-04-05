"""
SpaceScream — HUD Module
Bottom-of-screen status bar with score, lives, and emotion face.
"""
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PLAY_AREA_HEIGHT, HUD_HEIGHT,
    HUD_BG, HUD_BORDER, WHITE, CYAN, YELLOW, RED, SHIP_SIZE,
)
from hud_face import HUDFace


class HUD:
    def __init__(self):
        self.face = HUDFace()
        self.font = None
        self.small_font = None

    def init_fonts(self):
        """Initialize fonts after pygame.init()."""
        self.font = pygame.font.SysFont("consolas", 22, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 14)

    def update(self, dt, emotion_data, damage_event, lives):
        """Update HUD components."""
        self.face.set_low_health(lives <= 1)
        if damage_event:
            self.face.trigger_damage()
        self.face.update(dt, emotion_data)

    def draw(self, surface, score, lives, wave):
        """Draw the full HUD bar at the bottom of the screen."""
        hud_y = PLAY_AREA_HEIGHT

        # Background
        hud_rect = pygame.Rect(0, hud_y, SCREEN_WIDTH, HUD_HEIGHT)
        pygame.draw.rect(surface, HUD_BG, hud_rect)
        pygame.draw.line(surface, HUD_BORDER, (0, hud_y), (SCREEN_WIDTH, hud_y), 2)

        if not self.font:
            self.init_fonts()

        # Score (left side)
        score_text = self.font.render(f"SCORE: {score:,}", True, YELLOW)
        surface.blit(score_text, (20, hud_y + 12))

        # Wave indicator
        wave_text = self.small_font.render(f"WAVE {wave}", True, WHITE)
        surface.blit(wave_text, (20, hud_y + 42))

        # Lives (right side) — draw small ship icons
        lives_label = self.small_font.render("LIVES:", True, WHITE)
        label_x = SCREEN_WIDTH - 180
        surface.blit(lives_label, (label_x, hud_y + 12))

        for i in range(lives):
            ix = label_x + 55 + i * 25
            iy = hud_y + 18
            # Mini ship triangle
            verts = [
                (ix, iy - 8),
                (ix - 5, iy + 5),
                (ix + 5, iy + 5),
            ]
            pygame.draw.polygon(surface, CYAN, verts, 0)

        # Face (center)
        face_cx = SCREEN_WIDTH // 2
        face_cy = hud_y + HUD_HEIGHT // 2
        face_size = int(HUD_HEIGHT * 0.85)
        self.face.draw(surface, face_cx, face_cy, face_size)

        # Face frame - Digital terminal brackets [ ]
        frame_r = face_size // 2 + 8
        b_len = 15  # Bracket segment length
        
        # Corners [top-left, top-right, bottom-left, bottom-right]
        for sx, sy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            px, py = face_cx + sx * frame_r, face_cy + sy * frame_r
            # Draw L-shaped corner
            pygame.draw.line(surface, HUD_BORDER, (px, py), (px - sx * b_len, py), 2)
            pygame.draw.line(surface, HUD_BORDER, (px, py), (px, py - sy * b_len), 2)

