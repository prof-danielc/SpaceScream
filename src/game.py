"""
SpaceScream — Game State Manager
Handles score, lives, waves, collisions, particles, and stars.
"""
import math
import random
import pygame
from settings import (
    INITIAL_ASTEROIDS, ASTEROIDS_PER_WAVE, WAVE_SPEED_MULTIPLIER,
    SCREEN_WIDTH, PLAY_AREA_HEIGHT, STAR_COUNT, STAR_LAYERS,
    PARTICLE_COUNT, PARTICLE_SPEED, PARTICLE_LIFETIME,
    WHITE, YELLOW, RED,
)
from ship import Ship
from bullet import Bullet
from asteroid import Asteroid, spawn_asteroids


class Particle:
    """Brief visual debris from asteroid destruction."""
    def __init__(self, x, y, color=WHITE):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(PARTICLE_SPEED * 0.3, PARTICLE_SPEED)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = PARTICLE_LIFETIME * random.uniform(0.5, 1.0)
        self.color = color
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        alpha = max(0, self.lifetime / PARTICLE_LIFETIME)
        r, g, b = self.color
        color = (int(r * alpha), int(g * alpha), int(b * alpha))
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 2)


class Star:
    """Background star for visual depth."""
    def __init__(self, layer):
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(0, PLAY_AREA_HEIGHT)
        self.layer = layer
        brightness = random.randint(40, 100) + layer * 40
        self.color = (brightness, brightness, brightness + 20)
        self.size = 1 if layer < 2 else random.choice([1, 2])


class Game:
    def __init__(self):
        self.ship = Ship()
        self.bullets = []
        self.asteroids = []
        self.particles = []
        self.stars = []
        self.score = 0
        self.wave = 0
        self.game_over = False
        self.game_time = 0.0
        self.damage_event = False  # flag for HUD face

        # Generate starfield
        for layer in range(STAR_LAYERS):
            for _ in range(STAR_COUNT // STAR_LAYERS):
                self.stars.append(Star(layer))

        self.start_new_wave()

    def start_new_wave(self):
        self.wave += 1
        count = INITIAL_ASTEROIDS + (self.wave - 1) * ASTEROIDS_PER_WAVE
        speed_mult = WAVE_SPEED_MULTIPLIER ** (self.wave - 1)
        new_asteroids = spawn_asteroids(count, self.ship.x, self.ship.y, speed_mult)
        self.asteroids.extend(new_asteroids)

    def restart(self):
        self.__init__()

    def update(self, dt, keys, fire_pressed):
        if self.game_over:
            return

        self.game_time += dt
        self.damage_event = False

        # Ship respawn logic (FR-020)
        if self.ship.waiting_to_respawn:
            if self.ship.lives <= 0:
                self.game_over = True
                return
            self.ship.try_respawn(self.asteroids)
            # Even while waiting, asteroids continue
            for ast in self.asteroids:
                ast.update(dt)
            for p in self.particles:
                p.update(dt)
            self.particles = [p for p in self.particles if p.alive]
            return

        # Update ship
        self.ship.update(dt, keys)

        # Fire bullet
        if fire_pressed and self.ship.can_fire():
            nx, ny = self.ship.get_nose_position()
            self.bullets.append(Bullet(nx, ny, self.ship.angle))
            self.ship.fire()

        # Update bullets
        for b in self.bullets:
            b.update(dt)
        self.bullets = [b for b in self.bullets if b.alive]

        # Update asteroids
        for ast in self.asteroids:
            ast.update(dt)

        # Update particles
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

        # Collision: bullet ↔ asteroid
        new_asteroids = []
        for b in self.bullets:
            if not b.alive:
                continue
            for ast in self.asteroids:
                if not ast.alive:
                    continue
                dx = b.x - ast.x
                dy = b.y - ast.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < ast.radius:
                    b.alive = False
                    ast.alive = False
                    self.score += ast.score
                    # Spawn particles
                    for _ in range(PARTICLE_COUNT):
                        self.particles.append(Particle(ast.x, ast.y, WHITE))
                    # Split asteroid
                    children = ast.split()
                    new_asteroids.extend(children)
                    break

        self.asteroids = [a for a in self.asteroids if a.alive]
        self.asteroids.extend(new_asteroids)

        # Collision: ship - asteroid
        if self.ship.alive and not self.ship.is_invulnerable:
            for ast in self.asteroids:
                if not ast.alive:
                    continue
                dx = self.ship.x - ast.x
                dy = self.ship.y - ast.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < ast.radius + 10:  # ship collision radius ~10
                    self.ship.die()
                    self.damage_event = True
                    # Explosion particles at ship
                    for _ in range(PARTICLE_COUNT * 2):
                        self.particles.append(Particle(self.ship.x, self.ship.y, YELLOW))
                    break

        # Wave progression
        if len(self.asteroids) == 0 and self.ship.alive:
            self.start_new_wave()

    def draw(self, surface):
        # Draw stars
        for star in self.stars:
            pygame.draw.circle(surface, star.color, (int(star.x), int(star.y)), star.size)

        # Draw particles
        for p in self.particles:
            p.draw(surface)

        # Draw asteroids
        for ast in self.asteroids:
            ast.draw(surface)

        # Draw bullets
        for b in self.bullets:
            b.draw(surface)

        # Draw ship
        self.ship.draw_thruster(surface, self.game_time)
        self.ship.draw(surface, self.game_time)
