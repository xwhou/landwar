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

    def can_move(self):
        """
        算子是否可以机动
        :return: (FLAG, DETAIL)
        """
        try:
            action_flag, reason = self.can_do_action()
            if not action_flag:  # 无法做动作
                return False, reason
            if self.is_moving():
                return False, ActionResult.CantMoveWhenMoving
            if self.get_tire_level() >= 2:
                return False, ActionResult.CantMoveUnderTireLv2     # 二级疲劳算子无法机动
            if self.get_move_state() == MoveState.Charge_2 and self.get_tire_level() >= 1:
                return False, ActionResult.CantCharge2UnderTireLv1  # 一级疲劳无法二级冲锋
            if self.get_bop_type() == OperatorType.People and self.is_kept():
                return False, ActionResult.CantMoveKeptPeople   # 步兵被压制
            if self.get_move_state() == MoveState.March:
                if self.get_bop_type() != OperatorType.Car:
                    return False, ActionResult.CantMarchNotCar  # 非车辆无法行军
                if not self.terrain.has_road(self.get_hex_pos()):
                    return False, ActionResult.CantMarchOnNotRoad   # 无法在非非公路上行军
            return True, ActionResult.Success
        except Exception as e:
            print_exception(e)
            raise e

    def can_shoot(self):
        """
        算子是否可以射击
        :return: (Flag, Detail)
        """
        try:
            action_flag, reason = self.can_do_action()
            if not action_flag:  # 无法做动作
                return False, reason
            if self.is_weapon_cooling():
                return False, ActionResult.WeaponCooling
            if self.get_move_state() == MoveState.March:
                return False, ActionResult.CantShootUnderMarch
            if not self.can_move_shoot():
                if self.is_moving():
                    return False, ActionResult.CantShootWhenMoving
                if self.is_weapon_unfolding():
                    return False, ActionResult.WeaponUnfolding
            if self.get_bop_type() == OperatorType.People and self.is_kept():
                return False, ActionResult.CantShootByKeptPeo
            if self.get_bop_sub_type() == OperatorSubType.FlyMissile and not self.get_launcher():
                return False, ActionResult.CantShootByUnLunchedFlyMissile
            return True, ActionResult.Success
        except Exception as e:
            print_exception(e)
            raise e

    def can_guide(self):
        try:
            action_flag, reason = self.can_do_action()
            if not action_flag:  # 无法做动作
                return False, reason
            if self.is_moving():
                return False, ActionResult.CantGuideCauseMoving
            if not self.get_guide_ability():
                return False, ActionResult.CantGuideCauseLackAbility
            if self.get_bop_sub_type() in [OperatorSubType.Soldier, OperatorSubType.AutoChariot]:
                if not self.get_launcher():
                    return False, ActionResult.CantGuideCauseNotLaunched
            if self.is_weapon_cooling():
                return False, ActionResult.CantGuideCauseWeaponCooling
            if self.get_bop_sub_type() == OperatorSubType.Soldier:
                # if self.is_moving():
                #     return False, ActionResult.CantGuideCausePeoMoving
                if self.is_kept():
                    return False, ActionResult.CantGuideCausePeoKept
            return True, ActionResult.Success
        except Exception as e:
            print_exception(e)
            raise e

    def can_jm_plan(self):
        try:
            action_flag, reason = self.can_do_action()
            if not action_flag:  # 无法做动作
                return False, reason
            if self.is_moving():
                return False, ActionResult.CantGuideCauseMoving
            if not self.get_bop_sub_type() == OperatorSubType.Artillery:
                return False, ActionResult.CantJMCauseNotArtillery
            if self.is_weapon_cooling():
                return False, ActionResult.CantJMCauseWeaponCooling
            if self.is_weapon_unfolding():
                return False,ActionResult.CantJMCauseWeaponUnfolding
            return True, ActionResult.Success
        except Exception as e:
            print_exception(e)
            raise e

    def can_get_on(self):
        try:
            action_flag, reason = self.can_do_on_and_off_action()
            if not action_flag:  # 无法做动作
                return False, reason
            if not self.get_bop_sub_type() in [OperatorSubType.Soldier,
                                               OperatorSubType.AutoChariot,
                                               OperatorSubType.FlyMissile]:
                return False, ActionResult.CantGetOnCauseWrongObjectType
            if self.get_bop_sub_type() == OperatorSubType.Soldier and self.is_kept():
                return False, ActionResult.CantGetOnCausePeoKept
            if self.is_moving():
                return False, ActionResult.CantGetOnWhenMoving
            return True, ActionResult.Success
        except Exception as e:
            print_exception(e)
            raise e

    def can_get_off(self):
        try:
            action_flag, reason = self.can_do_on_and_off_action()
            if not action_flag:  # 无法做动作
                return False, reason
            if self.is_moving():
                return False, ActionResult.CantGetOffWhenMoving
            if self.is_kept():
                return False, ActionResult.CantGetOffCauseCarKept
            if not self.get_passenger_ids():
                return False, ActionResult.CantGetOffCauseNoPassengers
            return True, ActionResult.Success
        except Exception as e:
            print_exception(e)
            raise e

    def can_switch_state(self):
        try:
            flag, code = self.can_do_action()
            if not flag:
                return False, code
            if self.is_moving():
                return False, ActionResult.CantSwitchStateWhenMoving
            return True, ActionResult.Success
        except Exception as e:
            print_exception(e)
            raise e

    def can_occupy(self):
        try:
            flag, code = self.can_control()
            if not flag:
                return False, code
            if self.get_bop_type() == OperatorType.Plane:
                return False, ActionResult.CantOccupyCausePlane
            return True, ActionResult.Success
        except Exception as e:
            print_exception(e)
            raise e

    def can_remove_keep(self):
        try:
            flag, code = self.can_control()
            if not flag:
                return False, code
            if not self.get_bop_type() == OperatorType.People:
                return False, ActionResult.CantRemoveKeepCauseNotPeo
            if not self.is_kept():
                return False, ActionResult.CantRemoveKeepCauseNotKept
            if self.blood <= 1:
                return False, ActionResult.CantRemoveKeepCauseLackBlood
            return True, ActionResult.Success
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

    def can_do_action(self):
        try:
            control_flag, reason = self.can_control()
            if not control_flag:  # 算子无法控制
                return False, reason
            if self.is_getting_on():
                return False, ActionResult.CantActionWhenGettingOn   # 算子正在上车,无法打断
            if self.is_getting_off():
                return False, ActionResult.CantActionWhenGettingOff  # 算子正在下车,无法打断
            if self.is_changing_state():
                return False, ActionResult.CantActionWhenChangingState
            if self.is_stopping():
                return False, ActionResult.CantActionWhenStopping
            return True, ActionResult.Success
        except Exception as e:
            print_exception(e)
            raise e

    def can_do_on_and_off_action(self):
        try:
            control_flag, reason = self.can_control()
            if not control_flag:  # 算子无法控制
                return False, reason
            if self.is_moving():
                return False, ActionResult.CantGuideCauseMoving
            if self.get_bop_sub_type() != OperatorSubType.Chariot:
                if self.is_getting_on():
                    return False, ActionResult.CantActionWhenGettingOn  # 算子正在上车,无法打断
                if self.is_getting_off():
                    return False, ActionResult.CantActionWhenGettingOff  # 算子正在下车,无法打断
            if self.is_changing_state():
                return False, ActionResult.CantActionWhenChangingState
            if self.is_stopping():
                return False, ActionResult.CantActionWhenStopping
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

    def set_move_state(self, state):
        self.move_state = state

    def set_lose_control(self):
        self.lose_control = 1

    def get_bop_move_path(self):
        return self.move_path

    def set_bop_move_path(self, path):
        self.move_path = path

    def get_terrain_move_type(self):
        if self.get_bop_type() == OperatorType.People:
            return TerrainMoveType.PeoMove
        elif self.get_bop_type() == OperatorType.Car:
            if self.get_move_state() == MoveState.March:
                return TerrainMoveType.CarMarch
            else:
                return TerrainMoveType.CarMove
        else:
            return TerrainMoveType.PeoMove

    def get_hex_pos(self):
        """返回当前六角格坐标"""
        return self.cur_hex

    def set_hex_pos(self, pos):
        self.cur_hex = pos

    def get_basic_speed(self):
        """返回地形无关速度"""
        return self.basic_speed

    def get_blood(self):
        return self.blood

    def set_blood(self, blood):
        self.blood = blood

    def get_armor(self):
        return self.armor

    def get_color(self):
        return self.color

    def get_carry_weapons(self):
        return self.carry_weapon_ids

    def get_missile_num(self):
        return self.C3

    def set_missile_num(self, n):
        self.C3 = n

    def get_bullet_num(self):
        return self.C2

    def set_bullet_num(self, n):
        self.C2 = n

    def get_launcher(self):
        return self.launcher

    def set_launcher(self, l):
        self.launcher = l

    def get_max_observe_distance(self, obj_type):
        if obj_type in self.observe_distance.keys():
            return self.observe_distance[obj_type]
        return 0

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

    def cal_remain_score(self):
        return self.blood * self.value

    def cal_lost_score(self):
        return (self.max_blood - self.blood) * self.value

    def init_states(self):
        """
        获取初始化状态集合
        :return:
        """
        pass

    def receive_actions(self, action_msg):
        """
        收到动作消息
        根据动作信息，获取指定类型的状态对象，调用该对象的check方法
        若通过：将该消息加入 todo_action_msg_sets 中
        若不通过： 记录错误信息，将其移到完成队列中
        :param action_msg:
        :return:
        """
        pass

    def step(self, count=1):
        """
        更新算子状态
        遍历 todo_action_msg_sets ，调用对应state对象的enter方法
        遍历active_states集合，调用每个state对象的step方法，判断状态是否结束
        如果结束：从active_states中移除
        :param count:
        :return:
        """
        pass

    def get_my_see_enemy_bop_ids(self):
        """
        获取我可视敌方算子
        :return: [bop_id]
        """
        return self.see_enemy_bop_ids

    def set_my_see_enemy_bop_ids(self, l):
        self.see_enemy_bop_ids = l

    def get_my_see_pos(self):
        """
        获取我可视位置
        :return: [pos]
        """
        pass

    def set_damage(self, damage):
        """
        返回算子是否死亡
        :param damage:
        :return: True-死亡 False-未死亡
        """
        try:
            if self.get_bop_type() == OperatorType.People and self.is_kept() and damage == 0:
                damage = 1
            if damage >= 0:
                self.blood = int(self.blood - damage)
                self.keep = 1

            if self.blood <= 0:
                self.blood = 0
                return True
            return False
        except Exception as e:
            print_exception(e)
            raise e

    def bop_to_dict(self):
        try:
            values = dict(vars(self))
            values.pop('terrain')
            return values
        except Exception as e:
            print_exception(e)
            raise e

    def bop_to_dict_note(self):
        try:
            return {
                "obj_id": "算子ID int",
                "color": "算子阵营 0-红 1-蓝",
                "type": "算子类型 1-步兵 2-车辆 3-飞机",
                "name": "名称 str",
                "sub_type": "细分类型 坦克 0/  战车1 / 人员2 / 炮兵3 / 无人战车4 / 无人机5 / 直升机6 / 巡飞弹7",
                "basic_speed": "基础速度 int",
                "armor": "装甲类型 int 0-无装甲 1-轻型装甲 2-中型装甲 3-重型装甲 4-复合装甲",
                "A1": "是否有行进间射击能力 int",
                "stack": "是否堆叠 int",
                "carry_weapon_ids": "携带武器ID list(int)",
                "C3": "剩余导弹数 int",
                "C2": "剩余子弹数 int",
                "guide_ability": "是否有引导射击能力 int",
                "value": "分值 int",
                "valid_passenger_types": "可承载类型 list(int)",
                "max_passenger_nums": "最大承载数 dict()",
                "space": "容量 int",
                "observe_distance": "观察距离 dict()",
                "move_state": "机动状态 0-正常机动 1-行军 2-一级冲锋 3-二级冲锋 4-掩蔽",
                "cur_hex": "当前坐标 int 四位",
                "cur_pos": "当前格到下一格的百分比进度 float",
                "speed": "当前速度 int",
                "move_to_stop_remain_time": "停止机动剩余时间",
                "stop": "是否静止 0-否, 1-是",
                "move_path": "机动路径 [int] 首个元素代表下一目标格",
                "blood": "当前血量 int",
                "max_blood": "最大血量 int",
                "tire": "疲劳等级 0-不疲劳 1-一级疲劳 2-二级疲劳 int",
                "tire_accumulate_time": "疲劳累积时间 int",
                "keep": "是否被压制 int",
                "keep_remain_time": "疲劳剩余时间 int",
                "on_board": "是否在车上 int",
                "car": "所属车辆ID int",
                "launcher": "所属发射器 int",
                "passenger_ids": "乘客列表 [int]",
                "launch_ids": "发射单元列表 [int]",
                "get_on_remain_time": "上车剩余时间 float",
                "get_on_partner_id": "正在上车目标ID int",
                "get_off_remain_time": "下车剩余时间 float",
                "change_state_remain_time": "切换状态剩余时间 float",
                "target_state": "目标状态 int",
                "weapon_cool_time": "武器剩余冷却时间 float",
                "weapon_unfold_time": "武器剩余展开时间 float",
                "see_enemy_bop_ids": "观察敌方算子列表 list(int)"

            }

        except Exception as e:
            print_exception(e)
            raise e


if __name__ == "__main__":
    pass


