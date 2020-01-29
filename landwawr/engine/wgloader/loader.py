#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-12 下午1:47
# @Author  : sgr
# @Site    : 
# @File    : loader.py

import pandas as pd
import os
import pickle
from common.m_exception import print_exception


class SOURCE:
    FILE = 0
    DB = 1
    DATA = 2


class Loader:
    """
    资源数据加载类
    负责加载算子，地图，武器，夺控点，时钟等资源数据；
    也可以用来加载参数性常规配置;
    可以指定加载数据源： 从文件，从数据库，或从现有数据中;
    """
    def __init__(self, scenario, data_dir="../../"):
        try:
            self.scenario = scenario
            df_scen = pd.read_excel(os.path.join(data_dir, "Data/scenario.xlsx"), 'scenario')
            df_scen.index = df_scen.scenarioID
            df_scen = df_scen[df_scen.scenarioID == scenario]
            assert len(df_scen) == 1
            self.terrain_id, self.operators_id, self.cities_id, self.weapons_id = df_scen.loc[scenario, 'mapID'], df_scen.loc[scenario, 'operatorsID'], \
                                                               df_scen.loc[scenario, 'citiesID'], df_scen.loc[scenario, 'weaponsID']

            self.str_dir_map = os.path.join(data_dir, 'Data/map/')
            self.str_dir_cities = os.path.join(data_dir, 'Data/cities/')
            self.str_dir_weapons = os.path.join(data_dir, 'Data/weapons/')

        except Exception as e:
            print_exception(e)
            raise e

    def get_scenario(self):
        return self.scenario

    def load_operator(self):
        pass

    def load_terrain(self):
        try:
            df_terrain = pd.read_excel(self.str_dir_map + 'map_'+str(self.terrain_id)+'/reduced_map.xls', 'df')
            df_terrain.index = df_terrain.MapID
            with open(self.str_dir_map + 'map_' + str(self.terrain_id) + '/icanc_range.pickle', 'rb') as f1:
                see_range = pickle.load(f1)
            with open(self.str_dir_map + 'map_' + str(self.terrain_id) + '/adjmat_roadnet.pickle', 'rb') as f1:
                dict_roadnet = pickle.load(f1)
            with open(self.str_dir_map + 'map_' + str(self.terrain_id) + '/waternet.pickle', 'rb') as f1:
                dict_water_net = pickle.load(f1)
            with open(self.str_dir_map + 'map_' + str(self.terrain_id) + '/icu.pickle', 'rb') as f1:
                np_icu_dis = pickle.load(f1)
            with open(self.str_dir_map + 'map_' + str(self.terrain_id) + '/nicu_a2a.pickle', 'rb') as f1:
                np_nicu_a2a = pickle.load(f1)
            with open(self.str_dir_map + 'map_' + str(self.terrain_id) + '/nicu_a2g.pickle', 'rb') as f1:
                np_nicu_a2g = pickle.load(f1)
            return df_terrain, see_range, dict_roadnet, np_icu_dis, dict_water_net, np_nicu_a2a, np_nicu_a2g
        except Exception as e:
            print_exception(e)
            raise e

    def load_weapon(self):
        pass

    def load_cities(self):
        try:
            df_cities = pd.read_excel(self.str_dir_cities + '/cities_'+str(self.cities_id)+'.xlsx', 'cities')
            return df_cities
        except Exception as e:
            print_exception(e)
            raise e

    def load_clock(self):
        pass


if __name__ == '__main__':
    load = Loader(19)
    operator = load.load_operator()
    terrain = load.load_terrain()
    city = load.load_cities()
   # jm_weapon = load.load_jm_weapon()
    pass