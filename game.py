import pygame
import pygame.display
import os
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas

import pandas as pd
import random
import igraph as ig


# constants
SCREEN_WIDTH=1000
SCREEN_HEIGHT=1000
DIM=8
ROOMSX = 2
ROOMSY = 2
MAZE_WIDTH = SCREEN_WIDTH * ROOMSX
MAZE_HEIGHT = SCREEN_HEIGHT * ROOMSY
WC=10
SCALE=.5
BLACK=(0,0,0)
RED=(136,8,8)
WHITE=(196,170,35,10)
GREY=(50,50,50)
ORANGE=(229, 88, 7)
SCREEN_BG=(50,50,50)


class Asterion(pygame.sprite.Sprite):
    def __init__(self, 
                img_path, scale, screen,
                rx, ry, x, y, 
                xv, yv, g, jf, shorthop, speed):
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
        #     return False
        # elif (self.rect.centerx <= minplatform.rect.left or self.rect.centerx >= minplatform.rect.right):
        #     return False
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


    def move(self, walls, platforms, path, x, y):
        dx = x
        dy = y

        while self.collisiony(platforms, 0, dy):
            dy -= np.sign(dy)

        while self.collisionx(walls, dx, 0):
            dx -= np.sign(dx)

        self.rect.move_ip([dx, dy])
        self.pathcollision(path)
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
            self.rect.move_ip(0,SCREEN_HEIGHT)
        if self.rect.top > SCREEN_HEIGHT:
            self.ry += 1
            self.hitpaths.empty()
            self.rect.move_ip(0,-SCREEN_HEIGHT)
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


    def update(self, walls, platforms, path):
        self.onplatform = self.collisiony(platforms, 0, 1)
        self.keys()

        if not self.onplatform:
            self.yv += self.g

        if self.yv > 0 and self.onplatform:
            self.yv = 0

        self.move(walls, platforms, path, self.xv, self.yv)

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color, alpha, screen):

        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.h = h
        self.w = w
        self.color = color
        self.screen = screen
        self.image = pygame.Surface([self.w, self.h])
        self.image.fill(self.color)
        self.image.set_alpha(alpha)
        self.rect = self.image.get_rect()
        self.rect.left = self.x
        self.rect.top = self.y

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

class Maze(pygame.sprite.Sprite):
    def __init__(self, screen, dim, roomsx, roomsy, wc, 
                 wallcolor, wallalpha, platformcolor, platformalpha, pathcolor, pathalpha):

        pygame.sprite.Sprite.__init__(self)
        self.dim = dim
        self.roomsx = roomsx
        self.roomsy = roomsy
        self.PW = SCREEN_WIDTH / (self.dim  / self.roomsx)
        self.WH = SCREEN_HEIGHT / (self.dim  / self.roomsx)
        self.WC = wc
        self.g = ig.Graph.Lattice([dim,dim], circular=False)
        self.path = pd.DataFrame()
        self.platforms = pd.DataFrame()
        self.walls = pd.DataFrame()
        self.doors = pd.DataFrame()
        self.roomplatforms = pd.DataFrame()
        self.roomwalls = pd.DataFrame()
        self.roomdoors = pd.DataFrame()
        self.roompath = pd.DataFrame()
        self.pathgroup = pygame.sprite.Group()
        self.wallgroup = pygame.sprite.Group()
        self.platformgroup = pygame.sprite.Group()
        self.doorgroup = pygame.sprite.Group()
        self.wallcolor = wallcolor
        self.wallalpha = wallalpha
        self.platformcolor = platformcolor
        self.platformalpha = platformalpha
        self.pathcolor = pathcolor
        self.pathalpha = pathalpha
        self.screen = screen

    
    def buildmaze(self):

        vdf = self.g.get_vertex_dataframe()
        vdf.index.names = ['vertexid']
        vdf['vertex'] = vdf.index
                
        vdf['x'] = np.repeat(np.arange(0,self.dim),self.dim)
        vdf['y'] = np.tile(np.arange(0,self.dim),self.dim)

        edges = self.g.get_edge_dataframe()
        edges['eid'] = edges.index
        edges['st'] = list(zip(edges['source'], edges['target']))
        edges['st'] = edges['st'].apply(sorted)

        self.g.es["weight"] = [random.randint(1, 77) for _ in self.g.es]     
        mst = self.g.spanning_tree(weights=self.g.es["weight"], return_tree=False)
        self.g.spanning_tree(weights=self.g.es["weight"], return_tree=True).get_edge_dataframe()

        edges['mst'] = edges.index.isin(mst)
        mstedges = edges.loc[edges['mst'], ['st']]['st']
        sp = ig.Graph([self.dim, self.dim], edges=mstedges)
        shortest_path = sp.get_shortest_paths(self.dim**2-self.dim,self.dim-1, output="epath")

        sp_edge_df = sp.get_edge_dataframe()
        sp_edge_df['path'] = sp_edge_df.index.isin(shortest_path[0])
        sp_edge_df = sp_edge_df.loc[sp_edge_df['path'],:]
        sp_edge_df['st'] = list(zip(sp_edge_df['source'], sp_edge_df['target']))
        sp_verts = list(sp_edge_df['st'])

        def in_sp(v): 
            return tuple(v) in sp_verts
        
        edges['path'] = edges['st'].apply(in_sp)

        edges = pd.merge(edges, vdf, how='left', left_on='source', right_on='vertex')
        edges = edges.rename(columns={'x': 'source_x', 'y': 'source_y'})
        edges = pd.merge(edges, vdf, how='left', left_on='target', right_on='vertex')
        edges = edges.rename(columns={'x': 'target_x', 'y': 'target_y'})
        edges = edges.drop(columns=['vertex_x', 'vertex_y'])

        mst = edges.loc[edges['mst']]
        maze = edges.loc[~edges['mst']]
        maze['Platform'] = np.where(maze['source_x']==maze['target_x'], True, False)
        maze['walla_x'] = maze['source_x']
        maze['walla_y'] = maze['source_y'] + 1
        maze['wallb_x'] = maze['target_x'] + 1
        maze['wallb_y'] = maze['target_y']
        maze.loc[~maze['Platform'], 'walla_x'] = maze['source_x'] + 1
        maze.loc[~maze['Platform'], 'walla_y'] = maze['source_y']
        maze.loc[~maze['Platform'], 'wallb_x'] = maze['target_x']
        maze.loc[~maze['Platform'], 'wallb_y'] = maze['target_y'] + 1
        
        maze['roomx'] = np.where(maze['walla_x'] <  (self.dim  / self.roomsx), 0, 1)
        maze['roomy'] = np.where(maze['walla_y'] <  (self.dim  / self.roomsy), 0, 1)

        maze['doorx'] = False
        maze['doory'] = False
        maze.loc[((maze['Platform']) & (maze['walla_y']==(self.dim  / self.roomsy))), 'doory'] = True 
        maze.loc[((~maze['Platform']) & (maze['walla_x']==(self.dim  / self.roomsx))), 'doorx'] = True 

        maze['door'] = False
        maze.loc[(maze['doorx']) | (maze['doory']), 'door'] = True

        maze['width'] = np.where(maze['Platform'], self.PW, WC)
        maze['height'] = np.where(maze['Platform'], WC, self.WH+WC)
        maze['left'] = (maze['walla_x'] - ((self.dim / self.roomsx) * maze['roomx'])) * self.PW
        maze['top'] = (maze['walla_y'] - ((self.dim / self.roomsy) * maze['roomy'])) * self.WH

        self.doors = maze.loc[maze['door']]
        self.doors = self.doors.reset_index()

        # update for dim!
        self.doors['roomsx'] = self.doors['doorx'].apply(lambda x: [0, self.roomsx-1] if x else np.nan)
        self.doors['roomsy'] = self.doors['doory'].apply(lambda y: [0, self.roomsy-1] if y else np.nan)


        mst['roomx'] = np.where(mst['source_x'] <  (self.dim  / self.roomsx), 0, 1)
        mst['roomy'] = np.where(mst['source_y'] <  (self.dim  / self.roomsy), 0, 1)

        mst['left'] = ((mst['source_x'] - ((self.dim / self.roomsx) * mst['roomx'])) * self.PW) + (self.PW/2)
        mst['top'] = ((mst['source_y'] - ((self.dim / self.roomsy) * mst['roomy'])) * self.WH) + (self.WH/2)

        mst['width'] = np.where(mst['source_x']!=mst['target_x'], self.PW, self.WC)
        mst['height'] = np.where(mst['source_x']!=mst['target_x'], self.WC, self.WH+self.WC)
  

        self.path = mst.loc[mst['path']]
        self.path = self.path.reset_index()
        self.platforms = maze.loc[(maze['Platform']) & (~maze['door'])]
        self.platforms = self.platforms.reset_index()
        self.walls = maze.loc[(~maze['Platform']) & ((~maze['door']))]
        self.walls = self.walls.reset_index()
        

    def buildroom(self, asterion):

        self.roomplatforms = self.platforms.loc[(self.platforms['roomx']==asterion.rx) & (self.platforms['roomy']==asterion.ry)]
        self.platformgroup.empty()
        self.roomplatforms.apply(lambda row: self.platformgroup.add(Wall(row['left'], row['top'], row['width'], row['height'], self.platformcolor, self.platformalpha, self.screen)), axis=1)

        self.roomwalls = self.walls.loc[(self.walls['roomx']==asterion.rx) & (self.walls['roomy']==asterion.ry)]
        self.wallgroup.empty()
        self.roomwalls.apply(lambda row: self.wallgroup.add(Wall(row['left'], row['top'], row['width'], row['height'], self.wallcolor, self.wallalpha, self.screen)), axis=1)

        self.roompath = self.path.loc[(self.path['roomx']==asterion.rx) & (self.path['roomy']==asterion.ry)]
        self.pathgroup.empty()
        self.roompath.apply(lambda row: self.pathgroup.add(Wall(row['left'], row['top'], row['width'], row['height'], self.pathcolor, self.pathalpha, self.screen)), axis=1)


        #ceilings and floors, roomx set, left is set, config top
        roomdoorsy = self.doors.loc[(self.doors['Platform']) & (self.doors['roomx'] == asterion.rx)]
        if len(roomdoorsy) != 0:
            roomdoorsy['ceiling'] = roomdoorsy['roomsy'].apply(lambda y: max(y) == asterion.ry)   
            roomdoorsy['top'] = np.where(roomdoorsy['ceiling'], 0, SCREEN_HEIGHT-WC)
            roomdoorsy.apply(lambda row: self.platformgroup.add(Wall(row['left'], row['top'], row['width'], row['height'], self.platformcolor, self.platformalpha, self.screen)), axis=1)


        # roomy set, top is set, config left
        roomdoorsx = self.doors.loc[(~self.doors['Platform']) & (self.doors['roomy'] == asterion.ry)]
        if len(roomdoorsx) != 0:
            roomdoorsx['ceiling'] = roomdoorsx['roomsx'].apply(lambda x: min(x) == asterion.rx)   
            roomdoorsx['left'] = np.where(roomdoorsx['ceiling'], SCREEN_WIDTH-WC, 0)
            roomdoorsx.apply(lambda row: self.wallgroup.add(Wall(row['left'], row['top'], row['width'], row['height'], self.wallcolor, self.wallalpha, self.screen)), axis=1) 


        if asterion.ry == 0:
            maze.platformgroup.add(Wall(0, 0, SCREEN_WIDTH, WC, self.platformcolor, self.platformalpha, self.screen))
        if asterion.ry == ROOMSY-1:
            maze.platformgroup.add(Wall(0, SCREEN_HEIGHT-WC, SCREEN_WIDTH, WC, self.platformcolor, self.platformalpha, self.screen))
        if asterion.rx == 0:
            maze.wallgroup.add(Wall(0, 0, WC, SCREEN_HEIGHT, self.wallcolor, self.wallalpha, self.screen))
        if asterion.rx == ROOMSX-1:
            maze.wallgroup.add(Wall(SCREEN_WIDTH-WC, 0, WC, SCREEN_HEIGHT, self.wallcolor, self.wallalpha, self.screen))


pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Consolas', 30)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asterion")

maze = Maze(screen=screen, dim=DIM, roomsx=ROOMSX, roomsy=ROOMSY, wc=WC, wallcolor=RED, wallalpha=255, platformcolor=RED, platformalpha=255, pathcolor=ORANGE, pathalpha=200)

maze.buildmaze()


asterion = Asterion(img_path="sprites/a0.png", scale=SCALE, screen=screen, rx=0, ry=1, x=2*WC, y=SCREEN_HEIGHT-(2*WC), xv=0, yv=0, g=1, jf=35, shorthop=10, speed=30)


clock = pygame.time.Clock()
running=True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
    
    screen.fill(BLACK)

    
    
    maze.buildroom(asterion)
    asterion.update(maze.wallgroup, maze.platformgroup, maze.pathgroup)

        
    maze.platformgroup.draw(screen)
    maze.wallgroup.draw(screen)
    asterion.hitpaths.draw(screen)
    asterion.draw(screen)
    
    

    pygame.display.flip()
    clock.tick(60)  