import numpy as np
import pandas as pd
import random
import igraph as ig

dim=5
vertex_df = pd.DataFrame({'ID':np.arange(0,dim**2),
                          'xID':np.repeat(np.arange(0,dim),dim),
                          'yID':np.tile(np.arange(0,dim),dim)})

g = ig.Graph.Lattice([dim,dim], circular=False)
edges = g.get_edge_dataframe()
edges['eid'] = edges.index
edges['st'] = list(zip(edges['source'], edges['target']))
edges['st'] = edges['st'].apply(sorted)

g.es["weight"] = [random.randint(1, 77) for _ in g.es]     
mst = g.spanning_tree(weights=g.es["weight"], return_tree=False)
g.spanning_tree(weights=g.es["weight"], return_tree=True).get_edge_dataframe()

edges['mst'] = edges.index.isin(mst)
mstedges = edges.loc[edges['mst'], ['st']]['st']
sp = ig.Graph(dim**2 - 1, edges=mstedges)
shortest_path = sp.get_shortest_paths(0,dim**2-1, output="epath")

sp_edge_df = sp.get_edge_dataframe()
sp_edge_df['path'] = sp_edge_df.index.isin(shortest_path[0])
sp_edge_df = sp_edge_df.loc[sp_edge_df['path'],:]
sp_edge_df['st'] = list(zip(sp_edge_df['source'], sp_edge_df['target']))
sp_verts = list(sp_edge_df['st'])

def in_sp(v): 
    return tuple(v) in sp_verts

edges['path'] = edges['st'].apply(in_sp)

sp = mstree.get_shortest_paths(0,, output="epath")

mst_edges = edge_pairs.loc[edge_pairs['mst'], ['ab']]  
mst_edges = mst_edges['ab']
sp = ig.Graph((vertex_per_circle*circles) + 1, edges=mst_edges)
shortest_path = sp.get_shortest_paths(0,(vertex_per_circle*(circles-1)) + 1, output="vpath")

sp_edge_df = sp.get_edge_dataframe()
sp_edge_df['path'] = sp_edge_df.index.isin(shortest_path[0])
sp_edge_df = sp_edge_df.loc[sp_edge_df['path'],:]
sp_edge_df['ab'] = list(zip(sp_edge_df['source'], sp_edge_df['target']))
sp_verts = list(sp_edge_df['ab'])


# dim=10

# g = ig.Graph.Lattice([dim,dim], circular=False)

# # Random edge weights
# g.es["weight"] = [random.randint(1, 77) for _ in g.es]

# # Add Row-Col ID attributes
# for i in range(len(g.vs)):
#     g.vs[i]["id"] = i
#     #g.vs[i]["label"] = str(i)
#     g.vs[i]["rowid"] = i // dim
#     g.vs[i]["colid"] = i % dim

# #### minimum spanning tree of grid graph

# mst = g.spanning_tree(weights=g.es["weight"], return_tree=False)

# # Get vertice IDs of mst edges
# mst_edges = []

# for edge in g.es[mst]:
#     mst_edges.append([edge.source, edge.target])

# #### graph of mst edges 

# sp = ig.Graph(dim**2, edges=mst_edges)

# #### shortest path solution 

# shortest_path = sp.get_shortest_paths(0,dim**2-1, output="epath")

# #### grid graph neighbors DataFrame
# neighbors = []
# t=[]

# sources_id = []
# targets_id = []
# sources_rowid = []
# sources_colid = []

# targets_rowid = []
# targets_colid = []


# for i in range(len(g.vs)):
#     n=g.neighbors(i)
#     for j in n:
#         t=(i,j)
#         t=tuple(sorted(t))
#         neighbors.append(t)

#         sources_id.append(t[0])
#         targets_id.append(t[1])

#         sources_rowid.append(g.vs[t[0]]["rowid"])
#         sources_colid.append(g.vs[t[0]]["colid"])

#         targets_rowid.append(g.vs[t[1]]["rowid"])
#         targets_colid.append(g.vs[t[1]]["colid"])

# neighbors = pd.DataFrame({"neighbors" : neighbors, 
#                             "source_id" : sources_id,
#                             "target_id" : targets_id,
#                             "source_rowid" : sources_rowid, "source_colid" : sources_colid,
#                             "target_rowid" : targets_rowid, "target_colid" : targets_colid})

# neighbors = neighbors.drop_duplicates().reset_index(drop=True)

# neighbors["rowdiff"] = neighbors["source_rowid"] != neighbors["target_rowid"]
# neighbors["coldiff"] = neighbors["source_colid"] != neighbors["target_colid"]

# #### path (mst connected vertices) DataFrame
# source_target = []

# sources_rowid = []
# sources_colid = []

# targets_rowid = []
# targets_colid = []

# for i in range(len(g.es[mst])):

#     s=g.vs[g.es[mst][i].source]["id"]
#     t=g.vs[g.es[mst][i].target]["id"]

#     st=(s,t)    
#     source_target.append(tuple(sorted(st)))

#     sources_rowid.append(g.vs[g.es[mst][i].source]["rowid"])
#     sources_colid.append(g.vs[g.es[mst][i].source]["colid"])

#     targets_rowid.append(g.vs[g.es[mst][i].target]["rowid"])
#     targets_colid.append(g.vs[g.es[mst][i].target]["colid"])

# edges = pd.DataFrame({"source_target" : source_target,

#                         "sources_rowid" : sources_rowid, "sources_colid" : sources_colid,
#                         "targets_rowid" : targets_rowid, "targets_colid" : targets_colid})

# # List of vertex index tuples with an mst edge
# edge_vertices = list(edges["source_target"])

# #### walls DataFrame 
# # walls = neighbors - path
# walls = neighbors[~neighbors["neighbors"].isin(edge_vertices)].reset_index(drop=True)

# walls["wall_source_rowid"] = walls["source_rowid"]
# walls["wall_source_colid"] = walls["source_colid"]

# walls["wall_target_rowid"] = walls["target_rowid"]
# walls["wall_target_colid"] = walls["target_colid"]

# # Row difference 
# walls.loc[walls["rowdiff"]==True, "wall_source_rowid"] = walls["wall_source_rowid"] + 1
# walls.loc[walls["rowdiff"]==True, "wall_target_colid"] = walls["wall_target_colid"] + 1

# # Column Difference
# walls.loc[walls["coldiff"]==True, "wall_source_colid"] = walls["wall_source_colid"] + 1
# walls.loc[walls["coldiff"]==True, "wall_target_rowid"] = walls["wall_target_rowid"] + 1

# # Convert (Row, Column) ID to Vertex Index
# walls["wall_source_id"] = walls["wall_source_rowid"]*(dim+1) + walls["wall_source_colid"]
# walls["wall_target_id"] = walls["wall_target_rowid"]*(dim+1) + walls["wall_target_colid"]

# # walls vertix index tuple
# walls["walls"] = list(zip(walls["wall_source_id"], walls["wall_target_id"]))

# #### boundary DataFrame and vertex index list  
# sides_colid = np.repeat([0,dim],dim)

# sides_source_rowid = pd.Series(range(0,dim))
# sides_source_rowid = pd.concat([sides_source_rowid]*2)

# sides_target_rowid = pd.Series(range(1,dim+1))
# sides_target_rowid = pd.concat([sides_target_rowid]*2)

# floors_rowid =  np.repeat([0,dim],dim)

# floors_source_colid= pd.Series(range(0,dim))
# floors_source_colid = pd.concat([floors_source_colid]*2)

# floors_target_colid = pd.Series(range(1,dim+1))
# floors_target_colid = pd.concat([floors_target_colid]*2)

# sides = pd.DataFrame({"source_colid" : sides_colid,
#                         "target_colid" : sides_colid,
#                         "source_rowid" : sides_source_rowid,
#                         "target_rowid" : sides_target_rowid}
#                     )

# floors = pd.DataFrame({"source_colid" : floors_source_colid,
#                         "target_colid" : floors_target_colid,
#                         "source_rowid" : floors_rowid,
#                         "target_rowid" : floors_rowid}
#                     )

# boundaries = pd.concat([sides, floors], ignore_index=True, axis=0)

# # Convert boundary (Row, Column) ID to vertex index
# boundaries["source_id"] = boundaries["source_rowid"]*(dim+1) + boundaries["source_colid"]
# boundaries["target_id"] = boundaries["target_rowid"]*(dim+1) + boundaries["target_colid"]

# # boundary vertex index tuple
# boundaries["boundaries"] = list(zip(boundaries["source_id"], boundaries["target_id"]))

# # list of boundary vertex index tuples
# walls_boundaries = list(walls.walls) + list(boundaries.boundaries)