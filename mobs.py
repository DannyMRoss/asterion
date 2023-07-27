import pygame
import pygame.display
import numpy as np
from constants import *

class Mob(pygame.sprite.Sprite):
    def __init__(self, img_path, scale, rx, ry, x, y, xv, yv, g, jf, shorthop, speed, health, damage, xpower):
        pygame.sprite.Sprite.__init__(self)
        self.rx = rx
        self.ry = ry
        self.xv = xv
        self.yv = yv
        self.image = pygame.image.load(img_path).convert_alpha()
        self.image = pygame.transform.scale_by(self.image, scale)
        self.image.set_colorkey(self.image.get_at((0,0)))
        self.rect = self.image.get_rect()
        #self.rect.scale_by_ip(scale)
        self.rect.bottomleft = (x,y)
        self.speed = speed
        self.g = g
        self.jf = jf
        self.shorthop = shorthop
        self.onplatform=False
        self.health = health
        self.damage = damage
        self.xpower = xpower


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

        while self.collisiony(platforms, 0, dy):
            dy -= np.sign(dy)

        if self.collisionx(walls, dx, 0):
            while self.collisionx(walls, dx, 0):
                dx -= np.sign(dx)
            self.xv = -self.xv

        self.rect.move_ip([dx, dy])

        if self.rect.left > SCREEN_WIDTH:
            self.rect.move_ip(-SCREEN_WIDTH,0)
        elif self.rect.right < 0:
            self.rect.move_ip(SCREEN_WIDTH,0)
        if self.rect.bottom < 0:
            self.rect.move_ip(0,SCREEN_HEIGHT+HEAD)
        if self.rect.top > SCREEN_HEIGHT+HEAD:
            self.rect.move_ip(0,-SCREEN_HEIGHT+HEAD)

        
    def draw(self, surface):
        surface.blit(self.image, self.rect)


    def update(self, walls, platforms):
        self.onplatform = self.collisiony(platforms, 0, 1)

        if not self.onplatform:
            self.yv += self.g

        if self.yv > 0 and self.onplatform:
            self.yv = 0

        self.move(walls, platforms, self.xv, self.yv)

class Hunter(Mob):
        def __init__(self):
            Mob.__init__(self)