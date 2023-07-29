import pygame
import pygame.display
import numpy as np
from constants import *

def flyerhit(asterion, flyers):
    collided = pygame.sprite.spritecollide(asterion, flyers, False)
    if collided != []:
        for mob in collided:
            mob.hit(asterion)

def mobhit(asterion, mobs, walls, platforms):
    collided = pygame.sprite.spritecollide(asterion, mobs, False)
    if collided != []:
        for mob in collided:
            mob.hit(asterion, walls, platforms)

def mobarrow(mobs, asterion):
    collided = pygame.sprite.groupcollide(mobs, asterion.arrows, False, True)
    for mob, arrow in collided.items():
        for a in arrow:
            if a.xv + a.yv != 0:
                mob.health -= a.damage
                asterion.ahits+=1
            if mob.health<=0:
                mob.kill()