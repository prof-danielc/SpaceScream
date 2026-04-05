# SpaceScream — Architecture

## Overview

Emotion-driven Asteroids game using Pygame, OpenCV, and FER. Two-thread producer/consumer architecture.

## Project Structure

```
SpaceScream/
├── src/
│   ├── main.py              # Entry point — game loop, input, system integration
│   ├── settings.py          # All constants, colors, physics tunables, utilities
│   ├── ship.py              # Ship entity — thrust, rotate, strafe, safe respawn
│   ├── bullet.py            # Bullet entity — velocity, lifetime, wrapping
│   ├── asteroid.py          # Asteroid entity — splitting (FR-022), irregular polygons
│   ├── game.py              # Game state — collisions, waves, particles, stars
│   ├── emotion_engine.py    # Webcam + FER producer thread, numpy shared array
│   ├── hud.py               # HUD bar — score, lives, face frame
│   ├── hud_face.py          # Vector-drawn face with emotion interpolation
│   └── debug_overlay.py     # D-key toggled emotion bars overlay
├── assets/
│   └── fonts/               # (Optional — using pygame defaults)
├── specs/1-space-scream/    # Spec-Kit artifacts
├── requirements.txt
└── .gitignore
```

## Threading Model (FR-018/019)

```
Main Thread (Consumer)              Producer Thread
┌──────────────────────┐           ┌──────────────────────┐
│ Game Loop (60 FPS)   │           │ Webcam + FER (~10Hz) │
│ - Input handling     │           │ - cv2.VideoCapture   │
│ - Physics update     │  ┌─────┐ │ - FER.detect_emotions│
│ - Collision detect   │◄─│numpy│◄│ - Write back buffer  │
│ - HUD/Face render    │  │array│ │ - Swap under lock    │
│ - Debug overlay      │  └─────┘ │                      │
└──────────────────────┘           └──────────────────────┘
          reads (copy)                   writes (swap)
          Lock held: µs                  Lock held: µs
```

## Key Design Decisions

1. **Vector-only graphics** (FR-017) — All visuals use `pygame.draw.*` primitives
2. **Double-buffered emotions** (FR-019) — Lock only held during array swap, never during FER inference
3. **Safe respawn** (FR-020) — Ship delays spawn until center is clear of asteroids
4. **Spread split** (FR-022) — Child asteroids spread 90-120° apart with radial offset
5. **Lazy FER init** (FR-021) — Game starts immediately, FER loads on producer thread
