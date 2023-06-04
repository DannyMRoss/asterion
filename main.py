import pygame
import pygame.display
import os

# global constants
SCREEN_WIDTH=1440
SCREEN_HEIGHT=900
BLACK=(0,0,0)
SCREEN_BG=(50,50,50)
FLOOR=SCREEN_HEIGHT-500

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


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color, screen):

        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.h = h
        self.w = w
        self.color = color
        self.screen = screen
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asterion")

asterion = Asterion("sprites/a.png", screen, 0, 0, 0, 0, 1, 20, 10, FLOOR)
wall = Wall(700, FLOOR, 500, 10, BLACK, screen)

clock = pygame.time.Clock()
running=True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False

    asterion.keys()
    asterion.physics()

    screen.fill((SCREEN_BG)) 
    wall.draw()
    asterion.draw(screen)
    pygame.display.update()

    clock.tick(60)