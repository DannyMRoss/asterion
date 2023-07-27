import pygame
import pygame.display
import numpy as np
from constants import *

def mobhit(asterion, mobs, wall, platforms):
    collided = pygame.sprite.spritecollide(asterion, mobs, False)
    if collided != []:
        for mob in collided:
            asterion.health -= mob.damage
            mob.xv = -mob.xv
            mob.move(wall, platforms, 5, 0)
            asterion.rect.move_ip([mob.xpower*-np.sign(mob.xv),0])