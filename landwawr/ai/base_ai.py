#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-12-2 下午3:19
# @Author  : sgr
# @Site    : 
# @File    : base_ai.py


from common.m_exception import print_exception
from wgconst.const import StateType

class BaseAI:
    def __init__(self, color, obj_interface, interface_wgruler):
        """
        "time": {"cur_step": "当前步长 int", "tick": "s/步 float"},
        self.operators: [BasicOperator]
        self.jm_points: [{"obj_id": "攻击算子ID int",
                        "weapon_id": "攻击武器ID int",
                        "pos": "位置 int",
                        "status": "当前状态 0-正在飞行 1-正在爆炸 2-无效",
                        "fly_time": "剩余飞行时间 float",
                        "boom_time": "剩余爆炸时间 float"}]
        self.cities: [{"coord": "坐标 int", "value": "分值 int", "flag": "阵营 0-红 1-蓝", "name": "名称 str"}
        """
        self.color = color
        self.obj_interface = obj_interface
        self.interface_wgruler = interface_wgruler
        self.operators = []     # [BasicOperator]
        self.cities = []    # [{'Coord': int, "value": int, ""}]
        self.time = {}
        self.jm_points = []
        self.valid_actions = {}

    def reset(self):
        pass

    def step(self, state_data):
        """
        obs['operators'] = self.operator_sets.get_bop_observations(color)
            obs['time'] = self.clock.get_time_observation()
            obs['jm_points'] = self.jm_point_sets.get_jm_observations(color)
            obs['cities'] = self.cities.get_citites_obsevation()
        :param state_data:
                    {
                        "operators": [],
                        "time": {},
                        "jm_points": [],
                        "cities": {}
                    }
        :return:
        """
        try:
            # 更新自身态势
            self._update_state_data(dic_state=state_data)
            # 做动作, AI子类中完成
            return None

        except Exception as e:
            print_exception(e)
            raise e

    def update_state_data(self):
        """
        obs['operators'] = self.operator_sets.get_bop_observations(color)
            obs['time'] = self.clock.get_time_observation()
            obs['jm_points'] = self.jm_point_sets.get_jm_observations(color)
            obs['cities'] = self.cities.get_citites_obsevation()
        :param state_data:
                    {
                        "operators": [],
                        "time": {},
                        "jm_points": [],
                        "cities": {}
                    }
        :return:
        """
        try:
            # 更新自身态势
            state_data = self.obj_interface.get_observations()
            # state_data = state_data[self.color]
            self._update_state_data(dic_state=state_data)
            # 做动作, AI子类中完成
            return None

        except Exception as e:
            print_exception(e)
            raise e

    def _update_state_data(self, dic_state):
        '''
        更新游戏态势
        :param dic_state:获取到的态势
        '''
        try:
            self._update_operators() #更新算子状态
            self._update_cities()
            self._update_score()
            self.jm_points = dic_state['jm_points']
            self.clock = dic_state['time']
            self.judge_info = dic_state['judge_info']
            self.game_over = self.obj_interface.get_game_over()
        except Exception as e:
            print_exception(e)
            raise e

    def _update_operators(self):
        '''
        更新算子态势
        '''
        try:
            self.operators = self.obj_interface.getSideOperatorsData()
            self.enemy_operators = self.obj_interface.getEnemyOperatorsData()
            self.car_operators = self.obj_interface.getCarOperatorsData()
        except Exception as e:
            print_exception(e)
            raise e

    def _update_cities(self):
        '''
        更新夺控点态势
        '''
        try:
            self.cities = self.obj_interface.getCityData()
        except Exception as e:
            print_exception(e)
            raise e

    def _update_score(self):
        '''
        更新比赛分数信息
        '''
        try:
            self.score = self.obj_interface.getScore()
        except Exception as e:
            print_exception(e)
            raise e

    def create_action_msg(self, obj_id, action_type, paras):
        """
        生成动作信息
        :param obj_id:执行动作的算子id
        :param action_type:动作类型编号
        :param paras:  动作执行所需要的其他字段
        :return:动作信息列表
        """
        try:
            result = {
                "obj_id": obj_id,
                "type": action_type,
            }
            if action_type == StateType.Move:
                if 'move_path' not in paras.keys():
                    return False
            elif action_type == StateType.Shoot:
                if 'target_obj_id' not in paras.keys() or 'weapon_id' not in paras.keys():
                    return False
            elif action_type == StateType.GuideShoot:
                if 'target_obj_id' not in paras.keys() or 'weapon_id' not in paras.keys() or 'guided_obj_id' not in paras.keys():
                    return False
            elif action_type == StateType.JMPlan:
                if 'weapon_id' not in paras.keys() or 'jm_pos' not in paras.keys():
                    return False
            elif action_type == StateType.GetOn:
                if 'target_obj_id' not in paras.keys():
                    return False
            elif action_type == StateType.GetOff:
                if 'target_obj_id' not in paras.keys():
                    return False
            elif action_type == StateType.ChangeState:
                if 'target_state' not in paras.keys():
                    return False
            elif action_type == StateType.Occupy:
                pass
            elif action_type == StateType.RestoreKeep:
                pass
            if paras is None:
                paras = {}
            result.update(paras)
            return result
        except Exception as e:
            print_exception(e)
            raise e

    def get_bop_by_id(self, obj_id):
        '''
        通过算子id索引算子
        :param obj_id: 算子id
        :return: id匹配的算子
        '''
        try:
            for bop in self.operators:
                if bop.obj_id == obj_id:
                    return bop
            return None
        except Exception as e:
            print_exception(e)
            raise e




