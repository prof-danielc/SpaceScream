"""
SpaceScream — Debug Overlay Module
Toggleable emotion bar display (FR-013, FR-021).
"""
import pygame
from settings import EMOTION_KEYS, EMOTION_COLORS, FACE_DETECTED_IDX, WHITE, BLACK, LIGHT_GRAY


class DebugOverlay:
    def __init__(self):
        self.visible = False
        self.font = None
        self.small_font = None

    def toggle(self):
        self.visible = not self.visible

    def init_fonts(self):
        self.font = pygame.font.SysFont("consolas", 16, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 13)

    def draw(self, surface, emotion_data, is_ready):
        """Draw debug overlay with emotion bars.
        
        Args:
            surface: Pygame surface to draw on
            emotion_data: numpy array of shape (9,) from EmotionEngine
            is_ready: bool — whether the emotion engine has completed initialization
        """
        if not self.visible:
            return

        if not self.font:
            self.init_fonts()

        # Panel dimensions
        panel_x = 15
        panel_y = 15
        panel_w = 260
        bar_h = 18
        spacing = 24
        padding = 12

        panel_h = padding * 2 + len(EMOTION_KEYS) * spacing + 35

        # Semi-transparent background
        overlay = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (panel_x, panel_y))

        # Border
        pygame.draw.rect(surface, (80, 80, 120), (panel_x, panel_y, panel_w, panel_h), 1)

        # Title
        title = self.font.render("EMOTION DEBUG", True, WHITE)
        surface.blit(title, (panel_x + padding, panel_y + 6))

        # Status indicator
        if not is_ready:
            # FR-021: Show "Initializing camera..." during FER model load
            status = self.small_font.render("Initializing camera...", True, (255, 200, 50))
            surface.blit(status, (panel_x + padding, panel_y + 28))
            return

        face_detected = emotion_data[FACE_DETECTED_IDX] > 0.5 if emotion_data is not None else False

        if not face_detected:
            status = self.small_font.render("No face detected", True, (255, 100, 100))
            surface.blit(status, (panel_x + padding, panel_y + 28))

        # Draw emotion bars
        y_offset = panel_y + 48

        for i, key in enumerate(EMOTION_KEYS):
            y = y_offset + i * spacing
            color = EMOTION_COLORS.get(key, LIGHT_GRAY)
            value = emotion_data[i] if emotion_data is not None else 0.0

            # Label
            label = self.small_font.render(f"{key:>8s}", True, LIGHT_GRAY)
            surface.blit(label, (panel_x + padding, y))

            # Bar background
            bar_x = panel_x + padding + 80
            bar_w = panel_w - padding * 2 - 120
            pygame.draw.rect(surface, (40, 40, 50), (bar_x, y + 2, bar_w, bar_h - 4))

            # Bar fill
            fill_w = int(bar_w * min(1.0, max(0.0, value)))
            if fill_w > 0:
                pygame.draw.rect(surface, color, (bar_x, y + 2, fill_w, bar_h - 4))

            # Value text
            val_text = self.small_font.render(f"{value:.2f}", True, WHITE)
            surface.blit(val_text, (bar_x + bar_w + 5, y))
