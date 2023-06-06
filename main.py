import pygame
import pygame.display
import os
import numpy as np
import pandas as pd
import random
import igraph as ig


# global constants
SCREEN_WIDTH=1440
SCREEN_HEIGHT=900
BLACK=(0,0,0)
SCREEN_BG=(50,50,50)

class Asterion(pygame.sprite.Sprite):
    def __init__(self, img_path, screen, x, y, xv, yv, g, jf, speed):
        pygame.sprite.Sprite.__init__(self)

        self.screen = screen
        self.xv = xv
        self.yv = yv
        self.image = pygame.image.load(img_path).convert_alpha()
        self.image.set_colorkey(self.image.get_at((0,0)))
        self.rect = self.image.get_rect()
        self.rect.move_ip([x,y])
        self.speed = speed
        self.g = g
        self.jf = jf
        self.shorthop = 5
        self.onplatform=False
        self.prevkey = pygame.key.get_pressed()
  
    @staticmethod
    def get_min_platform(collidelist):
            min_platform = collidelist[0]
            for p in collidelist:
                if p.rect.top > min_platform.rect.top:
                    min_platform = p
            return min_platform

    def get_closest_wall(self, collidelist):
            closest_wall = collidelist[0]
            closest_wall_dist = abs(self.rect.centerx - closest_wall.rect.centerx)
            for w in collidelist:
                if abs(self.rect.centerx - closest_wall.rect.centerx) < closest_wall_dist:
                    closest_wall = w
            return closest_wall
    
    
    def collisiony(self, platforms, x, y):
        self.rect.move_ip([x,y])
        collided = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.move_ip([-x,-y])
        if collided == []:
            return False
        minplatform = Asterion.get_min_platform(collided)
        if self.rect.bottom > minplatform.rect.top:
            return False
        elif (self.rect.centerx <= minplatform.rect.left or self.rect.centerx >= minplatform.rect.right):
            return False
        else:
            return True

    def collisionx(self, walls, x, y):
        self.rect.move_ip([x,y])
        collided = pygame.sprite.spritecollide(self, walls, False)
        self.rect.move_ip([-x,-y])
        if collided == []:
            return False
        # closestwall = self.get_closest_wall(collided)
        # if (abs(self.rect.centerx - closestwall.rect.centerx) > WALL_BUFFER):
        #     return False
        else:
            return True

    def move(self, walls, platforms, x, y):
        dx = x
        dy = y

        while self.collisiony(platforms, 0, dy):
            dy -= np.sign(dy)

        while self.collisionx(walls, dx, 0):
            dx -= np.sign(dx)

        self.rect.move_ip([dx, dy])
        self.xv = 0

 
    def keys(self):
        key = pygame.key.get_pressed()

        if key[pygame.K_RIGHT]: 
            self.xv=self.speed
        elif key[pygame.K_LEFT]:
            self.xv=-self.speed
        if key[pygame.K_SPACE] and self.onplatform:
            self.yv = -self.jf

        if self.prevkey[pygame.K_SPACE] and not key[pygame.K_SPACE]:
            if self.yv < -self.shorthop:
                self.yv = -self.shorthop

        self.prevkey = key
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self, walls, platforms):
        self.onplatform = self.collisiony(platforms, 0, 1)
        self.keys()

        if not self.onplatform:
            self.yv += self.g

        if self.yv > 0 and self.onplatform:
            self.yv = 0

        self.move(walls, platforms,  self.xv, self.yv)


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color, screen, platform):

        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.h = h
        self.w = w
        self.color = color
        self.screen = screen
        self.image = pygame.Surface([self.w, self.h])
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.platform = platform

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asterion")

asterion = Asterion("sprites/a0.png", screen, 300, 160, 0, 0, 1, 20, 10)
walls = pygame.sprite.Group()
platforms = pygame.sprite.Group()

walls.add(Wall(50, 0, 10, SCREEN_HEIGHT, BLACK, screen, False))
walls.add(Wall(1200, 0, 10, SCREEN_HEIGHT, BLACK, screen, False))
platforms.add(Wall(700, 400, 600, 10, BLACK, screen, True))
for x in range(360,1440,360):
     platforms.add(Wall(x, 600, 100, 10, BLACK, screen, True))

platforms.add(Wall(0, 700, SCREEN_WIDTH, 10, BLACK, screen, True))

#walls.add(Wall(0, 319, 102, 10, BLACK, screen, True))

clock = pygame.time.Clock()
running=True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False

    asterion.update(walls, platforms)
    
    screen.fill((SCREEN_BG)) 
    walls.draw(screen)
    platforms.draw(screen)
    asterion.draw(screen)
    pygame.display.update()

    clock.tick(60)
    