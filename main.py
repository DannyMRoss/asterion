import pygame
import pygame.display
import os
import numpy as np

# global constants
SCREEN_WIDTH=1440
SCREEN_HEIGHT=900
BLACK=(0,0,0)
SCREEN_BG=(50,50,50)
FLOOR=SCREEN_HEIGHT-500

class Asterion(pygame.sprite.Sprite):
    def __init__(self, img_path, screen, x, y, xv, yv, g, jf, speed):
        pygame.sprite.Sprite.__init__(self)

        self.screen = screen
        self.x = x
        self.y = y
        self.xv = xv
        self.yv = yv
        self.image = pygame.image.load(img_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.speed = speed
        self.g = g
        self.jf = jf
        self.onplatform=False
        self.JUMP=False
        self.maxjump=20

    @staticmethod
    def get_platform(collidelist):
            for wall in collidelist:
                if wall.platform:
                    return wall
                
    @staticmethod
    def get_min_platform(collidelist):
            platforms = []
            for wall in collidelist:
                if wall.platform:
                    platforms.append(wall)
            min_platform = platforms[0]
            for p in platforms:
                if p.rect.top > min_platform.rect.top:
                    min_platform = p
            return min_platform
                
    @staticmethod
    def get_wall(collidelist):
            for wall in collidelist:
                if not wall.platform:
                    return wall

    def collisiony(self, walls, x, y):
        self.rect.move_ip([x,y])
        collided = pygame.sprite.spritecollide(self, walls, False)
        platform = Asterion.get_platform(collided)
        self.rect.move_ip([-x,-y])
        if platform == None:
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
        wall = Asterion.get_wall(collided)
        self.rect.move_ip([-x,-y])
        if wall == None:
            return False
        else:
            return True

    def move(self, walls, x, y):
        dx = x
        dy = y

        while self.collisiony(walls, 0, dy):
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
        if self.JUMP and self.onplatform:
            self.yv = -self.jf
            self.JUMP = False
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self, walls):
        self.onplatform = self.collisiony(walls, 0, 1)
        self.keys()

        if not self.onplatform:
            self.yv += self.g

        if self.yv > 0 and self.onplatform:
            self.yv = 0

        self.move(walls, self.xv, self.yv)


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

asterion = Asterion("sprites/a.png", screen, 103, 160, 0, 0, 1, 20, 10)
walls = pygame.sprite.Group()

walls.add(Wall(1200, 0, 10, SCREEN_HEIGHT, BLACK, screen, False))
walls.add(Wall(700, 400, 600, 10, BLACK, screen, True))
for x in range(360,1440,360):
     walls.add(Wall(x, 600, 100, 10, BLACK, screen, True))

walls.add(Wall(0, 700, SCREEN_WIDTH, 10, BLACK, screen, True))

#walls.add(Wall(0, 319, 102, 10, BLACK, screen, True))

clock = pygame.time.Clock()
running=True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                sp_start = pygame.time.get_ticks()
        if event.type == pygame.KEYUP:
             if event.key == pygame.K_SPACE:
                sp_time = pygame.time.get_ticks() - sp_start
                asterion.jf = min(max(10, sp_time // 20),asterion.maxjump)
                asterion.JUMP = True

    asterion.update(walls)
    
    screen.fill((SCREEN_BG)) 
    walls.draw(screen)
    asterion.draw(screen)
    pygame.display.update()

    clock.tick(60)


# asterion.rect.centerx <= platform.rect.left or asterion.rect.centerx >= platform.rect.right

# # # walls.add(Wall(206, 0, 10, SCREEN_HEIGHT, BLACK, screen, False))
# # walls.add(Wall(0, 319, SCREEN_WIDTH, 10, BLACK, screen, True))

# pygame.sprite.spritecollideany(asterion, walls) == None
# collided = pygame.sprite.spritecollide(asterion, walls, False)
# platform = Asterion.get_platform(collided)

# def get_platform(collidelist):
#         for wall in collidelist:
#             if wall.platform:
#                 return wall
            

# c = pygame.sprite.spritecollide(asterion, walls, False)
# c
# print(c)

# for x in range(0,1440,360):
#     walls.add(Wall(x, 500, 100, 10, BLACK, screen))

# for x in range(180,1440,360):
#     walls.add(Wall(x, 600, 100, 10, BLACK, screen))

# walls.add(Wall(1000, 0, 10, SCREEN_HEIGHT, BLACK, screen))
# #walls.add(Wall(0, 0, SCREEN_WIDTH, 20, BLACK, screen))
# walls.add(Wall(0, 0, 20, SCREEN_HEIGHT, BLACK, screen))
# walls.add(Wall(0, 800, SCREEN_WIDTH, 20, BLACK, screen))


