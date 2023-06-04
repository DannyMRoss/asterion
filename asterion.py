import pygame
import pygame.display
import os

class Asterion(pygame.sprite.Sprite):
    def __init__(self, img_path, screen, x, y, xv, yv, g, jf, speed, floor):
        pygame.sprite.Sprite.__init__(self)

        self.screen = screen
        self.x = x
        self.y = y
        self.xv = xv
        self.yv = yv
        self.image = pygame.image.load(img_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.speed = speed
        self.g = g
        self.jf = jf
        self.floor=floor

    def jump(self):
        if self.y == self.floor:
            self.yv = -self.jf

    def physics(self):
        self.x += self.xv
        self.y += self.yv
        self.yv += self.g
        
        if self.y > self.floor:
            self.y = self.floor
            self.yv = 0
        
        if self.y <= 0:
            self.y = 0

    def platform(self, walls):
        pygame.sprite.spritecollideany(self, walls)

        
    def keys(self):
        key = pygame.key.get_pressed()
        dist = self.speed
        if key[pygame.K_DOWN]:
            self.y += dist
        elif key[pygame.K_UP]:
            self.y -= dist
        if key[pygame.K_RIGHT]: 
            self.x += dist
            if self.x>self.screen.get_width()-self.image.get_width():
                self.x=self.screen.get_width()-self.image.get_width()
        elif key[pygame.K_LEFT]:
            self.x -= dist
            if self.x<0:
                self.x=0 
        if key[pygame.K_SPACE]:
            self.jump()
        
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))
