#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-8 下午2:49
# @Author  : sgr
# @Site    : 
# @File    : jm_point.py


import random
from common.m_exception import print_exception
from wgconst.const import JMPointStatus
from wgconst.const import JMAlignStatus
from wgstate.shooting import _execute_damage
from wgconst.const import OperatorType
from wgconst.const import TimeParameter


class JMPoint:
    """
    间瞄点类
    """
    max_fly_time = TimeParameter.JMTime["Fly"]
    max_boom_time = TimeParameter.JMTime["Boom"]

    def __init__(self, op_id, weapon_id, target_pos, operator_sets, weapon_sets, terrain, clock):
        """
        op_id   # 算子ID
        set_pos # 设置位置
        wp_id   # 武器编号
        start_step  # 设置时间
        bias    # 是否偏离目标
        fly_time    # 飞行时间
        boom_time   # 爆炸时间
        max_fly_time    # 最大飞行时间
        max_boom_time   # 最大爆炸时间
        valid   # 是否有效
        aim_type    # 较射类型

        operators    # 对算子类的引用
        terrain # 对地图类的引用
        """
        self.op_id = op_id
        self.weapon_id = weapon_id
        self.target_pos = target_pos
        self.operator_sets = operator_sets
        self.weapon_sets = weapon_sets
        self.terrain = terrain
        self.clock = clock
        self.status = JMPointStatus.Flying
        self.fly_time = 0
        self.boom_time = 0
        self.flag_offset = False    # 是否偏移
        self.boom_pos = None
        try:
            self.start_step = clock.get_cur_step()
            self.attack_bop = operator_sets.get_bop_by_id(op_id=self.op_id)
            assert self.attack_bop is not None
            self.distance = self.terrain.get_dis_between_hex(self.attack_bop.get_hex_pos(), self.target_pos)
            self.align_status = JMAlignStatus.NoAlign  # 较射状态
            self.all_judge_info = {}    # 裁决信息 {"裁决发生时步长 int": "裁决信息 list(dict)"}
            # self.align_status = self._judge_align_status()  # 较射状态
        except Exception as e:
            print_exception(e)
            raise e

    def update(self, state_manager):
        try:
            if self.is_flying():
                self.fly_time += self.clock.get_tick()
                if self.fly_time >= self.max_fly_time:
                    self.boom(state_manager)
                    self.status = JMPointStatus.Booming
            elif self.is_booming():
                self.boom_time += self.clock.get_tick()
                if self.boom_time >= self.max_boom_time:
                    self.status = JMPointStatus.Invalid

            return self.is_valid()
        except Exception as e:
            print_exception(e)
            raise e

    def boom(self, state_manager):
        try:
            self.align_status = self._judge_align_status()  # 较射状态
            offset, offset_random = self.weapon_sets.get_jm_offset(self.distance, self.align_status)
            self._set_offset(offset)
            self._jm_judge(state_manager=state_manager)
        except Exception as e:
            print_exception(e)
            raise e

    def get_attack_bop_id(self):
        return self.op_id

    def _jm_judge(self, state_manager):
        try:
            assert self.boom_pos is not None
            bops = self.operator_sets.get_valid_bops_by_pos(self.boom_pos)
            bops = [bop for bop in bops if bop.get_bop_type() != OperatorType.Plane]
            for bop in bops:
                self.jm_judge_per_bop(bop, state_manager)
        except Exception as e:
            print_exception(e)
            raise e

    def jm_judge_per_bop(self, target_bop, state_manager):
        try:
            damage, info = self.weapon_sets.get_jm_damage(attacker_blood=self.attack_bop.get_blood(),
                                           bop_obj=target_bop,
                                           weapon_id=self.weapon_id,
                                           offset=self.flag_offset)

            _execute_damage(target_bop=target_bop, damage=damage, state_manager=state_manager,
                            operator_sets=self.operator_sets)

            if info:
                cur_step = self.clock.get_cur_step()
                info["cur_step"] = cur_step
                info["type"] = "间瞄伤害"
                info["att_obj_id"] = self.op_id
                info["distance"] = self.distance
                info["align_status"] = self.align_status
                if cur_step not in self.all_judge_info.keys():
                    self.all_judge_info[cur_step] = []
                self.all_judge_info[cur_step].append(info)
        except Exception as e:
            print_exception(e)
            raise e

    def is_flying(self):
        return self.status == JMPointStatus.Flying

    def is_booming(self):
        return self.status == JMPointStatus.Booming

    def is_booming_in_pos(self, pos):
        return self.is_booming() and self.boom_pos == pos

    def is_valid(self):
        return self.status != JMPointStatus.Invalid

    def _judge_align_status(self):
        """
        判断较射状态
        :return:
        """
        try:
            see_enemy_bops = self.operator_sets.get_my_see_valid_enemy_bops(color=self.attack_bop.get_color())
            see_has_enemy_pos = list(set([bop.get_hex_pos() for bop in see_enemy_bops]))   # 所有能观察到敌方算子的位置
            if self.target_pos in see_has_enemy_pos:
                return JMAlignStatus.TargetAlign
            my_bops = self.operator_sets.get_valid_bops_by_color(color=self.attack_bop.get_color())
            my_pos = list(set([bop.get_hex_pos() for bop in my_bops]))
            can_see = False
            for m_pos in my_pos:
                mod = 0
                if self.terrain.check_see(m_pos, self.target_pos, mod):
                    can_see = True
                    break
            if can_see:
                return JMAlignStatus.HexAlign
            return JMAlignStatus.NoAlign
        except Exception as e:
            print_exception(e)
            raise e

    def _set_offset(self, offset):
        try:
            if offset > 0:
                dir = random.randint(0, 5)  # 六个方向中随机选择一个方向
                new_pos = self.terrain.get_spec_len_dir_pos(self.target_pos, offset, dir)
                self.boom_pos = new_pos
                self.flag_offset = True
            elif offset == 0:
                self.boom_pos = self.target_pos
                self.flag_offset = True
            else:
                self.boom_pos = self.target_pos
                self.flag_offset = False
        except Exception as e:
            print_exception(e)
            raise e

    def check_color_can_see_self(self, color):
        try:
            if self.status == JMPointStatus.Booming:
                return True
            elif self.status == JMPointStatus.Flying and self.attack_bop.get_color() == color:
                return True
            return False
        except Exception as e:
            print_exception(e)
            raise e

    def to_jm_pt_dict(self):
        return {
            'obj_id': self.op_id,
            "color": self.attack_bop.get_color(),
            'weapon_id': self.weapon_id,
            'pos': self.target_pos if self.status == JMPointStatus.Flying else self.boom_pos,
            'status': self.status,
            'fly_time': self.fly_time,
            'boom_time': self.boom_time
        }

    def get_jm_judge_info(self, cur_step):
        try:
            if cur_step in self.all_judge_info.keys():
                return self.all_judge_info[cur_step]
            return []
        except Exception as e:
            print_exception(e)
            raise e