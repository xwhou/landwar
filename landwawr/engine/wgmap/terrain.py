#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-8 下午2:18
# @Author  : sgr
# @Site    : 
# @File    : terrain.py

from common.m_exception import print_exception
from wgloader.loader import Loader
import numpy as np
from wgconst.const import OperatorType
import heapq
from wgconst.const import TerrainMoveType
# 0-开阔地 1-丛林 2-居民 3-松软地
dx_impact = [1, 2, 3, 4]
list_neighdir_offset_ji = [(0, 1), (-1, 1), (-1, 0), (0, -1), (1, 0), (1, 1)]
list_neighdir_offset_ou = [(0, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0)]
dic_xd2elequa = {83: 10, 19: 20, 86: 10, 43: 10, 84: 10, 82: 20}
map_size = {82: (63, 50), 83: (65, 50), 19: (69, 65), 43: (59, 57), 86: (63, 50), 84: (63, 50)}
dis_between_hex = 200   # 格间距 200m
river_impact = 4.0
dx_cost = [1, 2, 3, 4]                # 0-开阔地 1-丛林地 2-居民 3-松软地
rode_impact = [1.0, 1.5, 2.0, 3.0]    # 非道路/黑色道路/红色道路/黄色道路

class Terrain:
    """
    地图类
    """

    def __init__(self, loader):
        """
        MAP_X   # 地图长
        MAP_Y   # 地图高
        HEIGHT_LEVEL    # 高差等级
        df_map_data # 原始地图数据 (Coord, Cond, Road, Height, Water)
        cost_data   # 通行代价表 {'foot_cost', 'car_move_cost', 'car_march_cost', 'plane_cost'}
        dict_roadnet  #路网
        hex_dis_dict  #距离缓存
        see_rang      #通視範圍
        G             #车辆机动可行进边集
        G1            #车辆行军可行进边集
        G2            #人员和飞机边集
        """

        self.loader = loader
        self.terrain_id = self.loader.terrain_id
        self.MAP_X = map_size[self.terrain_id][0]
        self.MAP_Y = map_size[self.terrain_id][1]
        self.df_map_data = None
        self.dict_roadnet = None
        self.dic_water_net = None
        self.HEIGHT_LEVEL = dic_xd2elequa[self.loader.terrain_id]
        self.np_icu_dis = None
        self.np_nicu_a2a = None
        self.np_nicu_a2g = None
        self.see_range = None
        self.G = {}
        self.G1 = {}
        self.G2 = {}
        self.cost = [0]*10000
        self.load()
        self.load_G()

    def load(self):
        """
        Todo 加载数据
        :return:
        """
        try:
            self.df_map_data, self.see_range, self.dict_roadnet, self.np_icu_dis, self.dic_water_net, self.np_nicu_a2a, self.np_nicu_a2g = \
                self.loader.load_terrain()  # 地图数据
        except Exception as e:
            print_exception(e)
            raise e

    def load_G(self):
        try:
            for row in self.df_map_data.iterrows():
                mapid = row[0]
                self.G[mapid] = []   # G[mapid] = [(tomapid,elecost,road,water)]
                self.G1[mapid] = []  # 车辆行军G1[mapid] = [(tomapid, road)]
                self.G2[mapid] = []  # G2[mapid] = [(tomapid, ele)]   飞机/人员
                self.cost[mapid] = dx_cost[self.get_grid_sub_type(mapid)]  # 自身地形
                nei = self.get_neighbors(mapid)
                for x in nei:
                    if x != -1:
                        h = self.get_height_change_level(mapid, x)
                        self.G2[mapid].append((x, abs(h)))
                        has_road = self.get_road_type_between_hex(mapid, x)
                        if abs(h) <= 5:
                            if has_road != -1:
                                self.G1[mapid].append((x, has_road))
                            has_river = self.has_river_between_hex(mapid, x)
                            self.G[mapid].append((x, max(1, abs(h)), has_road, has_river))
        except Exception as e:
            raise e

    def get_neighbors(self, pos):
        """
        获取指定位置的邻域
        :param pos: 四位坐标
        :return: 相邻六格四位坐标，如果超出地图范围则填-1
        """
        try:
            row, col = pos // 100, pos % 100
            assert self.is_pos_valid(pos)
            list_neigh_loc = []
            ji_flag = row % 2 == 1
            list_neighdir_offset = list_neighdir_offset_ji if ji_flag else list_neighdir_offset_ou
            for dir_index in range(6):
                list_neigh_loc.append(tuple(np.add((row, col), list_neighdir_offset[dir_index])))
            nei = []
            for e in list_neigh_loc:
                if self.is_pos_valid(e[0]*100 + e[1]):
                    nei.append(e[0]*100 + e[1])
                else:
                    nei.append(-1)
            return nei
        except Exception as e:
            raise e

    def get_height(self, pos):
        """
        获取指定位置的高程
        :param pos:
        :return:
        """
        try:
            height = -1
            if pos in self.df_map_data['MapID']:
            #assert (len(self.df_map_data[self.df_map_data.MapID == pos]) == 1)
                height = int(self.df_map_data.loc[pos, 'GroundID'])

            return height
        except Exception as e:
            print_exception(e)
            raise e

    def get_path(self, pos1, pos2, mod):
        """
        获取通行代价最小的路径
        :param pos1:出发点坐标
        :param pos2:目标点坐标
        :param type:通行方式
        :return:
        """
        if mod == TerrainMoveType.CarMove:
            return self.dij_CarMove(pos1, pos2)
        elif mod == TerrainMoveType.CarMarch:
            return self.dij_CarMarch(pos1, pos2)
        elif mod == TerrainMoveType.PeoMove:
            return self.dij_PeoMove(pos1, pos2)
        elif mod == TerrainMoveType.PlaneMove:
            return self.dij_PlaneMove(pos1, pos2)

    def get_height_change_level(self, pos1, pos2):
        """
        获取两个位置的高差变化等级 (从pos1进入pos2的高差)
        :param pos1:
        :param pos2:
        :return:
        """
        ele_diff = (self.get_height(pos2) - self.get_height(pos1)) // self.HEIGHT_LEVEL
        return ele_diff

    def get_speed_ratio(self, move_type, pos1, pos2):  # 車輛機動/車輛行軍/人員機動 0 1 2
        """
        获取位置1到位置2的速度变化率
        :param pos1:
        :param pos2:
        :return:
        """
        speed = 1.0  # 正常機動速度
        if self.is_pos_valid(pos1 ) == False or self.is_pos_valid(pos2) == False or self.is_neighbor(pos1, pos2) == False:
            return 0
        ele_diff = self.get_height_change_level(pos1, pos2)
        if move_type != 2 and abs(ele_diff) > 5:
            return 0
        if move_type == 0:  # 車輛機動
            '''地形相關'''
            if self.get_road_type_between_hex(pos1, pos2) != -1:  # 车辆沿道路行驶不受地形影响且与坡度无关
                speed /= 1.0
            else:  # 車輛不沿道路行駛受地形影響
                '''坡度相關'''
                speed /= 1.0 * max(1, abs(ele_diff))
                if self.has_river_between_hex(pos1, pos2):
                    speed /= (1.0*river_impact)
                dx = self.get_grid_sub_type(pos2)
                speed /= 1.0 * dx_impact[dx]

        elif move_type == 1:  # 車輛行軍
            grid_type = self.get_road_type_between_hex(pos1, pos2)  # -1(无效) / 0（黑色公路） / 1（红色公路） / 2 （等级公路）(红)
            speed *= (1.0*rode_impact[grid_type + 1])  #rode_impact = [1.0, 1.5, 2.0, 3.0]

        elif move_type == 2:
            '''地形不相關'''
            '''坡度相關'''
            if abs(ele_diff) > 3:
                speed = 0.5
        return speed

    def check_see(self, pos1, pos2, mod=0):
        """
        判断两个位置是否通视
        :param mod: 0 1 2 3地对地，空对空，空对地，地对空
        :param pos1:
        :param pos2:
        :return:
        """
        try:
            flag_hex_icu = True
            if pos1 == pos2:
                return flag_hex_icu
            key_af = pos1 * 10000 + pos2
            key_bf = pos2 * 10000 + pos1
            if mod == 0:
                flag_hex_icu = False
                if (key_af in self.np_icu_dis) or (key_bf in self.np_icu_dis):
                    flag_hex_icu = True
            else:
                if (mod == 1 and key_af in self.np_nicu_a2a) or (mod == 2 and key_af in self.np_nicu_a2g) or (mod == 3 and key_bf in self.np_nicu_a2g):
                    flag_hex_icu = False
            return flag_hex_icu
        except Exception as e:
            print_exception(e)
            raise e

    def is_neighbor(self, pos1, pos2):
        return self.get_dis_between_hex(pos1=pos1, pos2=pos2) == 1

    def is_neighbor_cache(self, pos1, pos2):
        for e in self.G2[pos1]:
            if e[0] == pos2:
                return True
        return False

    def is_in_cover(self, pos):
        """
        是否遮蔽地形
        :param pos:
        :return:
        """
        if self.get_grid_type(pos) == 3:
            return True
        return False

    def is_pos_valid(self, pos):
        """
        坐标是否在地图有效范围内
        :param pos:
        :return:
        """
        if 0 <= pos//100 <= self.MAP_X and 0 <= pos % 100 <= self.MAP_Y:
            return True
        return False
        #if (map_min_row <= pos // 100 <= map_max_row) and (map_min_col <= pos % 100 <= map_max_col):
        #    return True
        #return False

    def get_see_range(self, pos):
        """
        获取指定位置的通视范围
        :param pos:
        :return:
        """
        return self.see_range[pos]

    def has_road(self, pos):
        """返回当前坐标是否包含道路"""
        try:
            assert (len(self.df_map_data[self.df_map_data.MapID == pos]) == 1)
            return self.df_map_data.loc[pos, 'GridType'] == 2
        except Exception as e:
            print_exception(e)
            raise e

    def has_road_between_hex(self, pos1, pos2):
        return self.get_road_type_between_hex(pos1, pos2) > -1

    def get_road_type_between_hex(self, pos1, pos2):
        """
        :param pos1 pos2
        :return:  -1(无效) / 0（黑色公路） / 1（红色公路） / 2 （等级公路）(黄)
        """
        try:
            if not self.is_pos_valid(pos1) or not self.is_pos_valid(pos2):
                return -1
            if self.get_dis_between_hex(pos1, pos2) != 1:
                return -1
            type_a = -1
            if pos1 in self.dict_roadnet.keys():
                edge_num = int(self.dict_roadnet[pos1][0])
                for e_i in range(edge_num):
                    tmp_pos = int(self.dict_roadnet[pos1][1 + e_i * 2])
                    if tmp_pos == pos2:
                        type_a = int(self.dict_roadnet[pos1][1 + e_i * 2 + 1])
                        break
            return type_a
        except Exception as e:
            print_exception(e)
            raise e

    def get_dis_between_hex(self, pos1, pos2):
        """
        :param pos1:
        :param pos2:
        :return:
        """
        try:
            '''转换为二元坐标'''
            row1 = pos1//100
            col1 = pos1%100
            row2 = pos2 // 100
            col2 = pos2 % 100
            '''转换为立方坐标'''
            q1 = col1 - (row1 - (row1 & 1)) // 2
            r1 = row1
            s1 = 0 - q1 - r1
            q2 = col2 - (row2 - (row2 & 1)) // 2
            r2 = row2
            s2 = 0 - q2 - r2
            '''输出距离为曼哈顿距离的1/2'''
            return (abs(q1-q2) + abs(r1-r2) + abs(s1-s2))//2

        except Exception as e:
            print_exception(e)
            raise e

    def get_grid_type(self, pos):
        '''

        :param pos:
        :return: grid_type: 0-开阔地 1-河流 2-道路 3-遮蔽地
        '''
        try:
            pos_info = self.df_map_data[self.df_map_data.MapID == pos]
            grid_type = pos_info.loc[pos, 'GridType']
            return grid_type
        except Exception as e:
            print_exception(e)
            raise e

    def get_grid_sub_type(self, pos):
        '''

        :param pos:
        :return: 0-开阔地 1-丛林地 2-居民地 3-松软地
        '''
        pos_info = self.df_map_data[self.df_map_data.MapID == pos]
        grid_type = pos_info.loc[pos, 'GridType']
        dx = 0
        grid_id = pos_info.loc[pos, 'GridID']
        cond = pos_info.loc[pos, 'Cond']
        if (grid_type == 2 and grid_id == 51) or cond == 7:
            dx = 2
        elif grid_type == 3:
            dx = 1 if grid_id == 52 else 2
        if cond == 6:
            dx = 3
        return dx

    def get_spec_len_dir_pos(self, pos, len, dir):
        """
        Todo 计算指定方向和距离上的邻域坐标
        :param pos
        :param len:
        :param dir: 0-5 六个方向
        :return:
        """
        try:
            assert self.is_pos_valid(pos)
            assert (dir >= 0 and dir < 6)
            row, col = pos // 100, pos % 100
            tt = (row, col)
            while len > 0:
                ji_flag = tt[0] % 2 == 1
                list_neighdir_offset = list_neighdir_offset_ji if ji_flag else list_neighdir_offset_ou
                nt = tuple(np.add((tt[0], tt[1]), list_neighdir_offset[dir]))
                #print(nt[0]*100+nt[1])
                if self.is_pos_valid(nt[0]*100 + nt[1]):
                    tt = nt
                else:
                    break
                len -= 1
            return tt[0]*100 + tt[1]
        except Exception as e:
            print_exception(e)
            raise e

    def change_speed_to_hex_sec(self, speed):
        """
        速度转化为 格/s
        :param speed: km/h
        :return: 格/s
        """
        try:
            speed_ms = speed / 3.6  # 速度 m/s
            return speed_ms / dis_between_hex
        except Exception as e:
            print_exception(e)
            raise e

    def has_river_between_hex(self, pos1, pos2):
        try:
            if not self.is_pos_valid(pos1) or not self.is_pos_valid(pos2):
                return False
            if self.get_dis_between_hex(pos1, pos2) != 1:
                return -1
            poslist = [pos1, pos2]
            for pos in poslist:
                if pos in self.dic_water_net.keys():
                    edge_num = int(self.dic_water_net[pos][0])
                    for i in range(edge_num):
                        tmp_pos = int(self.dic_water_net[pos][1+i])
                        if tmp_pos == pos2 or tmp_pos == pos1:
                            return True
            return False
        except Exception as e:
            print_exception(e)
            raise e

    def dij_CarMove(self, begin, end):
        tasks = []
        fa = [-1]*10000
        d = [0x3f3f3f3f]*10000
        d[begin] = 0
        heapq.heappush(tasks, (d[begin], begin))
        while tasks:
            task = heapq.heappop(tasks)
            v = task[1]
            if d[v] < task[0] or self.G.get(v, -1) == -1 or self.G[v] == []:
                continue
            for e in self.G[v]:
                if e[2] != -1:
                    '''车辆在道路上机动不用考虑地形和高差'''
                    if d[e[0]] > d[v] + 1:
                        d[e[0]] = d[v] + 1
                        heapq.heappush(tasks, (d[e[0]], e[0]))
                        fa[e[0]] = v
                else:
                    '''非道路上： 基础时间 = 高差×河流×地形'''
                    if e[3]:
                        if d[e[0]] > d[v] + e[1] * 4 * self.cost[e[0]]:
                            d[e[0]] = d[v] + e[1] * 4 * self.cost[e[0]]
                            heapq.heappush(tasks, (d[e[0]], e[0]))
                            fa[e[0]] = v
                    else:
                        if d[e[0]] > d[v] + e[1] * self.cost[e[0]]:
                            d[e[0]] = d[v] + e[1] * self.cost[e[0]]
                            heapq.heappush(tasks, (d[e[0]], e[0]))
                            fa[e[0]] = v
        t = end
        path = []
        if d[end] < 0x3f3f3f3f:
            while t != -1 and t != begin:
                path.append(t)
                t = fa[t]
        path.reverse()
        return path

    def dij_CarMarch(self, begin, end):
        tasks = []
        fa = [-1] * 10000
        d = [0x3f3f3f3f] * 10000
        d[begin] = 0
        heapq.heappush(tasks, (d[begin], begin))
        while tasks:
            task = heapq.heappop(tasks)
            v = task[1]
            if d[v] < task[0] or self.G1.get(v, -1) == -1 or self.G1[v] == []:
                continue
            for e in self.G1[v]:
                if d[e[0]] > d[v] + 1.0/rode_impact[e[1]+1]:
                    d[e[0]] = d[v] + 1.0 / rode_impact[e[1]+1]      # 非道路/黑色道路/红色道路/黄色道路
                    heapq.heappush(tasks, (d[e[0]], e[0]))
                    fa[e[0]] = v
        t = end
        path = []
        if d[end] < 0X3f3f3f3f:
            while t != -1 and t != begin:
                path.append(t)
                t = fa[t]
            path.reverse()
        return path

    def dij_PeoMove(self, begin, end):
        tasks = []
        fa = [-1] * 10000
        d = [0x3f3f3f3f] * 10000
        d[begin] = 0
        heapq.heappush(tasks, (d[begin], begin))
        while tasks:
            task = heapq.heappop(tasks)
            v = task[1]
            if d[v] < task[0] or self.G2.get(v, -1) == -1 or self.G2[v] == []:
                continue
            for e in self.G2[v]:
                if d[e[0]] > d[v] + (2 if e[1] > 3 else 1):
                    d[e[0]] = d[v] + (2 if e[1] > 3 else 1)
                    heapq.heappush(tasks, (d[e[0]], e[0]))
                    fa[e[0]] = v
        t = end
        path = []
        if d[end] < 0X3f3f3f3f:
            while t != -1 and t != begin:
                path.append(t)
                t = fa[t]
            path.reverse()
        return path

    def dij_PlaneMove(self, begin, end):
        tasks = []
        fa = [-1] * 10000
        d = [0x3f3f3f3f] * 10000
        d[begin] = 0
        heapq.heappush(tasks, (d[begin], begin))
        while tasks:
            task = heapq.heappop(tasks)
            v = task[1]
            if d[v] < task[0] or self.G2.get(v, -1) == -1 or self.G2[v] == []:
                continue
            for e in self.G2[v]:
                if d[e[0]] > d[v] + 1:
                    d[e[0]] = d[v] + 1
                    heapq.heappush(tasks, (d[e[0]], e[0]))
                    fa[e[0]] = v
        t = end
        path = []
        if d[end] < 0X3f3f3f3f:
            while t != -1 and t != begin:
                path.append(t)
                t = fa[t]
            path.reverse()
        return path

    """"
    def get_see_range_dic(self):
        self.dic_see_range = {}
        self.poslist = self.df_map_data.MapID
        #poslist = [1624, 1623]
        for pos in self.poslist:
            print('continue..')
            print(pos)
            list=[]
            for pos1 in self.poslist:
                if self.check_see(pos, pos1):
                    list.append(pos1)
            self.dic_see_range.update({pos: list})

        with open(str_map_dir + 'map_' + str(self.loader.terrain_id) + '/icanc_range.pickle', 'wb') as f1:
            pickle.dump(self.dic_see_range, f1)
            f1.close()
    """
    """
    def gen_waternet(self):
        self.dic_water_net = {}
        df_labelled = pandas.read_excel('../../Data/labelled_hexs.xls', 'Sheet1')
        df_labelled.index = df_labelled.GridID
        for row in self.df_map_data.iterrows():
            pos = row[0]
            r = pos // 100
            c = pos % 100
            if r < 0 or r > self.MAP_X or c < 0 or c > self.MAP_Y:
                continue
            pos_info = self.df_map_data[self.df_map_data.MapID == pos]
            grid_type = pos_info.loc[pos, 'GridType']
            if grid_type == 1:  # 是水域
                nei = self.get_neighbors(pos)
                grid_id = pos_info.loc[pos, 'GridID']
                gird_info = df_labelled[df_labelled.GridID == grid_id]
                dir = gird_info.loc[grid_id, 'WaterDK']
                dir = eval('[' + str(dir) + ']')
                list1 = []
                list1.append(len(dir))
                if dir[0] == 6:
                    list1[0] = 6
                    for i in range(6):
                        list1.append(nei[i])
                else:
                    for i in dir:
                        list1.append(nei[i])
                self.dic_water_net.update({pos: list1})
        with open('../../Data/map/map_' + str(self.loader.terrain_id) + '/waternet.pickle', 'wb') as f1:
            pickle.dump(self.dic_water_net, f1)
            f1.close()
    """

def cvt_int4_to_offset(int4_loc):
    return int4_loc // 100, int4_loc % 100


def cvt_offset_to_int4(row, col):
    return row * 100 + col


def cvt_int6_to_int4(int6_loc):
    try:
        assert isinstance(int6_loc, int)
        y, x = cvt_int6_to_offset(int6_loc)
        return y * 100 + x
    except Exception as e:
        print_exception(e)
        raise e


def cvt_int6_to_offset(int6_loc):
    '''转换6位整形坐标int6loc转换为偏移坐标（y,x）2元组'''
    try:
        str6loc = str(int6_loc)
        len_oristr6loc = len(str6loc)
        assert (len_oristr6loc <= 6)
        if len_oristr6loc < 6:
            str6loc = '0' * (6 - len_oristr6loc) + str6loc

        int_first_2, int_last_3 = int(str6loc[0:2]), int(str6loc[3:])
        if int_last_3 % 2 == 1:
            row, col = int_first_2 * 2 + 1 , (int_last_3 - 1) // 2
        else:
            row, col = int_first_2 * 2, int_last_3 // 2
        return row, col
    except Exception as e:
        print_exception(e)
        raise


def cvt_int4_to_int6(int4_loc):
    try:
        assert isinstance(int4_loc, int)
        row, col = cvt_int4_to_offset(int4_loc)
        return cvt_offset_to_int6(row, col)
    except Exception as e:
        print_exception(e)
        raise e


def cvt_offset_to_int6(row, col):
    try:
        if row % 2 == 1:
            tmpfirst = (row - 1) // 2
            tmplast = col * 2 + 1
        else:
            tmpfirst = row // 2
            tmplast = col * 2
        if tmpfirst < 0 or tmplast < 0:
            return -1
        return int(tmpfirst * 10000 + tmplast)
    except Exception as e:
        print_exception(e)
        raise


def check_bop_see(bop_a, bop_b, t_terrain):
    """
    检查算子a能否观察到b
    :param bop_a : 主动观察者
    :param bop_b : 目标
    :param t_terrain
    :returns : True 可观察 / False 不可观察
    :key : 首先基于地形进行HexIcuIsOK通视判断;
           然后考虑两个影响因素, 地形遮蔽和算子掩蔽状态, 两个因素对当前观察距离都有减半的影响
    """
    try:
        if not bop_a or not bop_b:
            return False
        flag_iou = False

        pos_a = bop_a.get_hex_pos()
        pos_b = bop_b.get_hex_pos()
        hex_distance = t_terrain.get_dis_between_hex(pos_a, pos_b)
        max_distance = bop_a.get_max_observe_distance(bop_b.get_bop_type())
        if max_distance != 0:
            max_distance += bop_b.B1
        # 如果算子之间的距离已经超过了最大距离则直接判断为不可观察
        if hex_distance > max_distance or max_distance == 0:
            flag_iou = False
        else:
            fly_a = 1 if bop_a.get_bop_type() == OperatorType.Plane else 0
            fly_b = 1 if bop_b.get_bop_type() == OperatorType.Plane else 0
            mod = 1 if fly_a == 1 and fly_b == 1 else 2 if fly_a == 1 and fly_b == 0 else 3 if fly_a == 0 and fly_b == 1 else 0
            if t_terrain.check_see(pos_a, pos_b, mod):
                # 地形通视判断通过没有遮挡,开始依据目标状态判断是否可观察
                distance_threshold = max_distance
                # 目标处于遮蔽地形,观察能力减半, 暂定空中单位不受地形影响
                if bop_b.get_bop_type() in [OperatorType.People, OperatorType.Car]:
                    flag_in_hide = bop_b.is_hiding()
                    if t_terrain.is_in_cover(pos_b):
                        distance_threshold = distance_threshold // 2
                    # 观察者观察目标（车辆）, 高差大于一个单位高程/或观察者为空中单位, 掩蔽无效
                    if flag_in_hide and bop_b.get_bop_type() == OperatorType.Car:
                        if bop_a.get_bop_type() == OperatorType.Plane:
                            flag_in_hide = False
                        else:
                            if t_terrain.get_height_change_level(pos_a, pos_b) <= -1:
                                flag_in_hide = False
                    distance_threshold = distance_threshold // 2 if flag_in_hide else distance_threshold
                # 比较计算完成后的观察距离和实际距离
                flag_iou = (hex_distance <= distance_threshold)
        return flag_iou
    except Exception as e:
        print_exception(e)
        raise e


if __name__ == '__main__':
    #load = Loader(1631)
    #terrain = Terrain(load)
    #print(terrain.get_path(2020, 2024, 1))
    print(cvt_int6_to_int4(60031))
    pass
