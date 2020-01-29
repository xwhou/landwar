#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-10-31 上午10:36
# @Author  : sgr
# @Site    : 
# @File    : operator.py

import pandas
from common.m_exception import print_exception
from wgmessage.action_result import ActionResult
from wgconst.const import MoveState
from wgconst.const import OperatorType
from wgconst.const import OperatorSubType
from wgconst.const import TerrainMoveType
from wgmap.terrain import cvt_int6_to_int4
from common.data_transfer import str2int_list
from wgconst.const import Color
from wgconst.const import BasicSpeed
from wgconst.const import MaxPassengerNums


class BasicOperator:
    """
    算子类
    属性由基础属性+状态属性(State类中定义)组成
    """

    dic_map = {
        'ID': {'name': 'obj_id', 'fun': int},
        'GameColor': {'name': 'color', 'fun': int},
        'ObjName': {'name': 'name', 'fun': str},
        'ObjType': {'name': 'type', 'fun': int},
        'B0': {'name': 'armor', 'fun': int},
        'S1': {'name': 'S1', 'fun': int},    # 单独判断
        'S2': {'name': 'S2', 'fun': int},    # 单独判断
        'S3': {'name': 'S3', 'fun': int},    # 单独判断
        'ObjPos': {'name': 'cur_hex', 'fun': int},   # 单独判断
        'A1': {'name': 'A1', 'fun': int},
        'B1': {'name': 'B1', 'fun': int},
        'ObjTypeX': {'name': 'sub_type', 'fun': int},    # 单独判断
        'ObjKeep': {'name': 'keep', 'fun': int},
        'ObjTire': {'name': 'tire', 'fun': int},
        'ObjBlood': {'name': 'blood', 'fun': int},
        "ObjBlood2": {"name": "max_blood", "fun": int},
        'C2': {'name': 'C2', 'fun': int},
        'C3': {'name': 'C3', 'fun': int},
        'Wz': {'name': 'carry_weapon_ids', 'fun': str2int_list},
        'ObjOnboard': {'name': 'on_board', 'fun': int},
        'ObjSup': {'name': 'car', 'fun': int},
        'ObjSonID': {'name': 'passenger_ids', 'fun': str2int_list},  # 需要转化
        'ObjValue': {'name': 'value', 'fun': int},
        'ObjSonTypes': {'name': 'valid_passenger_types', 'fun': str2int_list},   # 需要转化 单独判断
        'ObjSpace': {'name': 'space', 'fun': int},
        'ObjGuideAbility': {'name': 'guide_ability', 'fun': int},  # 单独判断
        'basic_speed': {'name': 'basic_speed', 'fun': int},   # 单独判断
    }

    def __init__(self, terrain, data_source):
        """
        ID  # 算子唯一标识（建议取值范围 0-最大算子数）
        color   # 所属方
        name    # 名称
        type    # 类型 0-车辆 1-步兵 2-空中
        sub_type    # 细分类型 0-坦克 1-战车 2-步兵 3-炮兵 4-无人战车 5-无人机 6-武装直升机 7-巡飞弹
        max_blood   # 最大车/班数
        value   # 分值/每班
        armor  # 装甲类型 0-无装甲， 1-轻型装甲，2-中型装甲，3-重型装甲，4-复合装甲
        D1  # 被观察距离
        space   # 搭载上限
        valid_passenger_types   # 可以搭载算子类型
        A1  # 行进间射击能力

        state_sets  # 状态集合  {type: state(class)}
        active_states   # 需要持续更新的状态集合 [type(int)]
        todo_action_msg_sets    # 需要处理的消息列表

        terrain # terrain类的引用
        operator_sets   # OperatorSets类的引用
        action_msg_sets # ActionMsgSets类的引用

        """
        self.obj_id = -1    # 算子ID
        self.color = 0  # 算子阵营
        self.type = -1  # 算子类型
        self.name = None    # 算子名称
        self.sub_type = -1   # 细分类型
        self.basic_speed = 0    # 基础速度
        self.armor = 0  # 装甲类型
        self.A1 = 0  # 行进间射击能力
        self.stack = 0  # 是否堆叠
        self.carry_weapon_ids = []  # 携带武器列表
        self.C3 = 0     # 剩余导弹数
        self.C2 = 0     # 剩余子弹数
        self.guide_ability = 0  # 算子引导射击能力
        self.value = 0  # 算子分值
        self.valid_passenger_types = []  # 可承载类型
        self.max_passenger_nums = {}    # 最大承载数 {passenger_type: int}
        self.space = 0   # 最大搭乘数量
        self.B1 = 0  # 目标大小 24-直升机 0-非直升机
        # Todo
        self.observe_distance = {
            OperatorType.People: 0,
            OperatorType.Car: 0,
            OperatorType.Plane: 0
        }

        self.move_state = MoveState.NormalMove     # 机动状态
        self.cur_hex = -1   # 六角格坐标(四位)
        self.cur_pos = 0.0  # 当前格到下一格的百分比进度
        self.speed = 0  # 机动速度 km/h 机动速度为0表示算子没有机动(有可能正在转换为停止状态)
        self.move_to_stop_remain_time = 0   # 停止机动剩余时间
        self.stop = 1   # 是否静止 0-否, 1-是
        self.move_path = []  # 机动路径

        self.blood = 0  # 算子血量
        self.max_blood = 0  # 最大血量
        self.tire = 0  # 疲劳等级
        self.tire_accumulate_time = 0  # 疲劳累计时间
        self.keep = 0   # 压制状态
        self.keep_remain_time = 0   # 压制剩余时间

        self.on_board = 0   # 算子是否在车上
        self.car = None  # 算子所属车辆 (在车上时使用)
        self.launcher = None    # 算子所属发射器 (下车后使用)
        self.passenger_ids = []    # 算子搭载成员ID
        self.launch_ids = []   # 已经发射的算子ID

        self.lose_control = 0   # 算子失去控制: 指无人车失去指挥

        self.alive_remain_time = 0  # 巡飞弹剩余存活时间

        self.get_on_remain_time = 0     # 上车剩余时间
        self.get_on_partner_id = []      # 车辆算子ID(本算子为上车算子) 或 待上车算子(本算子为车辆算子)
        self.get_off_remain_time = 0    # 下车剩余时间
        self.get_off_partner_id = []     # 车辆算子ID(本算子为待下车算子) 或 车上算子ID(本算子为车辆算子ID)
        self.change_state_remain_time = 0   # 切换状态
        self.target_state = MoveState.NormalMove    # 目标状态

        self.weapon_cool_time = 0   # 武器冷却时间
        self.weapon_unfold_time = 0  # 武器展开时间

        self.see_enemy_bop_ids = []  # 观察的敌方算子ID列表  Todo 有算子位置变化，血量变为0，切换到掩蔽状态，上下车等(才)需更新此状态

        self.terrain = terrain  # 对地图类的引用

        try:
            self._init_self(data_source=data_source)
        except Exception as e:
            print_exception(e)
            raise e

    def _init_self(self, data_source):
        try:
            if isinstance(data_source, pandas.Series):
                self._init_self_from_series(data_source)
            elif isinstance(data_source, dict):
                self._init_self_from_dict(data_source)
            else:
                raise ValueError
        except Exception as e:
            print_exception(e)
            raise e

    def _init_self_from_series(self, data_source):
        try:
            for key, value in self.dic_map.items():
                if key in data_source.keys():
                    if key == 'S1':
                        self.observe_distance[OperatorType.People] = int(data_source['S1'])
                    elif key == 'S2':
                        self.observe_distance[OperatorType.Car] = int(data_source['S2'])
                    elif key == 'S3':
                        self.observe_distance[OperatorType.Plane] = int(data_source['S3'])
                    elif key == 'ObjPos':
                        self.cur_hex = cvt_int6_to_int4(int(data_source['ObjPos']))
                    elif key == 'GameColor':
                        self.color = Color.name_to_color[data_source['GameColor']]
                    else:
                        try:
                            setattr(self, value['name'], value['fun'](data_source[key]))
                        except Exception as e:
                            print_exception(e)
                            print(value['name'], data_source[key])
                            raise e
            if 'ObjTypeX' not in data_source.keys():
                if self.type == 2:
                    if self.A1 == 1:
                        self.sub_type = 0  # 坦克
                    else:
                        self.sub_type = 1  # 战车
                elif self.type == 1:
                    self.sub_type = 2  # 人员
                if self.name == "炮兵":
                    self.sub_type = 3
                elif self.name == "无人机":
                    self.sub_type = 5
                elif self.name == "武装直升机":
                    self.sub_type = 6
                elif self.name == "无人战车":
                    self.sub_type = 4
                elif self.name == "巡飞弹":
                    self.sub_type = 7
            if 'ObjGuideAbility' not in data_source.keys():
                if self.sub_type in [OperatorSubType.Soldier, OperatorSubType.AutoPlane, OperatorSubType.AutoChariot]:
                    self.guide_ability = 1  # 步兵\无人机\无人战车有引导能力
                else:
                    self.guide_ability = 0
            if 'ObjSonTypes' not in data_source.keys():
                if self.sub_type == OperatorSubType.Chariot:
                    self.valid_passenger_types = [OperatorSubType.Soldier,
                                                  OperatorSubType.AutoChariot,
                                                  OperatorSubType.FlyMissile]  # 战车可以承载人员\无人战车\巡飞弹
                elif self.sub_type == OperatorSubType.Soldier:
                    self.valid_passenger_types = [OperatorSubType.FlyMissile]  # 人员可以承载巡飞弹
                else:
                    self.valid_passenger_types = []
            if 'basic_speed' not in data_source.keys():
                if self.type == OperatorType.People:
                    self.basic_speed = BasicSpeed.People
                elif self.type == OperatorType.Plane:
                    self.basic_speed = BasicSpeed.Plane
                else:
                    self.basic_speed = BasicSpeed.Car
            if "max_passenger_nums" not in data_source.keys():
                if self.valid_passenger_types:
                    self.max_passenger_nums = MaxPassengerNums
        except Exception as e:
            print_exception(e)
            raise e

    def _init_self_from_dict(self, data_source):
        try:
            for key, value in data_source.items():
                setattr(self, key, value)
        except Exception as e:
            print_exception(e)
            raise e


    def can_control(self):
        """
        算子是否可以被控制，不能控制的算子无法作任何动作
        :return: Flag(能否控制), Code(不能控制的原因)
        """
        try:
            if self.on_board:   # 在车上算子无法控制
                return False, ActionResult.CantControlOnBoardOperator
            if self.is_died():  # 死亡算子无法控制
                return False, ActionResult.CantControlDiedOperator
            if self.lose_control:
                return False, ActionResult.CantControlLostControlOperator
            return True, ActionResult.Success
        except Exception as e:
            print_exception(e)
            raise e

    def can_move_shoot(self):
        return self.A1 > 0

    def is_getting_on(self):
        """
        算子是否正在上车
        :return:
        """
        return len(self.get_on_partner_id) > 0

    def is_getting_off(self):
        """算子是否正在下车"""
        return len(self.get_off_partner_id) > 0

    def is_kept(self):
        """是否被压制"""
        return self.keep

    def is_changing_state(self):
        """是否在切换状态"""
        return self.change_state_remain_time > 0

    def is_moving(self):
        return self.speed > 0

    def is_stopping(self):
        return self.stop == 0 and self.move_to_stop_remain_time > 0

    def set_stop_status(self, status):
        self.stop = status

    def is_hiding(self):
        return self.move_state == MoveState.Hide

    def is_marching(self):
        return self.move_state == MoveState.March

    def is_stack(self):
        return self.stack

    def is_weapon_cooling(self):
        return self.weapon_cool_time > 0

    def is_weapon_unfolding(self):
        return self.weapon_unfold_time > 0

    def is_died(self):
        return self.blood <= 0

    def is_on_board(self):
        return self.on_board == 1

    def get_bop_id(self):
        return self.obj_id

    def get_bop_name(self):
        return self.name

    def get_bop_type(self):
        """算子类型"""
        return self.type

    def get_bop_sub_type(self):
        """算子细分类型"""
        return self.sub_type

    def get_tire_level(self):
        """疲劳等级"""
        return self.tire

    def get_move_state(self):
        return self.move_state

    def get_carry_weapons(self):
        return self.carry_weapon_ids

    def get_hex_pos(self):
        """返回当前六角格坐标"""
        return self.cur_hex

    def get_max_observe_distance(self, obj_type):
        if obj_type in self.observe_distance.keys():
            return self.observe_distance[obj_type]
        return 0

    def set_move_state(self, state):
        self.move_state = state

    def set_lose_control(self):
        self.lose_control = 1

    def get_bop_move_path(self):
        return self.move_path

    def set_bop_move_path(self, path):
        self.move_path = path

    def get_guide_ability(self):
        return self.guide_ability

    def get_valid_passenger_types(self):
        return self.valid_passenger_types

    def get_passenger_ids(self):
        return self.passenger_ids

    def get_getting_off_partner_id(self):
        return self.get_off_partner_id

    def get_getting_on_partner_id(self):
        return self.get_on_partner_id

    def set_passenger_ids(self, l):
        self.passenger_ids = l

    def get_launch_ids(self):
        return self.launch_ids

    def get_max_passenger_nums(self, passenger_type):
        if passenger_type in self.max_passenger_nums.keys():
            return self.max_passenger_nums[passenger_type]
        return 0



if __name__ == "__main__":
    pass


