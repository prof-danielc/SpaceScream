"""
SpaceScream — Main Entry Point
Game loop, input handling, and system integration.
Two threads: main game thread (consumer) + emotion producer thread (FR-018).
"""
import sys
import pygame
from pygame._sdl2 import Window
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, BLACK, WHITE, YELLOW, RED,
    PLAY_AREA_HEIGHT,
)
from game import Game
from hud import HUD
from emotion_engine import EmotionEngine
from debug_overlay import DebugOverlay


def main():
    pygame.init()

    # Logical surface — all game rendering happens here at fixed resolution
    logical_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Actual display window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    fullscreen = False
    maximized = False
    window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)

    # Force maximize
    maximized = True
    Window.from_display_module().maximize()
    window_size = screen.get_size()

    # Core systems
    game = Game()
    hud = HUD()
    debug = DebugOverlay()

    # Emotion engine (producer thread — FR-018)
    emotion = EmotionEngine()
    emotion.start()

    # Game Over font
    font_large = pygame.font.SysFont("consolas", 48, bold=True)
    font_medium = pygame.font.SysFont("consolas", 22)
    font_small = pygame.font.SysFont("consolas", 16)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)  # cap delta to prevent physics explosion on lag

        # ─── Events ───────────────────────────────────────
        fire_pressed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                if not fullscreen:
                    window_size = (event.w, event.h)
                    screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_F10:
                    maximized = not maximized

                    if maximized:
                        Window.from_display_module().maximize()
                        window_size = screen.get_size()
                    else:
                        Window.from_display_module().restore()
                        window_size = screen.get_size()

                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        window_size = screen.get_size()
                    else:
                        window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
                        screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)

                elif event.key == pygame.K_d:
                    debug.toggle()

                elif event.key == pygame.K_SPACE:
                    if game.game_over:
                        game.restart()
                    else:
                        fire_pressed = True

                elif game.game_over and event.key:
                    game.restart()

        # Continuous fire while holding space
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not game.game_over:
            fire_pressed = True

        # ─── Update ───────────────────────────────────────
        game.update(dt, keys, fire_pressed)

        # Read emotion data from shared array (consumer — FR-018)
        emotion_data = emotion.get_emotions()
        dominant = emotion.get_dominant_emotion()

        # Update HUD
        hud.update(dt, dominant, game.damage_event, game.ship.lives)

        # ─── Draw (to logical surface at fixed 1024×768) ──
        logical_surface.fill(BLACK)

        # Play area clip
        play_rect = pygame.Rect(0, 0, SCREEN_WIDTH, PLAY_AREA_HEIGHT)
        logical_surface.set_clip(play_rect)

        # Draw game (stars, particles, asteroids, bullets, ship)
        game.draw(logical_surface)

        # Game Over overlay
        if game.game_over:
            # Dim the play area
            dim = pygame.Surface((SCREEN_WIDTH, PLAY_AREA_HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 140))
            logical_surface.blit(dim, (0, 0))

            # GAME OVER text
            go_text = font_large.render("GAME OVER", True, RED)
            go_rect = go_text.get_rect(center=(SCREEN_WIDTH // 2, PLAY_AREA_HEIGHT // 2 - 30))
            logical_surface.blit(go_text, go_rect)

            # Score
            score_text = font_medium.render(f"Final Score: {game.score:,}", True, YELLOW)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, PLAY_AREA_HEIGHT // 2 + 20))
            logical_surface.blit(score_text, score_rect)

            # Wave
            wave_text = font_small.render(f"Reached Wave {game.wave}", True, WHITE)
            wave_rect = wave_text.get_rect(center=(SCREEN_WIDTH // 2, PLAY_AREA_HEIGHT // 2 + 50))
            logical_surface.blit(wave_text, wave_rect)

            # Restart prompt
            restart_text = font_small.render("Press any key to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, PLAY_AREA_HEIGHT // 2 + 85))
            logical_surface.blit(restart_text, restart_rect)

        # Reset clip for HUD
        logical_surface.set_clip(None)

        # Draw HUD
        hud.draw(logical_surface, game.score, game.ship.lives, game.wave)

        # Debug overlay (on top of everything)
        debug.draw(logical_surface, emotion_data, emotion.is_ready)

        # FPS counter (tiny, top-right)
        fps_text = font_small.render(f"FPS: {int(clock.get_fps())}", True, (80, 80, 80))
        logical_surface.blit(fps_text, (SCREEN_WIDTH - 90, 5))

        # ─── Scale logical surface to actual window ───────
        screen.fill(BLACK)
        # Maintain aspect ratio
        win_w, win_h = window_size
        scale = min(win_w / SCREEN_WIDTH, win_h / SCREEN_HEIGHT)
        scaled_w = int(SCREEN_WIDTH * scale)
        scaled_h = int(SCREEN_HEIGHT * scale)
        offset_x = (win_w - scaled_w) // 2
        offset_y = (win_h - scaled_h) // 2

        scaled = pygame.transform.smoothscale(logical_surface, (scaled_w, scaled_h))
        screen.blit(scaled, (offset_x, offset_y))

        pygame.display.flip()

    # Cleanup
    emotion.stop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
