import pygame
import pygame.display
import os
import numpy as np
import pandas as pd
import random
import igraph as ig


# constants
SCREEN_WIDTH=1000
SCREEN_HEIGHT=800
DIM=7
WC=10
SCALE=.3
BLACK=(0,0,0)
RED=(136,8,8)
WHITE=(196,170,35,10)
GREY=(52,60,36)
SCREEN_BG=(50,50,50)

class Asterion(pygame.sprite.Sprite):
    def __init__(self, img_path, screen, x, y, xv, yv, g, jf, speed, scale):
        pygame.sprite.Sprite.__init__(self)

        self.screen = screen
        self.xv = xv
        self.yv = yv
        self.image = pygame.image.load(img_path).convert_alpha()
        self.image = pygame.transform.scale_by(self.image, scale)
        self.image.set_colorkey(self.image.get_at((0,0)))
        self.rect = self.image.get_rect()
        #self.rect.scale_by_ip(scale)
        self.rect.move_ip([x,y])
        self.speed = speed
        self.g = g
        self.jf = jf
        self.shorthop = 5
        self.onplatform=False
        self.prevkey = pygame.key.get_pressed()
  
    @staticmethod
    def get_min_platform(collidelist):
            min_platform = collidelist[0]
            for p in collidelist:
                if p.rect.top > min_platform.rect.top:
                    min_platform = p
            return min_platform

    def get_closest_wall(self, collidelist):
            closest_wall = collidelist[0]
            closest_wall_dist = abs(self.rect.centerx - closest_wall.rect.centerx)
            for w in collidelist:
                if abs(self.rect.centerx - closest_wall.rect.centerx) < closest_wall_dist:
                    closest_wall = w
            return closest_wall
    
    
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

    def collidesprite(self, sprite, x, y):
        self.rect.move_ip([x,y])
        collided = pygame.sprite.collide_rect(self, sprite)
        self.rect.move_ip([-x,-y])
        return collided

    def collisionx(self, walls, x, y):
        self.rect.move_ip([x,y])
        collided = pygame.sprite.spritecollide(self, walls, False)
        self.rect.move_ip([-x,-y])
        if collided == []:
            return False
        closestwall = self.get_closest_wall(collided)
        if self.collidesprite(closestwall, 0, 1) or self.collidesprite(closestwall, 0, -1):
            return False
        # if self.
        # if (abs(self.rect.centerx - closestwall.rect.centerx) > WALL_BUFFER):
        #     return False
        else:
            return True

    def move(self, walls, platforms, x, y):
        dx = x
        dy = y

        while self.collisiony(platforms, 0, dy):
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
        if key[pygame.K_SPACE] and self.onplatform:
            self.yv = -self.jf

        if self.prevkey[pygame.K_SPACE] and not key[pygame.K_SPACE]:
            if self.yv < -self.shorthop:
                self.yv = -self.shorthop

        self.prevkey = key
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self, walls, platforms):
        self.onplatform = self.collisiony(platforms, 0, 1)
        self.keys()

        if not self.onplatform:
            self.yv += self.g

        if self.yv > 0 and self.onplatform:
            self.yv = 0

        self.move(walls, platforms, self.xv, self.yv)

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
    def __init__(self, dim, WC, wallcolor, platformcolor, pathcolor, screen):

        pygame.sprite.Sprite.__init__(self)
        self.dim = dim
        self.WC = WC
        self.g = ig.Graph.Lattice([dim,dim], circular=False)
        self.path = pd.DataFrame()
        self.platforms = pd.DataFrame()
        self.walls = pd.DataFrame()
        self.pathgroup = pygame.sprite.Group()
        self.wallgroup = pygame.sprite.Group()
        self.platformgroup = pygame.sprite.Group()
        self.wallcolor = wallcolor
        self.platformcolor = platformcolor
        self.pathcolor = pathcolor
        self.screen = screen

    
    def buildmaze(self):
        PW = SCREEN_WIDTH / self.dim
        WH = SCREEN_HEIGHT / self.dim

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
        shortest_path = sp.get_shortest_paths(0,self.dim**2-1, output="epath")

        sp_edge_df = sp.get_edge_dataframe()
        sp_edge_df['path'] = sp_edge_df.index.isin(shortest_path[0])
        sp_edge_df = sp_edge_df.loc[sp_edge_df['path'],:]
        sp_edge_df['st'] = list(zip(sp_edge_df['source'], sp_edge_df['target']))
        sp_verts = list(sp_edge_df['st'])

        @staticmethod
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
        maze["Platform"] = np.where(maze['source_x']==maze['target_x'], True, False)
        maze["walla_x"] = maze["source_x"]
        maze["walla_y"] = maze["source_y"] + 1
        maze["wallb_x"] = maze["target_x"] + 1
        maze["wallb_y"] = maze["target_y"]
        maze.loc[~maze["Platform"], "walla_x"] = maze["source_x"] + 1
        maze.loc[~maze["Platform"], "walla_y"] = maze["source_y"]
        maze.loc[~maze["Platform"], "wallb_x"] = maze["target_x"]
        maze.loc[~maze["Platform"], "wallb_y"] = maze["target_y"] + 1
        maze["left"] = maze["walla_x"]*PW
        maze["top"] = maze["walla_y"]*WH
        maze["width"] = np.where(maze['Platform'], PW, self.WC)
        maze["height"] = np.where(maze['Platform'], self.WC, WH+self.WC)

        mst["left"] = (mst["source_x"]*PW) + (PW/2)
        mst["top"] = (mst["source_y"]*WH) + (WH/2)
        mst["width"] = np.where(mst['source_x']!=mst['target_x'], PW, self.WC)
        mst["height"] = np.where(mst['source_x']!=mst['target_x'], self.WC, WH+self.WC)

        self.path = mst.loc[mst['mst']]
        self.path = self.path.reset_index()
        self.platforms = maze.loc[maze['Platform']]
        self.platforms = self.platforms.reset_index()
        self.walls = maze.loc[~maze['Platform']]
        self.walls = self.walls.reset_index()

        for index, i in self.platforms.iterrows():
            self.platformgroup.add(Wall(i['left'], i['top'], i['width'], i['height'], self.platformcolor, 255, self.screen))

        for index, i in self.walls.iterrows():
            self.wallgroup.add(Wall(i['left'], i['top'], i['width'], i['height'], self.wallcolor, 255, self.screen))

        for index, i in self.path.iterrows():
            self.pathgroup.add(Wall(i['left'], i['top'], i['width'], i['height'], self.pathcolor, 100, self.screen)) 


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asterion")


maze = Maze(DIM, WC, RED, RED, GREY, screen)
maze.buildmaze()

maze.platformgroup.add(Wall(0,SCREEN_HEIGHT-WC,SCREEN_WIDTH,WC,GREY,255, screen))
maze.platformgroup.add(Wall(0,0,SCREEN_WIDTH,WC,GREY,255, screen))
maze.wallgroup.add(Wall(0,0,WC,SCREEN_HEIGHT,GREY,255, screen))
maze.wallgroup.add(Wall(SCREEN_WIDTH-WC,0,WC,SCREEN_HEIGHT,GREY,255, screen))


asterion = Asterion("sprites/a0.png", screen, WC+WC, SCREEN_HEIGHT-(200)-WC, 0, 0, 1, 20, 10, SCALE) 

clock = pygame.time.Clock()
running=True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
    
    asterion.update(maze.wallgroup, maze.platformgroup)

    screen.fill(BLACK)
    maze.pathgroup.draw(screen)
    maze.platformgroup.draw(screen)
    maze.wallgroup.draw(screen)
    asterion.draw(screen)
    pygame.display.update()

    clock.tick(60)