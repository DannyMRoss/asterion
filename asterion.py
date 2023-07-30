import pygame
import pygame.display
import numpy as np
from constants import *
from weapons import *

class Asterion(pygame.sprite.Sprite):
    def __init__(self, screen, img_path, scale, rx, ry, x, y, xv, yv, g, jf, shorthop, speed, health, quiver):
        pygame.sprite.Sprite.__init__(self)

        self.screen = screen
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
        self.prevkey = pygame.key.get_pressed()
        self.hitpaths = pygame.sprite.Group()
        self.levels = 0
        self.new_level = False
        self.health = health
        self.arrows = pygame.sprite.Group()
        self.quiver = quiver
        self.ahits = 0
  
    # @staticmethod
    # def get_min_platform(collidelist):
    #         min_platform = collidelist[0]
    #         for p in collidelist:
    #             if p.rect.top > min_platform.rect.top:
    #                 min_platform = p
    #         return min_platform


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
        # minplatform = Asterion.get_min_platform(collided)
        # if self.rect.bottom > minplatform.rect.top:
        #   return False
        # elif (self.rect.centerx <= minplatform.rect.left or self.rect.centerx >= minplatform.rect.right):
        #   return False
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
    
    def pathcollision(self, path):
        hitpath = pygame.sprite.spritecollide(self, path, False)
        if hitpath!=[] and hitpath[0].groups() != self.hitpaths:
            self.hitpaths.add(hitpath)

    def gatecollision(self, gate):
        collided = pygame.sprite.spritecollide(self, gate, False)
        if collided != []:
            self.levels += 1
            self.new_level = True
            self.rect.bottomleft = (STARTX, STARTY)
            self.hitpaths.empty()
            self.arrows.empty()

    def move(self, walls, platforms, path, gate, x, y):
        dx = x
        dy = y

        while self.collisiony(platforms, 0, dy):
            dy -= np.sign(dy)

        while self.collisionx(walls, dx, 0):
            dx -= np.sign(dx)

        self.rect.move_ip([dx, dy])
        self.pathcollision(path)
        self.gatecollision(gate)
        if self.rect.left > SCREEN_WIDTH:
            self.rx += 1
            self.hitpaths.empty()
            self.rect.move_ip(-SCREEN_WIDTH,0)
        elif self.rect.right < 0:
            self.rx -= 1
            self.hitpaths.empty()
            self.rect.move_ip(SCREEN_WIDTH,0)
        if self.rect.bottom < 0:
            self.ry -= 1
            self.hitpaths.empty()
            self.rect.move_ip(0,SCREEN_HEIGHT+HEAD)
        if self.rect.top > SCREEN_HEIGHT+HEAD:
            self.ry += 1
            self.hitpaths.empty()
            self.rect.move_ip(0,-SCREEN_HEIGHT+HEAD)
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

        arrow=False
        if self.quiver>0:
            if key[pygame.K_d] and not self.prevkey[pygame.K_d]:
                arrow=True
                axv, ayv, aw, ah = 10, 0, 10, 2
                ax, ay = self.rect.right, self.rect.centery
            elif key[pygame.K_a] and not self.prevkey[pygame.K_a]:
                arrow=True
                axv, ayv, aw, ah = -10, 0, 10, 2
                ax, ay = self.rect.left, self.rect.centery
            elif key[pygame.K_s] and not self.prevkey[pygame.K_s]:
                arrow=True
                axv, ayv, aw, ah = 0, 10, 2, 10
                ax, ay = self.rect.centerx, self.rect.centery
            elif key[pygame.K_w] and not self.prevkey[pygame.K_w]:
                arrow=True
                axv, ayv, aw, ah = 0, -10, 2, 10
                ax, ay = self.rect.centerx, self.rect.centery
        
        if arrow:
            self.arrows.add(Arrow(screen=self.screen, x=ax, y=ay, 
                                    xv=axv, yv=ayv,
                                    w=aw, h=ah, color=GREY, alpha=255))
            self.quiver -= 1

        self.prevkey = key
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)


    def update(self, walls, platforms, path, gate):
        self.onplatform = self.collisiony(platforms, 0, 1)
        self.keys()

        if not self.onplatform:
            self.yv += self.g

        if self.yv > 0 and self.onplatform:
            self.yv = 0

        self.move(walls, platforms, path, gate, self.xv, self.yv)
        for arrow in self.arrows:
            arrow.update(walls, platforms)