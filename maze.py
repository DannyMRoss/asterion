import pygame
import numpy as np
import pandas as pd
import random
import igraph as ig

dim=100
SCREEN_WIDTH=1400
SCREEN_HEIGHT=900
PW = SCREEN_WIDTH / dim
WH = SCREEN_HEIGHT / dim
WC=1
g = ig.Graph.Lattice([dim,dim], circular=False)

vdf = g.get_vertex_dataframe()
vdf.index.names = ['vertexid']
vdf['vertex'] = vdf.index
        
vdf['x'] = np.repeat(np.arange(0,dim),dim)
vdf['y'] = np.tile(np.arange(0,dim),dim)

edges = g.get_edge_dataframe()
edges['eid'] = edges.index
edges['st'] = list(zip(edges['source'], edges['target']))
edges['st'] = edges['st'].apply(sorted)

g.es["weight"] = [random.randint(1, 77) for _ in g.es]     
mst = g.spanning_tree(weights=g.es["weight"], return_tree=False)
g.spanning_tree(weights=g.es["weight"], return_tree=True).get_edge_dataframe()

edges['mst'] = edges.index.isin(mst)
mstedges = edges.loc[edges['mst'], ['st']]['st']
sp = ig.Graph([dim, dim], edges=mstedges)
shortest_path = sp.get_shortest_paths(0,dim**2-1, output="epath")

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

mst = edges.loc[edges['mst'],]
maze = edges.loc[~edges['mst'],]
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
maze["width"] = np.where(maze['Platform'], PW, WC)
maze["height"] = np.where(maze['Platform'], WC, WH+WC)

mst["left"] = (mst["source_x"]*PW) + (PW/2)
mst["top"] = (mst["source_y"]*WH) + (WH/2)
mst["width"] = np.where(mst['source_x']!=mst['target_x'], PW, WC)
mst["height"] = np.where(mst['source_x']!=mst['target_x'], WC, WH+WC)

path = mst.loc[mst['path']]
path = path.reset_index()
platforms = maze.loc[maze['Platform']]
platforms = platforms.reset_index()
walls = maze.loc[~maze['Platform']]
walls = walls.reset_index()

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
        self.rect.left = self.x
        self.rect.top = self.y
        self.platform = platform

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asterion")

boundaries = pygame.sprite.Group()
pathgroup = pygame.sprite.Group()
wallgroup = pygame.sprite.Group()
platformgroup = pygame.sprite.Group()

boundaries.add(Wall(0,0,SCREEN_WIDTH,WC,(0,0,0),screen,False))
boundaries.add(Wall(0,0,WC,SCREEN_HEIGHT,(0,0,0),screen,False))
boundaries.add(Wall(0,SCREEN_HEIGHT-WC,SCREEN_WIDTH,WC,(0,0,0),screen,False))
boundaries.add(Wall(SCREEN_WIDTH-WC,0,WC,SCREEN_HEIGHT,(0,0,0),screen,False))

for index, p in platforms.iterrows():
    platformgroup.add(Wall(p['left'], p['top'], p['width'], p['height'], (0,0,0), screen, True))

for index, w in walls.iterrows():
    wallgroup.add(Wall(w['left'], w['top'], w['width'], w['height'], (0,0,0), screen, False))

for index, m in path.iterrows():
    pathgroup.add(Wall(m['left'], m['top'], m['width'], m['height'], (255,0,0), screen, False))    

clock = pygame.time.Clock()
running=True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
    
    screen.fill((255,255,255))
    boundaries.draw(screen)
    pathgroup.draw(screen)
    platformgroup.draw(screen)
    wallgroup.draw(screen)
    pygame.display.update()

    clock.tick(60)