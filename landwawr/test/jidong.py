#车辆正常机动
import sys
sys.path.append("../../cz/path32")
sys.path.append("../engine")
import heapq
from wgloader.loader import Loader
from wgmap.terrain import Terrain
from time_test import fn_timer

V = 10000
G = {}            #{id:[(to, cost),(to, cost)]}
cost = [0]*V

@fn_timer
def dij(begin, end):
    d = [0x3f3f3f3f]*V
    tasks = []
    fa = [-1]*V
    d[begin] = 0            #不考虑初始点地形
    heapq.heappush(tasks, (d[begin], begin))     #最短路长度 - 顶点
    while tasks:
        task = heapq.heappop(tasks)
        v = task[1]
        if d[v] < task[0]:
            continue
        if G.get(v, -1) == -1 or G[v] == []:
            continue
        for e in G[v]:    #G中存边
            if e[2] != -1:
                if d[e[0]] > d[v] + e[1]:
                    d[e[0]] = d[v] + e[1]
                    heapq.heappush(tasks, (d[e[0]], e[0]))
                    fa[e[0]] = v
            else:                                                  #没有道路 时间= 地形×高差
                if e[3]:         #是河流
                    if d[e[0]] > d[v] + e[1]*4*cost[e[0]]:
                        d[e[0]] = d[v] + e[1]*4*cost[e[0]]
                        heapq.heappush(tasks, (d[e[0]], e[0]))
                        fa[e[0]] = v
                else:
                    if d[e[0]] > d[v] + e[1]*cost[e[0]]:
                        d[e[0]] = d[v] + e[1]*cost[e[0]]
                        heapq.heappush(tasks, (d[e[0]], e[0]))
                        fa[e[0]] = v

    t = end
    path = []
    while t != -1:
        path.append(t)
        t = fa[t]
    path.reverse()

    return d[end], path


'''加载地图初始化数据'''
load = Loader(scenario=17, data_dir="../")
terrain = Terrain(load)
# 0-开阔地 1-丛林 2-居民 3-松软地
dx_cost = [1, 2, 3, 4]
for row in terrain.df_map_data.iterrows():
    mapid = row[0]
    G[mapid] = []                                                   #G[mapid] = {(tomapid,elecost,road,water)}
    if mapid < 101:
        continue
    cost[mapid] = dx_cost[terrain.get_grid_sub_type(mapid)]         #自身地形
    nei = terrain.get_neighbors(mapid)
    for x in nei:
        if x != -1:
            h = terrain.get_height_change_level(mapid, x)
            has_road = terrain.get_road_type_between_hex(mapid, x)   #-1 则不是道路 else是道路
            has_river = terrain.has_river_between_hex(mapid, x)      #true/false
            G[mapid].append((x, max(1, abs(h)), has_road, has_river))



'''计算'''
ll = [(2020, 2024), (4325, 4322), (3633, 3616), (2724, 3227), (3827, 3230), (4220, 4320), (1010, 4949), (1407, 1815)]
for l in ll:
    time, path = dij(l[0], l[1])
    print(time)
    print(path)
