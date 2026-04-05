"""
SpaceScream — Bullet Module
Projectiles fired by the ship.
"""
import pygame
from settings import BULLET_SPEED, BULLET_LIFETIME, BULLET_RADIUS, YELLOW, wrap_position, angle_to_vector, PLAY_AREA_HEIGHT, SCREEN_WIDTH


class Bullet:
    def __init__(self, x, y, angle):
        dx, dy = angle_to_vector(angle)
        self.x = x
        self.y = y
        self.vx = dx * BULLET_SPEED
        self.vy = dy * BULLET_SPEED
        self.lifetime = BULLET_LIFETIME
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.x, self.y = wrap_position(self.x, self.y)
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), BULLET_RADIUS)
