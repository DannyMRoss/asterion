import pygame
import pygame.display
import os



SCREEN_WIDTH=1440
SCREEN_HEIGHT=900
BLACK=(0,0,0)
SCREEN_BG=(50,50,50)
FLOOR=SCREEN_HEIGHT-500

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asterion")

asterion = Asterion("sprites/a.png", screen, 0, 0, 0, 0, 1, 20, 10)


clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False

    asterion.keys()
    asterion.physics()

    screen.fill((SCREEN_BG)) 
    asterion.draw(screen) 
    pygame.display.update()

    clock.tick(60)