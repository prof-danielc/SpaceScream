# Implementation Plan: SpaceScream — Emotion-Driven Asteroids

**Branch**: `1-space-scream` | **Date**: 2026-04-05 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/1-space-scream/spec.md`

## Summary

Build a Python Asteroids-style game where real-time webcam emotion recognition drives a Doom/Wolfenstein-inspired HUD face. The game features full ship controls (thrust, rotate, strafe, fire), wave-based asteroid destruction gameplay, and a toggleable debug overlay to display raw emotion values. Emotion analysis runs in a background thread to maintain smooth gameplay.

## Technical Context

**Language/Version**: Python 3.x (Anaconda 3 — Base Environment)  
**Primary Dependencies**: `pygame` (game engine), `opencv-python` (webcam), `fer` (emotion recognition)  
**Storage**: N/A (no persistence required)  
**Testing**: Manual verification + optional `pytest` for physics unit tests  
**Target Platform**: Windows (desktop), webcam-equipped  
**Project Type**: Single project  
**Performance Goals**: ≥30 FPS with webcam + emotion analysis active; ≥60 FPS without webcam  
**Constraints**: Must not block game loop with CV processing; graceful webcam fallback  
**Scale/Scope**: Single-player, single-screen, ~8 source files

## Constitution Check

*No constitution file exists. Proceeding without governance gates.*

## Project Structure

### Documentation (this feature)

```text
specs/1-space-scream/
├── spec.md              # Feature specification
├── plan.md              # This file
├── checklists/
│   └── requirements.md  # Quality checklist
└── tasks.md             # Task breakdown (generated next)
```

### Source Code (repository root)

```text
src/
├── main.py              # Entry point — game loop, initialization
├── settings.py          # Constants (screen size, colors, physics tunables)
├── ship.py              # Ship entity — movement, rotation, strafe, rendering
├── asteroid.py          # Asteroid entity — drift, split, rendering
├── bullet.py            # Bullet entity — travel, lifetime, rendering
├── game.py              # Game state — score, lives, waves, collisions
├── emotion_engine.py    # Webcam capture + FER analysis (background thread)
├── hud.py               # HUD rendering — score, lives, face display
├── hud_face.py          # Digital face state machine + vector expression rendering
└── debug_overlay.py     # D-key toggled emotion bars overlay

assets/
└── fonts/               # Game fonts (optional — can use pygame default)
```

**Structure Decision**: Single project layout. All game modules live under `src/`. No external image assets — all graphics are vector-drawn using Pygame primitives.

## Research

### Decision 1 — Emotion Recognition Library

- **Decision**: Use `FER` (Facial Expression Recognition) library
- **Rationale**: Purpose-built for facial emotion detection. Returns 7 emotion scores (happy, sad, angry, surprise, fear, disgust, neutral) as float confidence values. Simple API: `FER().detect_emotions(frame)`. Lightweight enough for real-time use when throttled.
- **Alternatives Considered**:
  - `deepface` — More powerful but heavier; overkill for this use case
  - `EmotiEffLib` — Faster inference with ONNX but more complex setup
  - Custom CNN — Too much effort for a game project

### Decision 2 — Threading Strategy

- **Decision**: Exactly two threads with shared-memory numpy array (producer/consumer)
- **Rationale**: Per spec FR-018, the architecture is mandated: one main game thread (consumer) and one face-reading thread (producer). They communicate through a shared numpy array of shape `(N,)` where N ≥ 7 (one float per emotion channel). The producer thread runs `cv2.VideoCapture` + `FER.detect_emotions()` in a loop and writes results to the shared array. The main thread reads from the array each frame. A `threading.Lock` protects concurrent access. This avoids queue overhead and gives the game thread instant access to the latest emotion snapshot.
- **Alternatives Considered**:
  - `multiprocessing` with shared memory — Higher overhead, complex setup; threading is sufficient for this use case
  - `queue.Queue` — Adds latency and complexity vs. a simple numpy array read
  - More than 2 threads — Ruled out by FR-018 (exactly two threads mandated)

### Decision 3 — HUD Face Rendering

- **Decision**: Procedural vector-drawn face using Pygame drawing primitives
- **Rationale**: Per spec FR-017, all graphics must be vector-drawn. The face will be constructed from circles (head outline, eyes, pupils), arcs (eyebrows, mouth curves), and lines. Emotion states change the curvature of the mouth arc, eyebrow angles, eye shapes, and pupil positions. This approach is lightweight, resolution-independent, and enables smooth interpolation between emotion states by tweening control points.
- **Alternatives Considered**:
  - Pre-generated PNG images — Ruled out by FR-017 (no bitmap assets permitted)
  - Sprite sheet animation — Ruled out by FR-017
  - 3D face model — Massive overkill for a 2D game

### Decision 4 — Physics Model

- **Decision**: Simple Newtonian mechanics with drag
- **Rationale**: Ship has position, velocity, and angle. Thrust adds force along the facing direction. Drag gradually slows the ship. Strafe (Q/E) adds force perpendicular to facing. Screen wrapping teleports entities crossing edges. This matches classic Asteroids feel.

## Data Model

### Ship
| Field | Type | Description |
|-------|------|-------------|
| x, y | float | Position (pixels) |
| vx, vy | float | Velocity vector |
| angle | float | Facing direction (degrees, 0=up) |
| lives | int | Remaining lives (default 3) |
| invulnerable_timer | float | Seconds of post-respawn invulnerability |
| fire_cooldown | float | Seconds until next shot allowed |

### Asteroid
| Field | Type | Description |
|-------|------|-------------|
| x, y | float | Position |
| vx, vy | float | Velocity |
| size | int | Tier: 3=large, 2=medium, 1=small |
| rotation | float | Visual spin angle |
| radius | float | Collision radius (derived from size) |

### Bullet
| Field | Type | Description |
|-------|------|-------------|
| x, y | float | Position |
| vx, vy | float | Velocity (fixed speed in ship's facing direction at fire time) |
| lifetime | float | Seconds remaining before auto-despawn |

### EmotionState (shared numpy array between threads)
| Field | Type | Description |
|-------|------|-------------|
| emotion_array | numpy.ndarray (float64, shape (N,)) | Shared array: indices 0-6 map to [happy, sad, angry, surprise, fear, disgust, neutral]. Values are confidence scores [0.0–1.0]. |
| lock | threading.Lock | Protects concurrent read/write access |
| face_detected | bool (or array index 7) | Whether a face was found in the last frame (can be stored as 8th element: 1.0=yes, 0.0=no) |
| last_updated | float (or array index 8) | Timestamp of last successful write (can be 9th element) |

### HUDFaceState
| Field | Type | Description |
|-------|------|-------------|
| current_emotion | str | Currently displayed emotion |
| target_emotion | str | Emotion transitioning toward |
| blend_alpha | float | Crossfade progress [0.0–1.0] |
| damage_flash_timer | float | Seconds remaining for pain overlay |
| health_modifier | str | "low_health" if 1 life remaining |

## Complexity Tracking

> No constitution violations — no complexity justifications needed.
