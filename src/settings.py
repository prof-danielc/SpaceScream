"""
SpaceScream — Game Settings & Constants
All tunables, colors, dimensions, and physics parameters.
"""
import math

# ─── Display ──────────────────────────────────────────────
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "SpaceScream"

# HUD occupies bottom portion of screen
HUD_HEIGHT = 100
PLAY_AREA_HEIGHT = SCREEN_HEIGHT - HUD_HEIGHT

# ─── Colors (RGB) ─────────────────────────────────────────
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 60, 60)
GREEN = (60, 255, 60)
ORANGE = (255, 165, 0)
DARK_GRAY = (40, 40, 40)
MID_GRAY = (100, 100, 100)
LIGHT_GRAY = (180, 180, 180)
HUD_BG = (20, 20, 30)
HUD_BORDER = (60, 60, 80)

# Face colors
FACE_SKIN = (220, 190, 160)
FACE_SKIN_ANGRY = (240, 150, 130)
FACE_SKIN_FEAR = (180, 190, 200)
FACE_SKIN_DAMAGE = (255, 100, 100)
FACE_EYE_WHITE = (240, 240, 240)
FACE_PUPIL = (30, 30, 30)
FACE_MOUTH = (180, 60, 60)
FACE_EYEBROW = (80, 60, 40)

# Holographic colors
HOLO_CYAN = (0, 255, 255)
HOLO_BLUE = (0, 100, 255)
HOLO_RED = (255, 0, 80)
HOLO_GLOW_ALPHA = 40
SCANLINE_SPACING = 3
GLITCH_MAX_OFFSET = 10

# Debug overlay colors per emotion
EMOTION_COLORS = {
    "happy": (255, 220, 50),
    "sad": (80, 120, 220),
    "angry": (220, 50, 50),
    "surprise": (255, 160, 30),
    "fear": (160, 80, 200),
    "disgust": (80, 180, 80),
    "neutral": (180, 180, 180),
}

# ─── Ship Physics ─────────────────────────────────────────
SHIP_THRUST = 300.0          # pixels/sec^2
SHIP_REVERSE_THRUST = 150.0  # pixels/sec^2
SHIP_STRAFE_THRUST = 200.0   # pixels/sec^2
SHIP_ROTATION_SPEED = 250.0  # degrees/sec
SHIP_DRAG = 0.98             # velocity multiplier per frame (1.0 = no drag)
SHIP_MAX_SPEED = 400.0       # pixels/sec
SHIP_SIZE = 18               # radius of ship bounding circle
SHIP_INVULN_TIME = 2.0       # seconds of invulnerability after respawn
SHIP_BLINK_RATE = 0.1        # seconds per blink toggle during invulnerability
STARTING_LIVES = 3
RESPAWN_SAFE_RADIUS = 150    # pixels — center must be clear of asteroids before respawn

# ─── Bullet ───────────────────────────────────────────────
BULLET_SPEED = 500.0         # pixels/sec
BULLET_LIFETIME = 2.0        # seconds
BULLET_RADIUS = 2
FIRE_COOLDOWN = 0.2          # seconds (= 5 shots/sec max)

# ─── Asteroids ────────────────────────────────────────────
ASTEROID_SIZES = {
    3: {"radius": 50, "speed_range": (30, 80), "score": 20},   # large
    2: {"radius": 30, "speed_range": (50, 120), "score": 50},  # medium
    1: {"radius": 15, "speed_range": (80, 160), "score": 100}, # small
}
INITIAL_ASTEROIDS = 4
ASTEROIDS_PER_WAVE = 2       # additional asteroids per wave
WAVE_SPEED_MULTIPLIER = 1.05 # speed increase per wave
ASTEROID_VERTICES_MIN = 7
ASTEROID_VERTICES_MAX = 12
ASTEROID_VERTEX_VARIANCE = 0.4  # 0.0 = perfect circle, 1.0 = very jagged
ASTEROID_SPIN_SPEED = 30.0      # degrees/sec max

# Splitting
SPLIT_COUNT_MIN = 2
SPLIT_COUNT_MAX = 3
SPLIT_SPREAD_ANGLE_2 = 90    # degrees apart for 2 children
SPLIT_SPREAD_ANGLE_3 = 120   # degrees apart for 3 children
SPLIT_OFFSET_RATIO = 0.5     # children offset by parent_radius * this

# ─── Emotion System ───────────────────────────────────────
EMOTION_KEYS = ["happy", "sad", "angry", "surprise", "fear", "disgust", "neutral"]
EMOTION_ARRAY_SIZE = 9       # 7 emotions + face_detected + timestamp
EMOTION_IDX = {name: i for i, name in enumerate(EMOTION_KEYS)}
FACE_DETECTED_IDX = 7
TIMESTAMP_IDX = 8
FACE_LOST_DECAY_TIME = 5.0   # seconds before decaying to neutral
FACE_DECAY_RATE = 0.2        # per-second decay speed toward neutral

# ─── HUD Face ────────────────────────────────────────────
FACE_TRANSITION_SPEED = 2.0  # 1/seconds to complete transition (0.5s)
DAMAGE_FLASH_DURATION = 0.5  # seconds
EMOTION_BLEND_DOMINANCE = 0.6 # 1.0 = dominant only, 0.0 = pure weighted average

# ─── Particles ────────────────────────────────────────────
PARTICLE_COUNT = 8           # per asteroid destruction
PARTICLE_SPEED = 150.0       # pixels/sec
PARTICLE_LIFETIME = 0.6      # seconds

# ─── Stars ────────────────────────────────────────────────
STAR_COUNT = 120
STAR_LAYERS = 3              # parallax layers

# ─── Utility ──────────────────────────────────────────────
def angle_to_vector(angle_deg):
    """Convert angle in degrees (0=up, clockwise) to a unit vector (dx, dy)."""
    rad = math.radians(angle_deg - 90)  # -90 because 0=up in game, 0=right in math
    return math.cos(rad), math.sin(rad)


def wrap_position(x, y):
    """Wrap position around the play area (not HUD)."""
    x = x % SCREEN_WIDTH
    y = y % PLAY_AREA_HEIGHT
    return x, y
