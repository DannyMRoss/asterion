import pygame
import pygame.display
import os
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import random
import igraph as ig

from asterion import *
from maze import *
from constants import *
from mobs import *
from combat import *


pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT+HEAD))
pygame.display.set_caption("Asterion")

def text(text, font, color):
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()

title = pygame.font.SysFont('Zapfino', 60, bold=True)
subtitle = pygame.font.SysFont('Consolas', 30, bold=True, italic=True)
quote = pygame.font.SysFont('Zapfino', 30, bold=True, italic=True)
sital = pygame.font.SysFont('Consolas', 10, bold=True, italic=True)


maze = Maze(screen=screen, dim=DIM, doorsx=DOORSX, doorsy=DOORSY, wc=WC, wallcolor=VIOLET, wallalpha=255, platformcolor=VIOLET, platformalpha=255, pathcolor=GREY, pathalpha=100, gatecolor=WHITE, gatealpha=255)

maze.buildmaze()

asterion = Asterion(screen=screen, img_path="sprites/a0.png", 
                    scale=SCALE, rx=0, ry=len(DOORSY), x=STARTX, y=STARTY, xv=0, yv=0, g=1, jf=35, shorthop=2, speed=10, health=5, quiver=50)

mobs = pygame.sprite.Group()
#mobs.add(Walker())
f = Flyer(maze=maze)
print(f.path)
print(f.X)
mobs.add(f)

def start_menu():

    intro = True
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    intro = False
                
        screen.fill(BLACK)
        TextSurf, TextRect = text("Asterion", title, VIOLET)
        TextSurf2, TextRect2 = text("Press Enter", subtitle, WHITE)
        TextRect.center = ((SCREEN_WIDTH/2),(SCREEN_HEIGHT/2))
        TextRect2.center = ((SCREEN_WIDTH/2),((SCREEN_HEIGHT+30)/2))
        screen.blit(TextSurf, TextRect)
        screen.blit(TextSurf2, TextRect2)
        pygame.display.flip()

def death():

    death = True
    while death:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    death = False

        screen.fill(BLACK)
        TextSurf, TextRect = text("\"Would you believe it? ... The Minotaur scarcely defended himself.\"", quote, VIOLET)
        TextRect.center = ((SCREEN_WIDTH/2),(SCREEN_HEIGHT/2))
        screen.blit(TextSurf, TextRect)

        TextSurf2, TextRect2 = text("Mazes: "+str(asterion.levels), subtitle, WHITE)
        TextRect2.midtop = TextRect.midbottom
        screen.blit(TextSurf2, TextRect2)

        pygame.display.flip()


def stats():
    TextSurf, TextRect = text("Mazes: "+str(asterion.levels), sital, WHITE)
    TextRect.bottomleft = (WC,HEAD)
    screen.blit(TextSurf, TextRect)

    TextSurf2, TextRect2 = text("Health: "+str(asterion.health), sital, WHITE)
    TextRect2.topright = (SCREEN_WIDTH, 0)
    screen.blit(TextSurf2, TextRect2)

    TextSurf3, TextRect3 = text("Arrows: "+str(asterion.quiver), sital, WHITE)
    TextRect3.midtop = (SCREEN_WIDTH/2, 0)
    screen.blit(TextSurf3, TextRect3)

    TextSurf4, TextRect4 = text(" -- Hits: "+str(asterion.ahits), sital, WHITE)
    TextRect4.left, TextRect4.top = TextRect3.right, 0
    screen.blit(TextSurf4, TextRect4)



def game_loop():
    clock = pygame.time.Clock()
    running=True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
        
        screen.fill(BLACK)

        if asterion.new_level:
            screen.fill(GREY)
            mobs.empty()
            maze.buildmaze()
            asterion.new_level = False
            mobs.add(Flyer(maze))
            
        maze.buildroom(asterion)
        
        asterion.update(maze.wallgroup, maze.platformgroup, maze.pathgroup, maze.gategroup)
        #mobs.update(maze.wallgroup, maze.platformgroup)
        mobs.update()
        mobs.draw(screen)
        flyerhit(asterion, mobs)
        mobarrow(mobs, asterion)

        maze.platformgroup.draw(screen)
        maze.wallgroup.draw(screen)
        maze.gategroup.draw(screen)
       #asterion.hitpaths.draw(screen)
        asterion.hitpaths.empty()
        asterion.draw(screen)

        

        stats()
        
        if asterion.health <= 0:
            death()

        pygame.display.flip()
        clock.tick(60)

start_menu()
game_loop()
