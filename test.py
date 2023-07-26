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
SCREEN_HEIGHT=800
DIM=4
WC=5
SCALE=.3
BLACK=(0,0,0)
RED=(136,8,8)
WHITE=(196,170,35,10)
GREY=(50,50,50)
ORANGE=(229, 88, 7)
SCREEN_BG=(50,50,50)


def mazeroombuild2(dim, doorsx, doorsy):
    df = pd.DataFrame({'walla_x' : np.repeat(np.arange(0,dim), dim), 'walla_y' : np.tile(np.arange(0,dim), dim), 'doorx' : 0, 'doory' : 0})
    df.loc[df['walla_x'].isin(doorsx),'doorx'] = 1
    df.loc[df['walla_y'].isin(doorsy),'doory'] = 1
    df['door'] = False
    df.loc[df['doorx'] + df['doory'] > 0, 'door'] = True
    df['roomx'] = df.groupby('walla_y')['doorx'].cumsum()
    df['roomy'] = df.groupby('walla_x')['doory'].cumsum()
    df['roomsx'] = df.loc[df['doorx']==1, 'roomx'].apply(lambda x: [x-1, x])
    df['roomsy'] = df.loc[df['doory']==1, 'roomy'].apply(lambda x: [x-1, x])
    df['walla_rx'] = df.groupby(['roomx', 'walla_y']).cumcount()
    df['walla_ry'] = df.groupby(['roomy', 'walla_x']).cumcount()
    df['roomxcount'] = df.groupby('roomx')['walla_x'].transform('nunique')
    df['roomycount'] = df.groupby('roomy')['walla_y'].transform('nunique')
    df['WH'] = (SCREEN_HEIGHT / df['roomycount'])
    df['PW'] = (SCREEN_WIDTH / df['roomxcount'])


    roomdf = df.loc[~df['door']]
    roomplatformsdf = roomdf.copy()
    roomplatformsdf['wallb_x'] = roomplatformsdf['walla_x']
    roomplatformsdf['wallb_y'] = roomplatformsdf['walla_y'] + 1
    roomwallsdf = roomdf.copy()
    roomwallsdf['wallb_x'] = roomwallsdf['walla_x'] + 1
    roomwallsdf['wallb_y'] = roomwallsdf['walla_y']
    doorsx = df.loc[df['doorx']==1]
    doorsx['wallb_x'] = doorsx['walla_x']
    doorsx['wallb_y'] = doorsx['walla_y'] + 1
    doorsx['doory'] = 0
    doorsx['roomsy'] = np.nan
    doorsy = df.loc[df['doory']==1]
    doorsy['wallb_x'] = doorsy['walla_x'] + 1
    doorsy['wallb_y'] = doorsy['walla_y']
    doorsy['doorx'] = 0
    doorsy['roomsx'] = np.nan
    dfroomdoors = pd.concat([roomplatformsdf, roomwallsdf, doorsx, doorsy], ignore_index=True, axis=0)


    return dfroomdoors

def mazeroombuild(dim, dx, dy):
    df = pd.DataFrame({'walla_x' : np.repeat(np.arange(0,dim+1), dim+1), 'walla_y' : np.tile(np.arange(0,dim+1), dim+1), 'doorx' : 0, 'doory' : 0})
    df = df.loc[~((df['walla_x']==dim) & (df['walla_y']==dim))]
    df.loc[df['walla_x'].isin(dx),'doorx'] = 1
    df.loc[df['walla_y']==dim,'doorx'] = 0
    df.loc[df['walla_y'].isin(dy),'doory'] = 1
    df.loc[df['walla_x']==dim,'doory'] = 0
    df['door'] = False
    df.loc[df['doorx'] + df['doory'] > 0, 'door'] = True

    #roomdf = df.loc[~df['door']]
    
    roomplatformsdf = df.copy()
    roomplatformsdf = roomplatformsdf.loc[df['doory']==0]
    roomplatformsdf['wallb_x'] = roomplatformsdf['walla_x'] + 1
    roomplatformsdf['wallb_y'] = roomplatformsdf['walla_y']
    roomplatformsdf = roomplatformsdf.loc[roomplatformsdf['walla_x']!=dim]
    roomplatformsdf['type'] = "platform"
    roomplatformsdf['doorx'] = 0
    roomplatformsdf['door'] = False
    
    roomwallsdf = df.copy()
    roomwallsdf = roomwallsdf.loc[df['doorx']==0]
    roomwallsdf['wallb_x'] = roomwallsdf['walla_x']
    roomwallsdf['wallb_y'] = roomwallsdf['walla_y'] + 1
    roomwallsdf = roomwallsdf.loc[roomwallsdf['walla_y']!=dim]
    roomwallsdf['type'] = "wall"
    roomwallsdf['doory'] = 0
    roomwallsdf['door'] = False
    
    doorsx = df.copy()
    doorsx = doorsx.loc[df['doorx']==1]
    doorsx['wallb_x'] = doorsx['walla_x']
    doorsx['wallb_y'] = doorsx['walla_y'] + 1
    doorsx['doory'] = 0
    doorsx['roomsy'] = np.nan
    doorsx['type'] = "wall"
    
    doorsy = df.copy()
    doorsy = doorsy.loc[df['doory']==1]
    doorsy['wallb_x'] = doorsy['walla_x'] + 1
    doorsy['wallb_y'] = doorsy['walla_y']
    doorsy['doorx'] = 0
    doorsy['roomsx'] = np.nan
    doorsy['type'] = "platform"
    
    dfroomdoors = pd.concat([roomplatformsdf, roomwallsdf, doorsx, doorsy], ignore_index=True, axis=0)

    
    def countdoors(x, doors):
        return sum(x >= d for d in doors)

    dfroomdoors['roomx'] = dfroomdoors['walla_x'].apply(lambda x: countdoors(x, dx))
    dfroomdoors['roomy'] = dfroomdoors['walla_y'].apply(lambda x: countdoors(x, dy))
    dfroomdoors['roomsx'] = dfroomdoors.loc[dfroomdoors['doorx']==1, 'roomx'].apply(lambda x: [x-1, x])
    dfroomdoors['roomsy'] = dfroomdoors.loc[dfroomdoors['doory']==1, 'roomy'].apply(lambda x: [x-1, x])
    

    dfroomdoors['walla_rx'] = (dfroomdoors.groupby('roomx')['walla_x'].rank(method='dense') - 1).astype(int)
    dfroomdoors['walla_ry'] = (dfroomdoors.groupby('roomy')['walla_y'].rank(method='dense') - 1).astype(int)

    dfroomdoors['roomxcount'] = dfroomdoors.loc[dfroomdoors['type']=="platform"].groupby('roomx')['walla_x'].transform('nunique') 
    dfroomdoors['roomycount'] = dfroomdoors.loc[dfroomdoors['type']=="wall"].groupby('roomy')['walla_y'].transform('nunique') 

    dfroomdoors['roomxcount'] = dfroomdoors.groupby('roomx')['roomxcount'].ffill().bfill()
    dfroomdoors['roomycount'] = dfroomdoors.groupby('roomy')['roomycount'].ffill().bfill()

    # dfroomdoors['roomxcount'] = dfroomdoors.groupby('roomx')['walla_x'].transform('nunique')
    # dfroomdoors['roomycount'] = dfroomdoors.groupby('roomy')['walla_y'].transform('nunique')
    dfroomdoors['WH'] = (SCREEN_HEIGHT / dfroomdoors['roomycount'])
    dfroomdoors['PW'] = (SCREEN_WIDTH / dfroomdoors['roomxcount'])

    return dfroomdoors



ROOMSX=2
ROOMSY=2
df = mazeroombuild(DIM, [2], [2])
#df2 = mazeroombuild(2, [6], [6])


class Asterion(pygame.sprite.Sprite):
    def __init__(self, img_path, scale, screen, rx, ry, x, y, xv, yv, g, jf, shorthop, speed):
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
        #   return False
        # elif (self.rect.centerx <= minplatform.rect.left or self.rect.centerx >= minplatform.rect.right):
        #   return False
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
    def __init__(self, screen, dim, roomlookup, wc,
    wallcolor, wallalpha, platformcolor, platformalpha, pathcolor, pathalpha):

        pygame.sprite.Sprite.__init__(self)
        self.dim = dim
        self.roomlookup = roomlookup
        self.WC = wc
        self.g = ig.Graph.Lattice([dim,dim], circular=False)
        self.maze = pd.DataFrame()
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

        self.maze = edges.copy()
        self.maze =  self.maze.loc[~self.maze['mst']]
        self.maze['Platform'] = False
        self.maze.loc[self.maze['source_x'] == self.maze['target_x'], 'Platform'] = True
        self.maze['walla_x'], self.maze['walla_y'] = self.maze['source_x'], self.maze['source_y'] + 1
        self.maze['wallb_x'], self.maze['wallb_y'] = self.maze['target_x'] + 1, self.maze['target_y']
        self.maze.loc[~self.maze['Platform'], 'walla_x'] = self.maze['source_x'] + 1
        self.maze.loc[~self.maze['Platform'], 'walla_y'] = self.maze['source_y']
        self.maze.loc[~self.maze['Platform'], 'wallb_x'] = self.maze['target_x']
        self.maze.loc[~self.maze['Platform'], 'wallb_y'] = self.maze['target_y'] + 1


        self.maze = pd.merge(self.maze, self.roomlookup, how='left')


        self.maze['width'], self.maze['height'] = self.WC, self.maze['WH'] + self.WC
        self.maze.loc[self.maze['Platform'], 'width'] = self.maze['PW']
        self.maze.loc[self.maze['Platform'], 'height'] = self.WC
        self.maze['left'] = self.maze['walla_rx'] * self.maze['PW']
        self.maze['top'] = self.maze['walla_ry'] * self.maze['WH']


        self.doors = self.maze.loc[self.maze['door']]
        self.doors = self.doors.reset_index()


        mst = edges.loc[edges['mst']]
        mst = pd.merge(mst, self.roomlookup, left_on=['source_x', 'source_y', 'target_x', 'target_y'], right_on=['walla_x', 'walla_y', 'wallb_x', 'wallb_y'], how='left')


        mst['left'] = (mst['walla_rx'] * mst['PW']) + (mst['PW']/2)
        mst['top'] = (mst['walla_ry'] * mst['WH']) + (mst['WH']/2)


        mst['width'] = mst['PW']
        mst['height'] = self.WC
        mst.loc[mst['source_x']==mst['target_x'], 'width'] = self.WC
        mst.loc[mst['source_x']==mst['target_x'], 'height'] = mst['WH']+self.WC


        self.path = mst.loc[mst['path']]
        self.path = self.path.reset_index()
        self.platforms = self.maze.loc[(self.maze['Platform']) & (~self.maze['door'])]
        self.platforms = self.platforms.sort_values(['roomx','walla_x','walla_y'])
        self.platforms = self.platforms.reset_index()
        self.walls = self.maze.loc[(~self.maze['Platform']) & ((~self.maze['door']))]
        self.walls = self.walls.sort_values(['roomx','walla_x','walla_y'])
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
        roomdoorsy = self.doors.loc[(self.doors['doory']==1) & (self.doors['roomx'] == asterion.rx)]
        if len(roomdoorsy) != 0:
            roomdoorsy['ceiling'] = roomdoorsy['roomsy'].apply(lambda y: max(y) == asterion.ry)
            roomdoorsy['top'] = SCREEN_HEIGHT-WC
            roomdoorsy.loc[roomdoorsy['ceiling'], 'top'] = 0
            roomdoorsy.apply(lambda row: self.platformgroup.add(Wall(row['left'], row['top'], row['width'], row['height'], self.platformcolor, self.platformalpha, self.screen)), axis=1)


        # roomy set, top is set, config left
        roomdoorsx = self.doors.loc[(self.doors['doorx']==1) & (self.doors['roomy'] == asterion.ry)]
        if len(roomdoorsx) != 0:
            roomdoorsx['ceiling'] = roomdoorsx['roomsx'].apply(lambda x: min(x) == asterion.rx)
            roomdoorsx['left'] = 0
            roomdoorsx.loc[roomdoorsx['ceiling'], 'left'] = SCREEN_WIDTH-WC
            roomdoorsx.apply(lambda row: self.wallgroup.add(Wall(row['left'], row['top'], row['width'], row['height'], self.wallcolor, self.wallalpha, self.screen)), axis=1)


        # if asterion.ry == 0:
        #     self.platformgroup.add(Wall(0, 0, SCREEN_WIDTH, WC, self.platformcolor, self.platformalpha, self.screen))
        # if asterion.ry == ROOMSY-1:
        #     self.platformgroup.add(Wall(0, SCREEN_HEIGHT-WC, SCREEN_WIDTH, WC, self.platformcolor, self.platformalpha, self.screen))
        # if asterion.rx == 0:
        #     self.wallgroup.add(Wall(0, 0, WC, SCREEN_HEIGHT, self.wallcolor, self.wallalpha, self.screen))
        # if asterion.rx == ROOMSX-1:
        #     self.wallgroup.add(Wall(SCREEN_WIDTH-WC, 0, WC, SCREEN_HEIGHT, self.wallcolor, self.wallalpha, self.screen))




pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Consolas', 30)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asterion")


maze = Maze(screen=screen, dim=DIM, roomlookup=df, wc=WC, wallcolor=RED, wallalpha=255, platformcolor=RED, platformalpha=255, pathcolor=ORANGE, pathalpha=200)

maze.buildmaze()

asterion = Asterion(img_path="sprites/a0.png", scale=SCALE, screen=screen, rx=0, ry=0, x=2*WC, y=SCREEN_HEIGHT-(2*WC), xv=0, yv=0, g=1, jf=35, shorthop=5, speed=25)




#clock = pygame.time.Clock()
# running=True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             pygame.quit()
#             running = False
    
#     screen.fill(BLACK)


#     maze.buildroom(asterion)
#     asterion.update(maze.wallgroup, maze.platformgroup, maze.pathgroup)


#     maze.platformgroup.draw(screen)
#     maze.wallgroup.draw(screen)
#     asterion.hitpaths.draw(screen)
#     asterion.draw(screen)


#     pygame.display.flip()
#     clock.tick(60)