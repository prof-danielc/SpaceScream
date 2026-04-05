"""
SpaceScream — Main Entry Point
Game loop, input handling, and system integration.
Two threads: main game thread (consumer) + emotion producer thread (FR-018).
"""
import sys
import pygame
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
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE | pygame.SCALED)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    fullscreen = False

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

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
                    else:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE | pygame.SCALED)

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

        # ─── Draw ─────────────────────────────────────────
        screen.fill(BLACK)

        # Play area clip
        play_rect = pygame.Rect(0, 0, SCREEN_WIDTH, PLAY_AREA_HEIGHT)
        screen.set_clip(play_rect)

        # Draw game (stars, particles, asteroids, bullets, ship)
        game.draw(screen)

        # Game Over overlay
        if game.game_over:
            # Dim the play area
            dim = pygame.Surface((SCREEN_WIDTH, PLAY_AREA_HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 140))
            screen.blit(dim, (0, 0))

            # GAME OVER text
            go_text = font_large.render("GAME OVER", True, RED)
            go_rect = go_text.get_rect(center=(SCREEN_WIDTH // 2, PLAY_AREA_HEIGHT // 2 - 30))
            screen.blit(go_text, go_rect)

            # Score
            score_text = font_medium.render(f"Final Score: {game.score:,}", True, YELLOW)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, PLAY_AREA_HEIGHT // 2 + 20))
            screen.blit(score_text, score_rect)

            # Wave
            wave_text = font_small.render(f"Reached Wave {game.wave}", True, WHITE)
            wave_rect = wave_text.get_rect(center=(SCREEN_WIDTH // 2, PLAY_AREA_HEIGHT // 2 + 50))
            screen.blit(wave_text, wave_rect)

            # Restart prompt
            restart_text = font_small.render("Press any key to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, PLAY_AREA_HEIGHT // 2 + 85))
            screen.blit(restart_text, restart_rect)

        # Reset clip for HUD
        screen.set_clip(None)

        # Draw HUD
        hud.draw(screen, game.score, game.ship.lives, game.wave)

        # Debug overlay (on top of everything)
        debug.draw(screen, emotion_data, emotion.is_ready)

        # FPS counter (tiny, top-right)
        fps_text = font_small.render(f"FPS: {int(clock.get_fps())}", True, (80, 80, 80))
        screen.blit(fps_text, (SCREEN_WIDTH - 90, 5))

        pygame.display.flip()

    # Cleanup
    emotion.stop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
