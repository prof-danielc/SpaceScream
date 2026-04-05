# 🚀 SpaceScream

In space, no one can hear you scream.

An emotion-driven Asteroids game that reads your face through the webcam and mirrors your emotions on a Doom-style HUD face — all rendered with vector graphics.

## Features

- **Classic Asteroids Gameplay** — Thrust, rotate, strafe, shoot, and survive through escalating waves of asteroids
- **Real-Time Emotion Recognition** — Your webcam captures your face and the [FER](https://github.com/justinshenk/fer) library detects 7 emotions (happy, sad, angry, surprise, fear, disgust, neutral)
- **HUD Emotion Face** — A vector-drawn digital face in the HUD reacts to your real emotions, Doom-style. It also flashes on damage and looks worried at low health
- **Debug Overlay** — Toggle a real-time emotion bar chart to see exactly what the system detects
- **Vector Graphics** — Every visual element (ship, asteroids, bullets, HUD, face) is drawn with Pygame primitives — no image assets
- **Two-Thread Architecture** — Emotion analysis runs on a dedicated producer thread with double-buffered numpy arrays, so the game never stutters

## Requirements

- **Python 3.x** (tested with Anaconda 3, base environment)
- **Webcam** (optional — game works without one, emotion features fall back to neutral)
- OS: **Windows** (tested), should work on macOS/Linux with minor path adjustments

## Installation

```bash
# Clone or download the project
cd SpaceScream

# Install dependencies (using Anaconda 3 base environment)
pip install -r requirements.txt
```

Dependencies: `pygame`, `opencv-python`, `fer`, `numpy`

## Running the Game

```bash
# Using Anaconda 3 on Windows:
& "C:\Users\Daniel\anaconda3\python.exe" src/main.py

# Or if Python is in your PATH:
python src/main.py
```

## Controls

| Key | Action |
|-----|--------|
| **↑** (Up Arrow) | Thrust forward |
| **↓** (Down Arrow) | Thrust backward / brake |
| **←** (Left Arrow) | Rotate counter-clockwise |
| **→** (Right Arrow) | Rotate clockwise |
| **Q** | Strafe left |
| **E** | Strafe right |
| **Space** | Fire bullet (hold for continuous fire, capped at 5/sec) |
| **D** | Toggle debug emotion overlay |
| **F10** | Toggle maximized screen |
| **F11** | Toggle fullscreen |
| **Escape** | Quit game |

## Gameplay

- Destroy asteroids by shooting them. Large asteroids split into medium, medium into small, small are destroyed completely.
- Avoid collisions — you start with **3 lives**. Getting hit costs one life and the ship respawns at center once the area is clear.
- Each wave cleared spawns more and faster asteroids.
- **Scoring**: Large = 20 pts, Medium = 50 pts, Small = 100 pts.

## Emotion System

The game uses your webcam to detect facial expressions in real time:

1. **Producer thread** captures webcam frames and runs FER emotion analysis (~10 Hz)
2. Results are written to a shared **numpy array** protected by a lock (held only during the swap — microseconds)
3. The **main game thread** reads the array each frame and drives the HUD face + debug overlay

If no webcam is detected, the game starts normally with the face defaulting to neutral.  
If FER is still loading at launch, the debug overlay shows *"Initializing camera..."* until ready.

## Project Structure

```
SpaceScream/
├── src/
│   ├── main.py              # Entry point — game loop, input handling
│   ├── settings.py          # Constants, colors, physics tunables
│   ├── ship.py              # Ship — thrust, rotate, strafe, safe respawn
│   ├── bullet.py            # Bullet — velocity, lifetime, screen wrapping
│   ├── asteroid.py          # Asteroid — splitting with spread angle, irregular polygons
│   ├── game.py              # Game state — collisions, waves, particles, stars
│   ├── emotion_engine.py    # Webcam + FER producer thread, numpy shared array
│   ├── hud.py               # HUD bar — score, wave, lives, face frame
│   ├── hud_face.py          # Vector-drawn face with 9 emotion states
│   └── debug_overlay.py     # D-key toggled emotion bars overlay
├── assets/fonts/            # (Reserved — currently using Pygame defaults)
├── specs/                   # Spec-Kit design artifacts
├── requirements.txt
├── ARCHITECTURE.md
└── README.md
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Daniel Cavalcanti Jeronymo <danielc@utfpr.edu.br>
