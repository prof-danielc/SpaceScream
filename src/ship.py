"""
SpaceScream — Ship Module
Player-controlled spacecraft with thrust, rotation, strafe, and rendering.
"""
import math
import pygame
from settings import (
    SHIP_THRUST, SHIP_REVERSE_THRUST, SHIP_STRAFE_THRUST,
    SHIP_ROTATION_SPEED, SHIP_DRAG, SHIP_MAX_SPEED, SHIP_SIZE,
    SHIP_INVULN_TIME, SHIP_BLINK_RATE, STARTING_LIVES,
    RESPAWN_SAFE_RADIUS, FIRE_COOLDOWN,
    SCREEN_WIDTH, PLAY_AREA_HEIGHT, CYAN, WHITE, RED,
    angle_to_vector, wrap_position,
)


class Ship:
    def __init__(self):
        self.reset()
        self.lives = STARTING_LIVES

    def reset(self):
        """Reset ship to center for respawn."""
        self.x = SCREEN_WIDTH / 2
        self.y = PLAY_AREA_HEIGHT / 2
        self.vx = 0.0
        self.vy = 0.0
        self.angle = 0.0  # 0 = pointing up
        self.invulnerable_timer = SHIP_INVULN_TIME
        self.fire_cooldown = 0.0
        self.alive = True
        self.waiting_to_respawn = False
        self.thrusting = False

    def die(self):
        """Ship is destroyed — enter respawn wait state."""
        self.lives -= 1
        self.alive = False
        self.waiting_to_respawn = True
        self.vx = 0.0
        self.vy = 0.0

    def can_respawn(self, asteroids):
        """Check if center is clear of asteroids (FR-020)."""
        cx, cy = SCREEN_WIDTH / 2, PLAY_AREA_HEIGHT / 2
        for ast in asteroids:
            dx = ast.x - cx
            dy = ast.y - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < RESPAWN_SAFE_RADIUS + ast.radius:
                return False
        return True

    def try_respawn(self, asteroids):
        """Attempt to respawn if center is safe."""
        if self.can_respawn(asteroids):
            self.reset()
            return True
        return False

    def update(self, dt, keys):
        """Update ship state each frame."""
        if not self.alive:
            return

        self.thrusting = False

        # Rotation
        if keys[pygame.K_LEFT]:
            self.angle -= SHIP_ROTATION_SPEED * dt
        if keys[pygame.K_RIGHT]:
            self.angle += SHIP_ROTATION_SPEED * dt
        self.angle %= 360

        # Forward / reverse thrust
        dx, dy = angle_to_vector(self.angle)
        if keys[pygame.K_UP]:
            self.vx += dx * SHIP_THRUST * dt
            self.vy += dy * SHIP_THRUST * dt
            self.thrusting = True
        if keys[pygame.K_DOWN]:
            self.vx -= dx * SHIP_REVERSE_THRUST * dt
            self.vy -= dy * SHIP_REVERSE_THRUST * dt

        # Lateral strafe (Q/E) — perpendicular to facing
        sx, sy = -dy, dx  # 90° left of facing
        if keys[pygame.K_e]:
            self.vx += sx * SHIP_STRAFE_THRUST * dt
            self.vy += sy * SHIP_STRAFE_THRUST * dt
        if keys[pygame.K_q]:
            self.vx -= sx * SHIP_STRAFE_THRUST * dt
            self.vy -= sy * SHIP_STRAFE_THRUST * dt

        # Clamp speed
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if speed > SHIP_MAX_SPEED:
            scale = SHIP_MAX_SPEED / speed
            self.vx *= scale
            self.vy *= scale

        # Apply drag
        self.vx *= SHIP_DRAG
        self.vy *= SHIP_DRAG

        # Move
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.x, self.y = wrap_position(self.x, self.y)

        # Timers
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
        if self.fire_cooldown > 0:
            self.fire_cooldown -= dt

    @property
    def is_invulnerable(self):
        return self.invulnerable_timer > 0

    def can_fire(self):
        return self.alive and self.fire_cooldown <= 0

    def fire(self):
        """Reset fire cooldown."""
        self.fire_cooldown = FIRE_COOLDOWN

    def get_nose_position(self):
        """Get the position of the ship's nose (tip)."""
        dx, dy = angle_to_vector(self.angle)
        return self.x + dx * SHIP_SIZE, self.y + dy * SHIP_SIZE

    def get_vertices(self):
        """Get the 3 triangle vertices of the ship, rotated to current angle."""
        rad = math.radians(self.angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        # Triangle: nose at top, two wings at back
        raw = [
            (0, -SHIP_SIZE),          # nose
            (-SHIP_SIZE * 0.6, SHIP_SIZE * 0.7),  # left wing
            (SHIP_SIZE * 0.6, SHIP_SIZE * 0.7),   # right wing
        ]
        verts = []
        for rx, ry in raw:
            x = self.x + rx * cos_a - ry * sin_a
            y = self.y + rx * sin_a + ry * cos_a
            verts.append((x, y))
        return verts

    def draw(self, surface, time):
        """Draw the ship. Blinks during invulnerability."""
        if not self.alive:
            # Draw blinking ghost at center if waiting to respawn
            if self.waiting_to_respawn:
                if int(time / SHIP_BLINK_RATE) % 2 == 0:
                    cx, cy = SCREEN_WIDTH / 2, PLAY_AREA_HEIGHT / 2
                    # Save position, draw ghost, restore
                    ox, oy = self.x, self.y
                    self.x, self.y = cx, cy
                    verts = self.get_vertices()
                    self.x, self.y = ox, oy
                    pygame.draw.polygon(surface, (60, 60, 80), verts, 1)
            return

        # Blinking during invulnerability
        if self.is_invulnerable:
            if int(time / SHIP_BLINK_RATE) % 2 == 0:
                return  # invisible frame

        verts = self.get_vertices()
        pygame.draw.polygon(surface, CYAN, verts, 2)

        # Inner detail line
        mid_back_x = (verts[1][0] + verts[2][0]) / 2
        mid_back_y = (verts[1][1] + verts[2][1]) / 2
        mid_x = (verts[0][0] + mid_back_x) / 2
        mid_y = (verts[0][1] + mid_back_y) / 2
        pygame.draw.line(surface, CYAN, (mid_x, mid_y), (mid_back_x, mid_back_y), 1)

    def draw_thruster(self, surface, time):
        """Draw thruster flame when accelerating."""
        if not self.alive or not self.thrusting:
            return
        if self.is_invulnerable and int(time / SHIP_BLINK_RATE) % 2 == 0:
            return

        rad = math.radians(self.angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        # Flame triangle behind the ship
        import random
        flicker = random.uniform(0.7, 1.3)
        flame_len = SHIP_SIZE * 0.8 * flicker

        raw = [
            (-SHIP_SIZE * 0.25, SHIP_SIZE * 0.6),
            (SHIP_SIZE * 0.25, SHIP_SIZE * 0.6),
            (0, SHIP_SIZE * 0.6 + flame_len),
        ]
        verts = []
        for rx, ry in raw:
            x = self.x + rx * cos_a - ry * sin_a
            y = self.y + rx * sin_a + ry * cos_a
            verts.append((x, y))

        color = (255, 200, 50) if int(time * 20) % 2 == 0 else (255, 120, 30)
        pygame.draw.polygon(surface, color, verts, 0)
