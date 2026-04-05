"""
SpaceScream — Asteroid Module
Destructible space debris with splitting behavior per FR-022.
"""
import math
import random
import pygame
from settings import (
    ASTEROID_SIZES, ASTEROID_VERTICES_MIN, ASTEROID_VERTICES_MAX,
    ASTEROID_VERTEX_VARIANCE, ASTEROID_SPIN_SPEED,
    SPLIT_COUNT_MIN, SPLIT_COUNT_MAX,
    SPLIT_SPREAD_ANGLE_2, SPLIT_SPREAD_ANGLE_3, SPLIT_OFFSET_RATIO,
    WHITE, SCREEN_WIDTH, PLAY_AREA_HEIGHT, wrap_position,
)


class Asteroid:
    def __init__(self, x, y, size, vx=None, vy=None):
        self.x = x
        self.y = y
        self.size = size  # 3=large, 2=medium, 1=small
        info = ASTEROID_SIZES[size]
        self.radius = info["radius"]
        self.score = info["score"]

        if vx is not None and vy is not None:
            self.vx = vx
            self.vy = vy
        else:
            speed_min, speed_max = info["speed_range"]
            speed = random.uniform(speed_min, speed_max)
            angle = random.uniform(0, 2 * math.pi)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed

        self.rotation = random.uniform(0, 360)
        self.spin = random.uniform(-ASTEROID_SPIN_SPEED, ASTEROID_SPIN_SPEED)
        self.alive = True

        # Generate irregular polygon shape (normalized vertices)
        self.vertex_count = random.randint(ASTEROID_VERTICES_MIN, ASTEROID_VERTICES_MAX)
        self.shape_offsets = []
        for i in range(self.vertex_count):
            angle = (2 * math.pi * i) / self.vertex_count
            r = 1.0 + random.uniform(-ASTEROID_VERTEX_VARIANCE, ASTEROID_VERTEX_VARIANCE)
            self.shape_offsets.append((angle, r))

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.x, self.y = wrap_position(self.x, self.y)
        self.rotation += self.spin * dt

    def split(self):
        """Split into smaller asteroids per FR-022: spread angle + radial offset."""
        if self.size <= 1:
            return []  # smallest — destroy completely

        new_size = self.size - 1
        count = random.randint(SPLIT_COUNT_MIN, SPLIT_COUNT_MAX)

        # Determine spread angle
        if count == 2:
            spread = SPLIT_SPREAD_ANGLE_2
        else:
            spread = SPLIT_SPREAD_ANGLE_3

        # Base angle = direction the bullet was traveling (random fallback)
        base_angle = math.atan2(self.vy, self.vx)

        children = []
        for i in range(count):
            # Evenly space children around the base angle
            child_angle = base_angle + math.radians(spread * (i - (count - 1) / 2))

            # Radial offset from parent center
            offset = self.radius * SPLIT_OFFSET_RATIO
            cx = self.x + math.cos(child_angle) * offset
            cy = self.y + math.sin(child_angle) * offset

            # Velocity: inherit parent velocity + spread component
            info = ASTEROID_SIZES[new_size]
            speed = random.uniform(*info["speed_range"])
            cvx = self.vx * 0.5 + math.cos(child_angle) * speed
            cvy = self.vy * 0.5 + math.sin(child_angle) * speed

            children.append(Asteroid(cx, cy, new_size, cvx, cvy))

        return children

    def get_vertices(self):
        """Get the rotated polygon vertices for drawing."""
        rad = math.radians(self.rotation)
        cos_r, sin_r = math.cos(rad), math.sin(rad)
        verts = []
        for angle, r in self.shape_offsets:
            px = math.cos(angle) * self.radius * r
            py = math.sin(angle) * self.radius * r
            rx = px * cos_r - py * sin_r
            ry = px * sin_r + py * cos_r
            verts.append((self.x + rx, self.y + ry))
        return verts

    def draw(self, surface):
        if not self.alive:
            return
        verts = self.get_vertices()
        pygame.draw.polygon(surface, WHITE, verts, 2)


def spawn_asteroids(count, ship_x, ship_y, wave_speed_mult=1.0):
    """Spawn asteroids at random positions away from the ship."""
    asteroids = []
    for _ in range(count):
        while True:
            x = random.uniform(0, SCREEN_WIDTH)
            y = random.uniform(0, PLAY_AREA_HEIGHT)
            dx = x - ship_x
            dy = y - ship_y
            if math.sqrt(dx * dx + dy * dy) > 200:
                break

        ast = Asteroid(x, y, 3)
        ast.vx *= wave_speed_mult
        ast.vy *= wave_speed_mult
        asteroids.append(ast)
    return asteroids
