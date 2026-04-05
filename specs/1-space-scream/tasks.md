# Tasks: SpaceScream — Emotion-Driven Asteroids

**Branch**: `1-space-scream` | **Generated**: 2026-04-05  
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Implementation Strategy

- **MVP**: Phase 3 (US1 — Core Asteroids Gameplay). A fully playable game without webcam.
- **Incremental Delivery**: Each phase adds a testable slice. US2 adds emotion data, US3 makes it visible, US4 adds diagnostics.
- **Parallel Opportunities**: Tasks within each phase marked `[P]` can be developed concurrently.

---

## Phase 1: Setup

- [x] T001 Initialize project directory structure per plan (`src/`, `assets/fonts/`)
- [x] T002 Create `requirements.txt` with `pygame`, `opencv-python`, `fer`, `numpy` dependencies
- [x] T003 Install dependencies into Anaconda base environment via `pip install -r requirements.txt`
- [x] T004 Create `src/settings.py` with all game constants (screen dimensions 1024×768, FPS target 60, colors, physics tunables, emotion config)

---

## Phase 2: Foundational

- [x] T005 Create `src/main.py` — minimal Pygame boilerplate: init display, clock, event loop, quit handling. Renders a black screen at 60 FPS.
- [x] T006 Implement basic vector math helpers in `src/settings.py` or inline — angle-to-vector conversion, screen wrapping utility function

---

## Phase 3: User Story 1 — Core Asteroids Gameplay (P1)

**Goal**: Fully playable Asteroids with ship control, shooting, asteroid destruction, scoring, lives, game over.  
**Independent Test**: Launch `python src/main.py` — fly the ship with arrow keys + Q/E, shoot with Space, destroy asteroids, score points, lose lives, see Game Over.

- [x] T007 [US1] Create `src/ship.py` — Ship class with position, velocity, angle, lives, invulnerability timer, fire cooldown. Draw as a triangle/polygon rotated to facing angle.
- [x] T008 [US1] Implement ship thrust (Up arrow) — accelerate in facing direction with configurable thrust force and max speed
- [x] T009 [US1] Implement ship reverse thrust (Down arrow) — accelerate opposite to facing direction
- [x] T010 [US1] Implement ship rotation (Left/Right arrows) — rotate angle at configurable degrees/second
- [x] T011 [US1] Implement ship lateral strafe (Q/E keys) — accelerate perpendicular to facing direction (left/right)
- [x] T012 [US1] Implement ship drag/friction — velocity decays each frame by a friction coefficient
- [x] T013 [US1] Implement screen wrapping for ship — teleport to opposite edge when crossing boundaries
- [x] T014 [P] [US1] Create `src/bullet.py` — Bullet class with position, velocity, lifetime timer. Draw as a small bright dot/line.
- [x] T015 [US1] Implement bullet firing from ship — on Space keypress, spawn bullet at ship nose with velocity in ship facing direction. Enforce fire rate cooldown (max 5/sec).
- [x] T016 [US1] Implement bullet lifetime — bullets despawn after configurable duration (e.g., 2 seconds) or screen exit
- [x] T017 [P] [US1] Create `src/asteroid.py` — Asteroid class with position, velocity, size tier (3=large, 2=medium, 1=small), rotation, radius. Draw as irregular polygon.
- [x] T018 [US1] Implement asteroid spawning — spawn initial wave of large asteroids at random positions (away from ship) with random velocities
- [x] T019 [US1] Implement asteroid screen wrapping — same as ship wrapping
- [x] T020 [US1] Implement asteroid splitting — when a large/medium asteroid is hit, spawn 2-3 smaller tier asteroids with slightly randomized velocities. Small asteroids are destroyed completely.
- [x] T021 [P] [US1] Create `src/game.py` — Game class managing game state: list of asteroids, bullets, ship reference, score, wave number, game-over flag
- [x] T022 [US1] Implement collision detection — circle-based collision between bullet↔asteroid (destroy both, split asteroid, add score) and ship↔asteroid (lose life, respawn)
- [x] T023 [US1] Implement scoring system — small asteroid = 100pts, medium = 50pts, large = 20pts. Display score in HUD.
- [x] T024 [US1] Implement lives system — start with 3 lives, decrement on ship-asteroid collision, brief invulnerability after respawn (2 seconds, ship blinks)
- [x] T025 [US1] Implement Game Over screen — when lives reach 0, display "GAME OVER" with final score, press any key to restart
- [x] T026 [US1] Implement wave progression — when all asteroids destroyed, spawn new wave with +2 asteroids and slightly higher speed
- [x] T027 [US1] Create `src/hud.py` — basic HUD bar at bottom of screen showing score (left), lives (right) as ship icons. Reserve center area for face (Phase 5).
- [x] T028 [US1] Wire everything into `src/main.py` — integrate Ship, Asteroids, Bullets, Game, HUD into the main game loop with proper update/draw order

---

## Phase 4: User Story 2 — Webcam Emotion Recognition (P2)

**Goal**: Background thread captures webcam, runs FER, produces real-time emotion scores.  
**Independent Test**: Launch game with webcam connected. Emotion values logged to console or accessible via debug overlay (Phase 6). Game does not stutter. Fallback works without webcam.

- [x] T029 [US2] Create `src/emotion_engine.py` — EmotionEngine class wrapping webcam capture + FER analysis in a producer thread, with a shared numpy array for output
- [x] T030 [US2] Implement shared numpy emotion array — create numpy.ndarray of shape (9,) for [happy, sad, angry, surprise, fear, disgust, neutral, face_detected, timestamp]. Protected by threading.Lock. Main thread reads (consumer), face thread writes (producer).
- [x] T031 [US2] Implement producer thread — daemon thread that runs `cv2.VideoCapture` read loop, passes frames to `FER().detect_emotions()`, acquires lock, writes 7 emotion scores + face_detected flag + timestamp into the shared numpy array
- [x] T032 [US2] Implement consumer read method — thread-safe getter that acquires lock and returns a copy of the shared numpy array for the main game thread to use each frame
- [x] T033 [US2] Implement graceful webcam fallback — if `VideoCapture` fails to open, set all array values to neutral defaults (neutral=1.0, rest=0.0), log warning, do not crash
- [x] T034 [US2] Implement face-lost decay — if face_detected is 0.0 for >2 seconds, producer gradually decays emotion values toward neutral in the shared array
- [x] T035 [US2] Integrate EmotionEngine into `src/main.py` — start producer thread on game init, stop on quit, read shared numpy array each frame and pass emotion values to HUD systems

---

## Phase 5: User Story 3 — HUD Emotion Face (P3)

**Goal**: Digital face in HUD bottom-center reflects player's detected emotions + reacts to game events.  
**Independent Test**: With webcam: smile → face smiles, frown → face frowns. Without webcam: face stays neutral. Ship takes damage → face shows pain briefly.

- [x] T036 [P] [US3] Define vector face geometry parameters in `src/hud_face.py` — map each emotion (neutral, happy, sad, angry, surprise, fear, disgust, damage, low_health) to a set of control points: mouth arc curvature, eyebrow angle, eye openness, pupil position, face color tint
- [x] T037 [US3] Create `src/hud_face.py` — HUDFace class with current/target emotion, blend alpha, damage flash timer, health modifier
- [x] T038 [US3] Implement vector face rendering — draw face using `pygame.draw.circle` (head, eyes, pupils), `pygame.draw.arc` (mouth, eyebrows), `pygame.draw.line` (detail lines). Face constructed entirely from primitives, no image assets.
- [x] T039 [US3] Implement emotion-to-face mapping — select face image based on dominant emotion from EmotionState
- [x] T040 [US3] Implement smooth interpolation between emotion states — when dominant emotion changes, tween control points (mouth curvature, eyebrow angle, eye shape) from current to target over ~0.5 seconds
- [x] T041 [US3] Implement damage flash override — on ship-asteroid collision, show damage face for 0.5 seconds regardless of camera emotion
- [x] T042 [US3] Implement low-health modifier — when 1 life remaining, blend worried/stressed expression with camera emotion
- [x] T043 [US3] Integrate HUDFace into `src/hud.py` — render face in the reserved center area of the HUD bar, sized proportionally

---

## Phase 6: User Story 4 — Debug Emotion Overlay (P4)

**Goal**: D key toggles overlay showing 7 emotion bars with numeric values updating in real-time.  
**Independent Test**: Press D → bars appear. Change expression → bars update. Press D again → bars disappear. No webcam → bars show 0 with "No webcam" text.

- [x] T044 [US4] Create `src/debug_overlay.py` — DebugOverlay class with toggle state, bar rendering logic
- [x] T045 [US4] Implement D-key toggle — listen for D keypress in event loop, flip overlay visibility boolean
- [x] T046 [US4] Implement emotion bar rendering — for each of 7 emotions, draw labeled horizontal bar (proportional to confidence 0.0-1.0) with numeric value text. Use color-coding per emotion.
- [x] T047 [US4] Implement no-webcam indicator — if EmotionState.face_detected is False, show "No webcam" or "No face" text alongside zeroed bars
- [x] T048 [US4] Integrate DebugOverlay into `src/main.py` — draw overlay on top of game when active, pass current EmotionState each frame

---

## Phase 7: Polish & Cross-Cutting

- [x] T049 Add starfield background — render scrolling or static star dots for visual depth
- [x] T050 Add particle effects for asteroid destruction — brief burst of small fragments when asteroids are hit
- [x] T051 Add ship thruster visual — small flame/glow behind ship when accelerating
- [x] T052 Refine HUD layout — ensure score, lives, and face are visually balanced and readable
- [x] T053 Final integration test — play through 3+ waves with webcam active, verify all controls, HUD face transitions, debug overlay, and graceful fallback

---

## Dependencies

```text
Phase 1 (Setup) ──→ Phase 2 (Foundation) ──→ Phase 3 (US1: Gameplay)
                                                       │
                                                       ├──→ Phase 4 (US2: Emotion Engine)
                                                       │            │
                                                       │            ├──→ Phase 5 (US3: HUD Face)
                                                       │            │
                                                       │            └──→ Phase 6 (US4: Debug Overlay)
                                                       │
                                                       └──→ Phase 7 (Polish)
```

- Phases 5 and 6 depend on Phase 4 (emotion data) and Phase 3 (game running)
- Phases 5 and 6 are independent of each other and can be built in parallel
- Phase 7 depends on all prior phases

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 53 |
| Phase 1 (Setup) | 4 tasks |
| Phase 2 (Foundation) | 2 tasks |
| Phase 3 (US1 — Gameplay) | 22 tasks |
| Phase 4 (US2 — Emotion) | 7 tasks |
| Phase 5 (US3 — HUD Face) | 8 tasks |
| Phase 6 (US4 — Debug) | 5 tasks |
| Phase 7 (Polish) | 5 tasks |
| Parallel Opportunities | T014/T017/T021 (entities), T036 (assets), T044-T047 (debug) |
| MVP Scope | Phase 1-3: Playable Asteroids without webcam |
