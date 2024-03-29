import pygame
import pygame.display
import numpy as np
import pandas as pd
import random
import igraph as ig
from constants import *

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
    def __init__(self, screen, dim, doorsx, doorsy, wc,
    wallcolor, wallalpha, platformcolor, platformalpha, pathcolor, pathalpha, gatecolor, gatealpha):

        pygame.sprite.Sprite.__init__(self)
        self.dim = dim
        self.doorsx = doorsx
        self.doorsy = doorsy
        self.WC = wc
        self.g = ig.Graph.Lattice([dim,dim], circular=False)
        self.sp = ig.Graph()
        self.maze = pd.DataFrame()
        self.path = pd.DataFrame()
        self.platforms = pd.DataFrame()
        self.walls = pd.DataFrame()
        self.doors = pd.DataFrame()
        self.gate = pd.DataFrame()
        self.roomplatforms = pd.DataFrame()
        self.roomwalls = pd.DataFrame()
        self.roomdoors = pd.DataFrame()
        self.roompath = pd.DataFrame()
        self.roomgate = pd.DataFrame()
        self.pathgroup = pygame.sprite.Group()
        self.wallgroup = pygame.sprite.Group()
        self.platformgroup = pygame.sprite.Group()
        self.doorgroup = pygame.sprite.Group()
        self.gategroup = pygame.sprite.Group()
        self.wallcolor = wallcolor
        self.wallalpha = wallalpha
        self.platformcolor = platformcolor
        self.platformalpha = platformalpha
        self.pathcolor = pathcolor
        self.pathalpha = pathalpha
        self.gatecolor = gatecolor
        self.gatealpha = gatealpha
        self.screen = screen

    @staticmethod
    def mazeroombuild(dim, dx, dy):
        df = pd.DataFrame({'walla_x' : np.repeat(np.arange(0,dim+1), dim+1), 'walla_y' : np.tile(np.arange(0,dim+1), dim+1), 'doorx' : 0, 'doory' : 0})
        df = df.loc[~((df['walla_x']==dim) & (df['walla_y']==dim))]
        df.loc[df['walla_x'].isin(dx),'doorx'] = 1
        df.loc[df['walla_y']==dim,'doorx'] = 0
        df.loc[df['walla_y'].isin(dy),'doory'] = 1
        df.loc[df['walla_x']==dim,'doory'] = 0
        df['door'] = False
        df.loc[df['doorx'] + df['doory'] > 0, 'door'] = True
        
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

        dfroomdoors['WH'] = (SCREEN_HEIGHT / dfroomdoors['roomycount'])
        dfroomdoors['PW'] = (SCREEN_WIDTH / dfroomdoors['roomxcount'])

        return dfroomdoors


    def buildpath(self, vertex0, vertex1):
        vdf = self.g.get_vertex_dataframe()
        vdf.index.names = ['vertexid']
        vdf['vertex'] = vdf.index
        vdf['x'] = np.repeat(np.arange(0,self.dim),self.dim)
        vdf['y'] = np.tile(np.arange(0,self.dim),self.dim)

        edges = self.g.get_edge_dataframe()
        edges['eid'] = edges.index
        edges['st'] = list(zip(edges['source'], edges['target']))
        edges['st'] = edges['st'].apply(sorted)

        mst = self.g.spanning_tree(weights=self.g.es["weight"], return_tree=False)
        self.g.spanning_tree(weights=self.g.es["weight"], return_tree=True).get_edge_dataframe()

        edges['mst'] = edges.index.isin(mst)
        mstedges = edges.loc[edges['mst'], ['st']]['st']
        shortest_path = self.sp.get_shortest_paths(vertex0,vertex1, output="epath")

        sp_edge_df = self.sp.get_edge_dataframe()
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

        roomlookup = Maze.mazeroombuild(self.dim, self.doorsx, self.doorsy)

        mst = edges.loc[edges['mst']]
        mst = pd.merge(mst, roomlookup, left_on=['source_x', 'source_y', 'target_x', 'target_y'], right_on=['walla_x', 'walla_y', 'wallb_x', 'wallb_y'], how='left')

        mst['left'] = (mst['walla_rx'] * mst['PW']) + (mst['PW']/2)
        mst['top'] = (mst['walla_ry'] * mst['WH']) + (mst['WH']/2)

        mst['width'] = mst['PW']
        mst['height'] = self.WC
        mst.loc[mst['source_x']==mst['target_x'], 'width'] = self.WC
        mst.loc[mst['source_x']==mst['target_x'], 'height'] = mst['WH']+self.WC

        path = mst.loc[mst['path']]
        path = path.reset_index()

        sps = {value: index for index, value in enumerate(shortest_path[0])}

        path["sps"] = path["index"].map(sps)

        path = path.sort_values(by="sps").reset_index(drop=True)

        def swap_columns(path):
            s0 = path.iloc[0].loc["source"]
            s_x, s_y = path.iloc[0].loc["source_x"], path.iloc[0].loc["source_y"]
            
            if (s0 == path.iloc[1].loc["target"]) or (s0 == path.iloc[1].loc["source"]):
                path.loc[0, ["source"]] = path.iloc[0].loc["target"]
                path.loc[0, ["target"]] = s0
                path.loc[0, ["source_x", "source_y"]] = path.iloc[0].loc["target_x"], path.iloc[0].loc["target_y"]
                path.loc[0, ["target_x", "target_y"]] = s_x, s_y

            prev_target = path.iloc[0].loc["target"]

            for i in range(1, len(path)):
                s = path.iloc[i].loc["source"]
                s_x, s_y = path.iloc[i].loc["source_x"], path.iloc[i].loc["source_y"]

                if s != prev_target:
                    t = path.iloc[i].loc["target"]
                    t_x, t_y = path.iloc[i].loc["target_x"], path.iloc[i].loc["target_y"]

                    path.loc[i, ["source"]] = t
                    path.loc[i, ["target"]] = s
                    path.loc[i, ["source_x", "source_y"]] = t_x, t_y
                    path.loc[i, ["target_x", "target_y"]] = s_x, s_y

                prev_target = path.iloc[i].loc["target"]

            return path

        path = swap_columns(path)

        # s0 = path.iloc[0].loc["source"]
        # if (s0 == path.iloc[1].loc["target"]) or (s0 == path.iloc[1].loc["source"]):
        #     path.loc[0, ["source"]] = path.iloc[0].loc["target"]
        #     path.loc[0, ["target"]] = s0
        # prev_target = path.iloc[0].loc["target"]

        # for i in range(1, len(path)-1):
        #     s = path.iloc[i].loc["source"]
        #     if s != prev_target:
        #         t = path.iloc[i].loc["target"]
        #         path.loc[i, ["source"]] = t
        #         path.loc[i, ["target"]] = s
        #     prev_target = path.iloc[i].loc["target"]

        def v1(row):
            return pygame.Vector2((row['source_x'] * row['PW']) + (row['PW']/2), (row['source_y'] * row['WH']) + (row['WH']/2))

        def v2(row):
            return pygame.Vector2((row['target_x'] * row['PW']) + (row['PW']/2), (row['target_y'] * row['WH']) + (row['WH']/2))

        path['v1'] = path.apply(v1, axis=1)
        path['v2'] = path.apply(v2, axis=1)

        return path

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
        self.sp = ig.Graph([self.dim, self.dim], edges=mstedges)
        shortest_path = self.sp.get_shortest_paths(self.dim**2-self.dim,self.dim-1, output="epath")


        sp_edge_df = self.sp.get_edge_dataframe()
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

        roomlookup = Maze.mazeroombuild(self.dim, self.doorsx, self.doorsy)

        self.maze = pd.merge(self.maze, roomlookup, how='left')


        self.maze['width'], self.maze['height'] = self.WC, self.maze['WH'] + self.WC
        self.maze.loc[self.maze['Platform'], 'width'] = self.maze['PW']
        self.maze.loc[self.maze['Platform'], 'height'] = self.WC
        self.maze['left'] = self.maze['walla_rx'] * self.maze['PW']
        self.maze['top'] = (self.maze['walla_ry'] * self.maze['WH'])


        self.doors = self.maze.loc[self.maze['door']]
        self.doors = self.doors.reset_index()


        mst = edges.loc[edges['mst']]
        mst = pd.merge(mst, roomlookup, left_on=['source_x', 'source_y', 'target_x', 'target_y'], right_on=['walla_x', 'walla_y', 'wallb_x', 'wallb_y'], how='left')


        mst['left'] = (mst['walla_rx'] * mst['PW']) + (mst['PW']/2)
        mst['top'] = (mst['walla_ry'] * mst['WH']) + (mst['WH']/2)


        mst['width'] = mst['PW']
        mst['height'] = self.WC
        mst.loc[mst['source_x']==mst['target_x'], 'width'] = self.WC
        mst.loc[mst['source_x']==mst['target_x'], 'height'] = mst['WH']+self.WC


        self.path = mst.loc[mst['path']]
        self.path = self.path.reset_index()

        #self.gate = self.path.loc[self.path['source']==self.dim**2-self.dim]
        self.gate = self.path.sort_values(['eid']).iloc[[-1]].copy().reset_index()
        self.gate.loc[0, 'width'] = self.WC*2
        self.gate.loc[0, 'height'] = self.WC*2

        self.platforms = self.maze.loc[(self.maze['Platform']) & (~self.maze['door'])]
        self.platforms = self.platforms.sort_values(['roomx','walla_x','walla_y'])
        self.platforms = self.platforms.reset_index()
        self.walls = self.maze.loc[(~self.maze['Platform']) & ((~self.maze['door']))]
        self.walls = self.walls.sort_values(['roomx','walla_x','walla_y'])
        self.walls = self.walls.reset_index()


    def buildroom(self, asterion):

        def add_to_group(df, group, color, alpha):
            group.empty()
            df.apply(lambda row: group.add(Wall(row['left'], row['top'] + HEAD, row['width'] + WC, row['height']+WC, color, alpha, self.screen)), axis=1)

        def get_room(df, asterion):
            return df.loc[(df['roomx'] == asterion.rx) & (df['roomy'] == asterion.ry)]

        self.roomplatforms = get_room(self.platforms, asterion)
        add_to_group(self.roomplatforms, self.platformgroup, self.platformcolor, self.platformalpha)

        self.roomwalls = get_room(self.walls, asterion)
        add_to_group(self.roomwalls, self.wallgroup, self.wallcolor, self.wallalpha)

        self.roompath = get_room(self.path, asterion)
        add_to_group(self.roompath, self.pathgroup, self.pathcolor, self.pathalpha)

        self.roomgate = get_room(self.gate, asterion)
        add_to_group(self.roomgate, self.gategroup, self.gatecolor, self.gatealpha)

        # self.roomplatforms = self.platforms.loc[(self.platforms['roomx']==asterion.rx) & (self.platforms['roomy']==asterion.ry)]
        # self.platformgroup.empty()
        # self.roomplatforms.apply(lambda row: self.platformgroup.add(Wall(row['left'], row['top'], row['width'], row['height'], self.platformcolor, self.platformalpha, self.screen)), axis=1)

        # self.roomwalls = self.walls.loc[(self.walls['roomx']==asterion.rx) & (self.walls['roomy']==asterion.ry)]
        # self.wallgroup.empty()
        # self.roomwalls.apply(lambda row: self.wallgroup.add(Wall(row['left'], row['top'], row['width'], row['height'], self.wallcolor, self.wallalpha, self.screen)), axis=1)

        # self.roompath = self.path.loc[(self.path['roomx']==asterion.rx) & (self.path['roomy']==asterion.ry)]
        # self.pathgroup.empty()
        # self.roompath.apply(lambda row: self.pathgroup.add(Wall(row['left'], row['top'], row['width'], row['height'], self.pathcolor, self.pathalpha, self.screen)), axis=1)

        # self.roomgate = self.gate.loc[(self.gate['roomx']==asterion.rx) & (self.gate['roomy']==asterion.ry)]
        # self.gategroup.empty()
        # self.roomgate.apply(lambda row: self.gategroup.add(Wall(row['left'], row['top'], row['width'], row['height'], self.gatecolor, self.gatealpha, self.screen)), axis=1)


        roomdoorsy = self.doors.loc[(self.doors['doory']==1) & (self.doors['roomx'] == asterion.rx)]
        if len(roomdoorsy) != 0:
            roomdoorsy['ceiling'] = roomdoorsy['roomsy'].apply(lambda y: max(y) == asterion.ry)
            roomdoorsy['top'] = SCREEN_HEIGHT-WC+HEAD
            roomdoorsy.loc[roomdoorsy['ceiling'], 'top'] = 0
            roomdoorsy.apply(lambda row: self.platformgroup.add(Wall(row['left'], row['top'], row['width'], row['height'], self.platformcolor, self.platformalpha, self.screen)), axis=1)

        roomdoorsx = self.doors.loc[(self.doors['doorx']==1) & (self.doors['roomy'] == asterion.ry)]
        if len(roomdoorsx) != 0:
            roomdoorsx['ceiling'] = roomdoorsx['roomsx'].apply(lambda x: min(x) == asterion.rx)
            roomdoorsx['left'] = 0
            roomdoorsx.loc[roomdoorsx['ceiling'], 'left'] = SCREEN_WIDTH-WC
            roomdoorsx.apply(lambda row: self.wallgroup.add(Wall(row['left'], row['top'], row['width'], row['height'], self.wallcolor, self.wallalpha, self.screen)), axis=1)

        if asterion.ry == 0:
            self.platformgroup.add(Wall(0, HEAD, SCREEN_WIDTH, WC, self.platformcolor, self.platformalpha, self.screen))
        if asterion.ry == len(DOORSY):
            self.platformgroup.add(Wall(0, SCREEN_HEIGHT-WC+HEAD, SCREEN_WIDTH, WC, self.platformcolor, self.platformalpha, self.screen))
        if asterion.rx == 0:
            self.wallgroup.add(Wall(0, HEAD, WC, SCREEN_HEIGHT, self.wallcolor, self.wallalpha, self.screen))
        if asterion.rx == len(DOORSX):
            self.wallgroup.add(Wall(SCREEN_WIDTH-WC, HEAD, WC, SCREEN_HEIGHT, self.wallcolor, self.wallalpha, self.screen))