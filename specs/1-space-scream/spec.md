# Feature Specification: SpaceScream — Emotion-Driven Asteroids

**Feature Branch**: `1-space-scream`  
**Created**: 2026-04-05  
**Status**: Draft  
**Input**: User description: "Create a game in Python similar to asteroids game. Arrow keys control the ship movement (forward, backward, turn right and turn left), space shoots, Q E keys control lateral movement. The game must use the webcam to read the player's face and use a computer vision library to measure different user emotions on a scale. The game must feature a HUD at the bottom of the screen that shows a digital human face. The purpose of this face is to demonstrate player emotions like Wolfenstein or Doom does it to demonstrate character status. However, the face in our game is also affected by the player's emotions. Use the D key to enable a debug overlay that shows player's emotions on scales and updates it in realtime."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Core Asteroids Gameplay (Priority: P1)

As a player, I launch the game and can immediately pilot a spaceship through an asteroid field. I use arrow keys to thrust forward/backward and rotate, Q/E to strafe laterally, and Space to fire bullets that destroy asteroids. Asteroids split into smaller fragments when hit. Colliding with an asteroid costs a life. The game ends when all lives are lost and displays a final score.

**Why this priority**: Without core gameplay, there is no game. This is the fundamental loop — move, shoot, survive, score.

**Independent Test**: Launch the game without a webcam connected. The ship should be fully controllable, asteroids should spawn and be destructible, scoring should work, and lives should decrement on collision. The HUD face can fallback to a neutral default.

**Acceptance Scenarios**:

1. **Given** the game has started, **When** the player presses the Up arrow, **Then** the ship accelerates in the direction it is facing.
2. **Given** the game has started, **When** the player presses the Down arrow, **Then** the ship decelerates or accelerates in the reverse direction.
3. **Given** the game has started, **When** the player presses Left/Right arrows, **Then** the ship rotates counter-clockwise/clockwise respectively.
4. **Given** the game has started, **When** the player presses Q, **Then** the ship strafes to the left relative to its facing direction.
5. **Given** the game has started, **When** the player presses E, **Then** the ship strafes to the right relative to its facing direction.
6. **Given** the game has started, **When** the player presses Space, **Then** a bullet fires from the ship's nose in the ship's facing direction.
7. **Given** a bullet contacts a large asteroid, **When** the collision is detected, **Then** the asteroid splits into 2-3 smaller asteroids spaced with a minimum spread angle and radial offset from the parent center, and the player's score increases.
8. **Given** a bullet contacts a small asteroid, **When** the collision is detected, **Then** the asteroid is destroyed (no further splitting) and the player's score increases by a higher amount.
9. **Given** the ship contacts an asteroid, **When** the collision is detected, **Then** the player loses one life. The ship waits to respawn at center until no asteroids are within a safe radius. A blinking ship outline is shown at center during the wait. Once the area is clear, the ship respawns with brief invulnerability.
10. **Given** the player has 0 lives remaining, **When** the ship is destroyed, **Then** a "Game Over" screen is displayed with the final score.

---

### User Story 2 — Webcam Emotion Recognition (Priority: P2)

As a player, when I launch the game with a webcam connected, the game captures my face in real-time and continuously measures my emotional state across multiple dimensions (happy, sad, angry, surprised, fearful, disgusted, neutral). These emotion readings are available to the HUD and debug systems.

**Why this priority**: This is the signature feature that differentiates SpaceScream from a standard Asteroids clone. It feeds data to both the HUD face (P3) and the debug overlay (P4).

**Independent Test**: Launch the game with a webcam. Verify that internal emotion values update when the player changes facial expressions. Can be validated through the debug overlay (P4) or by logging emotion values to the console.

**Acceptance Scenarios**:

1. **Given** the game starts and a webcam is available, **When** the game initializes, **Then** the webcam feed begins capturing frames for analysis without blocking the game loop.
2. **Given** the webcam is active, **When** the player smiles, **Then** the "happy" emotion value increases within 1-2 seconds.
3. **Given** the webcam is active, **When** the player shows a neutral face, **Then** the "neutral" emotion value is dominant.
4. **Given** no webcam is available, **When** the game starts, **Then** the game gracefully falls back to a neutral emotion state and does not crash.
5. **Given** the webcam is active, **When** the emotion detector processes a frame, **Then** it does not cause the game framerate to drop below 30 FPS.

---

### User Story 3 — HUD Emotion Face (Priority: P3)

As a player, I see a digital human face displayed prominently in the HUD at the bottom of the screen, reminiscent of the Doomguy/Wolfenstein status bar face. This face dynamically reflects my real-time emotions — if I smile, the face smiles; if I look angry, the face looks angry. The face also reacts to in-game events (taking damage, low health).

**Why this priority**: This is the primary visual payoff of the emotion system. It bridges the webcam data to a visible, immersive game element.

**Independent Test**: With a webcam connected, make various facial expressions and observe the HUD face changing to match. Without a webcam, the HUD face should default to neutral and still react to in-game events (damage flashes).

**Acceptance Scenarios**:

1. **Given** the game is running, **When** the player looks at the HUD bar, **Then** a digital face is visible at the bottom-center of the screen.
2. **Given** the emotion system detects "happy" as the dominant emotion, **When** the HUD updates, **Then** the face transitions to a happy/smiling expression.
3. **Given** the emotion system detects "angry" as the dominant emotion, **When** the HUD updates, **Then** the face transitions to an angry expression.
4. **Given** the ship takes damage from an asteroid, **When** the collision occurs, **Then** the HUD face briefly shows a pain/damage reaction regardless of camera emotion.
5. **Given** the player's health is low (1 life remaining), **When** the HUD updates, **Then** the face shows a worried/stressed expression blended with the camera emotion.
6. **Given** no webcam is connected, **When** the HUD updates, **Then** the face defaults to a neutral expression that only reacts to game events.

---

### User Story 4 — Debug Emotion Overlay (Priority: P4)

As a developer or curious player, I press the D key to toggle a debug overlay. This overlay shows real-time bar charts or scales for each detected emotion (happy, sad, angry, surprise, fear, disgust, neutral) with their numeric confidence values, updating continuously.

**Why this priority**: Essential for development, testing, and player curiosity. Low visual design burden but high diagnostic value.

**Independent Test**: Press D during gameplay. Verify that labeled bars appear for each emotion, update in real-time, and disappear when D is pressed again.

**Acceptance Scenarios**:

1. **Given** the game is running, **When** the player presses D, **Then** a debug overlay appears showing labeled emotion bars.
2. **Given** the debug overlay is visible, **When** the player presses D again, **Then** the overlay is hidden.
3. **Given** the debug overlay is visible and the webcam is active, **When** the player changes facial expression, **Then** the corresponding emotion bars update within 1-2 seconds.
4. **Given** the debug overlay is visible and no webcam is connected, **When** the player views the overlay, **Then** all bars show 0 or "N/A" with a "No webcam" indicator.

---

### Edge Cases

- What happens when the webcam is disconnected mid-game? — The emotion system gracefully switches to neutral/fallback mode. The game continues without interruption.
- What happens when no face is detected in the webcam frame (e.g., player looks away)? — The last known emotion state persists for a short decay period, then gradually returns to neutral.
- What happens when multiple faces are detected? — The system uses the largest/most centered face only.
- What happens when the game window is minimized or loses focus? — The game loop pauses or continues at reduced tick rate; webcam capture pauses.
- What happens when asteroids are all destroyed? — A new wave spawns with more/faster asteroids at increased difficulty.
- What happens if the player holds Space continuously? — Fire rate is capped to a maximum (e.g., 5 shots/second) to prevent bullet spam.
- What happens if the producer thread holds the lock during FER analysis? — This would block the game thread for 50-150ms and violate FR-009. FR-019 mandates the lock is only held during the buffer swap (microseconds), never during the expensive CV work.
- What happens if asteroids are at screen center when the ship needs to respawn? — The ship delays respawn until a safe radius around center is clear. A blinking outline shows the pending spawn point. This prevents chain-death loops (FR-020).
- What happens during the 5-15 second FER model initialization at launch? — The game starts immediately and is fully playable. The producer thread initializes FER on its own. HUD face shows neutral, debug overlay shows "Initializing camera..." until the first real reading arrives (FR-021).
- What happens when child asteroids spawn on top of each other or on the ship? — Children spawn with a minimum spread angle (90-120°) and radial offset from parent center. They don't cluster. Close-range shooting is risky by design (FR-022).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST render a playable Asteroids-style game at a minimum of 30 FPS on standard hardware.
- **FR-002**: System MUST accept keyboard input for ship control — Up (thrust forward), Down (thrust backward), Left (rotate CCW), Right (rotate CW), Q (strafe left), E (strafe right), Space (fire).
- **FR-003**: System MUST implement Newtonian-style ship physics with acceleration, velocity, drag/friction, and screen-edge wrapping.
- **FR-004**: System MUST spawn asteroids that drift across the screen, wrap at edges, and split into smaller fragments when shot.
- **FR-005**: System MUST detect collisions between bullets and asteroids (destroying them) and between the ship and asteroids (losing a life).
- **FR-006**: System MUST track and display the player's score (incrementing on asteroid destruction) and remaining lives.
- **FR-007**: System MUST display a "Game Over" screen when all lives are lost, showing the final score.
- **FR-008**: System MUST capture webcam frames and analyze facial expressions using a computer vision emotion recognition library, producing confidence scores for at least 7 emotions.
- **FR-009**: System MUST perform emotion analysis without degrading game performance below 30 FPS (via threading or frame-skipping).
- **FR-010**: System MUST display a digital human face in the HUD at the bottom-center of the screen that reflects the detected player emotion.
- **FR-011**: The HUD face MUST transition smoothly between emotion states (not snap instantly).
- **FR-012**: The HUD face MUST also react to in-game events such as taking damage (brief pain expression).
- **FR-013**: System MUST provide a debug overlay toggled by the D key showing all detected emotion values as labeled horizontal bars with numeric readouts, updating in real-time.
- **FR-014**: System MUST gracefully handle missing webcam by defaulting to neutral emotions and continuing gameplay.
- **FR-015**: System MUST cap the bullet fire rate to prevent spam (maximum ~5 bullets per second).
- **FR-016**: System MUST implement wave-based difficulty progression — when all asteroids are destroyed, a new wave spawns with increased count or speed.
- **FR-017**: ALL game graphics MUST be vector-drawn (lines, polygons, circles, arcs) — including the ship, asteroids, bullets, HUD elements, and the digital human face. No bitmap/raster image assets are permitted for game visuals.
- **FR-018**: System MUST use exactly two threads: one main game thread (consumer) and one face-reading thread (producer). The threads MUST communicate through a shared-memory numpy array representing emotion values. The face-reading thread continuously writes emotion scores to the array; the main game thread reads from it each frame.
- **FR-019**: The producer thread MUST NOT hold the threading lock during webcam capture or emotion analysis. The lock MUST only be held during the numpy array buffer swap (microseconds). A double-buffering pattern is used: producer writes emotion results to a back buffer outside the lock, then atomically swaps front/back buffers under lock. The consumer reads the front buffer under lock.
- **FR-020**: After ship destruction, the ship MUST delay respawn until no asteroids are within a safe radius of screen center. During the wait, a blinking ship outline is displayed at center. Once clear, the ship respawns with invulnerability. This prevents chain-death from asteroids occupying the spawn point.
- **FR-021**: The FER model MUST be initialized entirely on the producer thread. The game MUST launch and be playable immediately without waiting for model loading. During initialization, the HUD face defaults to neutral and the debug overlay shows "Initializing camera..." instead of emotion bars. Once the first successful emotion reading is produced, the system transitions seamlessly to live data.
- **FR-022**: When an asteroid splits, child asteroids MUST spawn with a minimum spread angle between them (90° for 2 children, 120° for 3) and a radial offset from the parent's center (at least half the parent's radius). Velocities inherit a component of the parent's velocity plus the spread vector. Close-range shooting remains risky by design — no invulnerability is granted.

### Key Entities

- **Ship**: The player-controlled spacecraft. Attributes: position, velocity, rotation angle, lives, invulnerability timer.
- **Asteroid**: Destructible space debris. Attributes: position, velocity, size tier (large/medium/small), rotation.
- **Bullet**: Projectile fired by the ship. Attributes: position, velocity, lifespan timer.
- **EmotionState**: A shared-memory numpy array of shape `(N,)` where N = number of emotion channels (at least 7). The face-reading producer thread writes confidence scores; the main game thread reads them. Access is synchronized via a threading lock or atomic read pattern.
- **HUDFace**: The visual face display in the HUD. Attributes: current displayed emotion, transition progress, game-event override (damage flash), health-based modifier.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Players can complete at least 3 waves of asteroids using all control inputs (arrows, Q, E, Space) without encountering control bugs.
- **SC-002**: The game maintains at least 30 FPS on a machine with a webcam active and emotion analysis running.
- **SC-003**: The HUD face visibly changes expression within 2 seconds of the player changing their facial expression, at least 80% of the time for strong expressions (smile, frown, surprise).
- **SC-004**: The debug overlay accurately displays 7 emotion channels with values updating at least 5 times per second.
- **SC-005**: The game launches and is fully playable (minus emotion features) when no webcam is present, with zero crashes or errors shown to the player.
- **SC-006**: Players intuitively understand the HUD face reflects their emotions within the first 30 seconds of play.

## Clarifications

### Session 2026-04-05

- Q: Should graphics use image assets or be vector-drawn? → A: ALL graphics must be vector-drawn (polygons, lines, arcs). No bitmap/raster assets.
- Q: How should threading and emotion data sharing work? → A: Exactly two threads. Main game thread (consumer) + face-reading thread (producer). Communication via shared-memory numpy array of emotion scores.
- Q: (Quizme) Where should the lock be held? → A: Lock MUST only be held during array swap (microseconds). Double-buffering: producer writes to back buffer unlocked, swaps front/back under lock. Producer MUST NOT hold lock during FER analysis.
- Q: (Quizme) What if asteroids are at center when ship respawns? → A: Delayed respawn until safe radius is clear (classic Asteroids approach). Blinking outline shown during wait.
- Q: (Quizme) What happens during FER model initialization delay? → A: Game starts immediately, fully playable. Producer thread self-initializes FER. HUD neutral, debug shows "Initializing camera..." until first reading.
- Q: (Quizme) What if child asteroids cluster or spawn on the ship? → A: Spread angle (90-120°) + radial offset from parent. Close-range risk is intentional.

## Assumptions

- The player's machine has Python 3.x via Anaconda 3 (base environment).
- A standard USB or built-in webcam is available for emotion capture (the game degrades gracefully without one).
- The `FER` library (or equivalent) provides adequate real-time performance when run in a background thread.
- Pygame is sufficient for 2D rendering at the required fidelity.
- All graphics are vector-drawn using Pygame drawing primitives (polygons, lines, circles, arcs). No external image assets are used.
- The game is single-player only.
- No persistent data storage (high scores, settings) is required for the initial version.
- Sound effects and music are not required for the initial version but may be added later.
