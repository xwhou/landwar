#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-25 下午8:14
# @Author  : sgr
# @Site    : 
# @File    : state_data.py


from common.m_exception import print_exception
from wgoperator.operator_sets import OperatorSets
from wgclock.clock import Clock
from wgmap.terrain import Terrain
from wgmap.cities import Cities
from wgweapon.weapon_sets import WeaponSets
from wgmap.jm_point_sets import JMPointSets
from wgconst.const import Color


class StateData:
    """
    态势管理类
    Attributes:
        terrain: 地图操作类
        weapons: 武器类
        clock: 时钟类
        cities: 夺控点类
        operator_sets： 算子管理类
        jm_point_sets: 间瞄点集合类
    """
    def __init__(self, loader, auto_get_on=True):
        self.loader = loader
        try:
            self.terrain = Terrain(loader=self.loader)
            self.weapons = WeaponSets(loader=self.loader, terrain=self.terrain)
            self.clock = Clock(loader=self.loader)
            self.cities = Cities(loader=self.loader)
            self.operator_sets = OperatorSets(loader=self.loader, terrain=self.terrain, weapon=self.weapons,
                                              clock=self.clock, auto_get_on=auto_get_on)
            self.jm_point_sets = JMPointSets(operator_sets=self.operator_sets,
                                             weapon_sets=self.weapons,
                                             terrain=self.terrain,
                                             clock=self.clock)

            self.scores = {
                "red_occupy": 0,    # 红方夺控分
                "red_remain": 0,    # 红方剩余算子分
                "red_attack": 0,    # 红方战斗得分
                "blue_occupy": 0,    # 蓝方夺控分
                "blue_remain": 0,    # 蓝方剩余得分
                "blue_attack": 0,    # 蓝方攻击得分
                "red_total": 0,    # 红方总分
                "blue_total": 0,    # 蓝方总分
                "red_win": 0,   # 红方净胜分
                "blue_win": 0,  # 蓝方净胜分
            }

            self.cal_scores()
        except Exception as e:
            print_exception(e)
            raise e

    def get_terrain(self):
        return self.terrain

    def get_weapon(self):
        return self.weapons

    def get_clock(self):
        return self.clock

    def get_cities(self):
        return self.cities

    def get_operator_sets(self):
        return self.operator_sets

    def get_jm_point_sets(self):
        return self.jm_point_sets

    def reset(self):
        try:
            self.clock.reset()
            self.cities.reset()
            self.operator_sets.reset()
            self.jm_point_sets.reset()
            self.cal_scores()
        except Exception as e:
            print_exception(e)
            raise e

    def auto_get_on(self):
        try:
            self.operator_sets.auto_get_on()
        except Exception as e:
            print_exception(e)
            raise e

    def load_component(self, operator_data=None, clock_data=None, cities_data=None):
        try:
            self.reset()
            if operator_data:
                self.operator_sets.load_component(operator_data)
            if clock_data:
                self.clock.load_component(clock_data)
            if cities_data:
                self.cities.load_component(cities_data)
        except Exception as e:
            print_exception(e)
            raise e

    def update(self, state_manager):
        """
        更新态势
        :param state_manager:
        :return:
        """
        try:
            self.jm_point_sets.update(state_manager)
            self.operator_sets.update()
            self.cal_scores()
            return self.clock.update()
        except Exception as e:
            print_exception(e)
            raise e

    def cal_scores(self):
        try:
            red_occupy = self.cities.get_cities_scores_by_color(color=Color.RED)
            blue_occupy = self.cities.get_cities_scores_by_color(color=Color.BLUE)
            red_remain, red_lost = self.operator_sets.get_remain_and_lost_scores_by_color(color=Color.RED)
            blue_remain, blue_lost = self.operator_sets.get_remain_and_lost_scores_by_color(color=Color.BLUE)
            red_total = red_occupy + red_remain + blue_lost
            blue_total = blue_occupy + blue_remain + red_lost
            self.scores["red_occupy"] = red_occupy
            self.scores["blue_occupy"] = blue_occupy
            self.scores["red_remain"] = red_remain
            self.scores["blue_remain"] = blue_remain
            self.scores["red_attack"] = blue_lost
            self.scores["blue_attack"] = red_lost
            self.scores["red_total"] = red_total
            self.scores["blue_total"] = blue_total
            self.scores["red_win"] = red_total - blue_total
            self.scores["blue_win"] = blue_total - red_total
        except Exception as e:
            print_exception(e)
            raise e

    def get_observations(self, color):
        """
        返回指定颜色可见态势
        :param color:
        :return:
        """
        try:
            obs = dict()
            obs['operators'] = self.operator_sets.get_bop_observations(color)
            obs['time'] = self.clock.get_time_observation()
            obs['jm_points'] = self.jm_point_sets.get_jm_observations(color)
            obs['cities'] = self.cities.get_citites_obsevation()
            obs["scores"] = self.scores
            return obs
        except Exception as e:
            print_exception(e)
            raise e

    def get_observarion_notes(self):
        """返回态势注释json文件"""
        try:
            obs = dict()
            obs['operators'] = self.operator_sets.get_bop_observation_notes()
            obs['time'] = self.clock.get_time_observation_notes()
            obs['jm_points'] = self.jm_point_sets.get_jm_observations_notes()
            obs['cities'] = self.cities.get_citites_obsevation_notes()
            obs["scores"] = {
                "red_occupy": "红方夺控分",
                "red_remain": "红方剩余算子分",
                "red_attack": "红方战斗得分",
                "blue_occupy": "蓝方夺控分",
                "blue_remain": "蓝方剩余得分",
                "blue_attack": "蓝方攻击得分",
                "red_total": "红方总分",
                "blue_total": "蓝方总分",
                "red_win": "红方净胜分",
                "blue_win": "蓝方净胜分",
            }
            return obs
        except Exception as e:
            print_exception(e)
            raise e


