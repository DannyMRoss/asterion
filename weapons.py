import pygame
import pygame.display
import numpy as np
from constants import *

class Weapon(pygame.sprite.Sprite):
    def __init__(self, screen, x, y, w, h, color, alpha, xv, yv, health, damage, xknock, yknock):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.x = x
        self.y = y
        self.h = h
        self.w = w
        self.color = color
        self.image = pygame.Surface([self.w, self.h])
        self.image.fill(self.color)
        self.image.set_alpha(alpha)
        self.rect = self.image.get_rect()
        self.rect.left = self.x
        self.rect.top = self.y
        self.xv = xv
        self.yv = yv
        self.health = health
        self.damage = damage
        self.xknock = xknock
        self.yknock = yknock

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Arrow(Weapon):
    def __init__(self, *args, **kwargs):
        super().__init__(health=1, damage=1, xknock=1, yknock=1, *args, **kwargs)

    def get_closest_wall(self, collidelist):
        closest_wall = collidelist[0]
        closest_wall_dist = abs(self.rect.centerx - closest_wall.rect.centerx)
        for w in collidelist:
            if abs(self.rect.centerx - closest_wall.rect.centerx) < closest_wall_dist:
                closest_wall = w
        return closest_wall
    
    def collidesprite(self, sprite, x, y):
        self.rect.move_ip([x,y])
        collided = pygame.sprite.collide_rect(self, sprite)
        self.rect.move_ip([-x,-y])
        return collided
    
    def collisiony(self, platforms, x, y):
        self.rect.move_ip([x,y])
        collided = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.move_ip([-x,-y])
        if collided == []:
            return False
        closest = self.get_closest_wall(collided)
        if self.collidesprite(closest, 1, 0) or self.collidesprite(closest, -1, 0):
            return False
        else:
            return True

    def collisionx(self, walls, x, y):
        self.rect.move_ip([x,y])
        collided = pygame.sprite.spritecollide(self, walls, False)
        self.rect.move_ip([-x,-y])
        if collided == []:
            return False
        closestwall = self.get_closest_wall(collided)
        if self.collidesprite(closestwall, 0, 1) or self.collidesprite(closestwall, 0, -1):
            return False
        else:
            return True

    def move(self, walls, platforms, x, y):
        dx = x
        dy = y

        if self.collisiony(platforms, 0, dy):
            while self.collisiony(platforms, 0, dy):
                dy -= np.sign(dy)
            self.yv = 0

        if self.collisionx(walls, dx, 0):
            while self.collisionx(walls, dx, 0):
                dx -= np.sign(dx)
            self.xv = 0

        self.rect.move_ip([dx, dy])

    def update(self, walls, platforms):
        self.draw(self.screen)
        self.move(walls, platforms, self.xv, self.yv)