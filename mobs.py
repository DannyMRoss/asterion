import pygame
import pygame.display
import numpy as np
import random
from constants import *

class Mob(pygame.sprite.Sprite):
    def __init__(self, img_path, scale, rx, ry, x, y, xv, yv, health, damage, xknock, yknock):
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
        self.g = 1
        self.jf = 35
        self.shorthop = 20
        self.onplatform=False
        self.health = health
        self.damage = damage
        self.xknock = xknock
        self.yknock = yknock


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


class Walker(Mob):
        def __init__(self, *args, **kwargs):
            super().__init__(img_path="sprites/a0.png", scale=SCALE/1.5, rx=0, ry=len(DOORSY), 
                             x=STARTX, y=50, xv=1, yv=0,
                             health=1, damage=1, xknock=10, yknock=10, *args, **kwargs)

        def hit(self, asterion, walls, platforms):
            asterion.health -= self.damage
            s = np.sign(asterion.xv) * np.sign(self.xv)
            asterion.xv = self.xknock * self.xv
            if s==-1 or asterion.xv==0:
                self.xv = -self.xv
            self.move(walls, platforms, np.sign(self.xv)*self.speed/4, 0)

class Flyer(Mob):
        def __init__(self, maze, *args, **kwargs):
            super().__init__(img_path="sprites/a0.png", scale=SCALE/1.5, rx=0, ry=len(DOORSY),
                     x=STARTX, y=50, xv=2, yv=2, health=1, damage=1, xknock=10, yknock=10, *args, **kwargs)
            self.maze = maze
            self.v0 = random.randint(0,DIM**2-1)
            self.v1 = random.randint(0,DIM**2-1)
            while self.v0 == self.v1:
                self.v1 = random.randint(0, DIM**2 - 1)

            X = self.maze.buildpath(self.v0,self.v1)
            self.path = [X.loc[0, 'v1']]
            self.path.extend(X['v2'].to_list())
            
            self.rect.center = self.path[0]
            self.vector = self.path[0]
            self.pathr = self.path[::-1]
            self.path.pop(0)

        def move(self):
            if len(self.path)==0:
                self.path = self.pathr
                self.pathr = self.path[::-1]
            v = self.path[0]
            self.vector.move_towards_ip(v, self.xv)
            self.rect.center = self.vector
            if self.vector==v:
                self.path.pop(0)

        def hit(self, asterion):
            asterion.health -= self.damage
        

        def update(self):
            self.move()