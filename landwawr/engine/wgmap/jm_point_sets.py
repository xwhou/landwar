#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-8 下午2:47
# @Author  : sgr
# @Site    : 
# @File    : jm_point_sets.py


from common.m_exception import print_exception
from wgmap.jm_point import JMPoint
from wgconst.const import Color


class JMPointSets:
    """
    炮瞄点集合
    """
    def __init__(self, operator_sets, weapon_sets, terrain, clock):
        """
        l_jm_points # 炮瞄点列表 list
        """
        self.operator_sets = operator_sets
        self.weapon_sets = weapon_sets
        self.terrain = terrain
        self.clock = clock

        self.l_jm_points = []  # [JMPoint]

    def get_my_see_points(self, color):
        """
        获取我方可见炮瞄点
        :param color:
        :return:
        """
        try:
            if color == Color.GREEN:
                return self.l_jm_points
            else:
                return [jm_pt for jm_pt in self.l_jm_points if jm_pt.check_color_can_see_self(color)]
        except Exception as e:
            print_exception(e)
            raise e

    def reset(self):
        try:
            self.l_jm_points = []
        except Exception as e:
            print_exception(e)
            raise e

    def update(self, state_manager):
        """
        更新炮瞄点状态
        :return:
        """
        for pt in self.l_jm_points:
            valid = pt.update(state_manager=state_manager)
            if not valid:
                self.l_jm_points.remove(pt)

    def add_jm_point(self, op_id, weapon_id, target_pos):
        try:
            j_pt = JMPoint(op_id=op_id,
                           weapon_id=weapon_id,
                           target_pos=target_pos,
                           operator_sets=self.operator_sets,
                           weapon_sets=self.weapon_sets,
                           terrain=self.terrain,
                           clock=self.clock
            )
            self.l_jm_points.append(j_pt)
        except Exception as e:
            print_exception(e)
            raise e

    def on_bop_hex_changed(self, bop, state_manager):
        try:
            valid_jm_points = self.get_booming_points_in_pos(pos=bop.get_hex_pos())
            for jm_point in valid_jm_points:
                jm_point.jm_judge_per_bop(target_bop=bop,
                                          state_manager=state_manager)
        except Exception as e:
            print_exception(e)
            raise e

    def get_booming_points_in_pos(self, pos):
        try:
            return [jm_pt for jm_pt in self.l_jm_points if jm_pt.is_booming_in_pos(pos=pos)]
        except Exception as e:
            print_exception(e)
            raise e

    def get_flying_points_by_bop(self, obj_id):
        try:
            return [jm_pt for jm_pt in self.l_jm_points if jm_pt.is_flying() and jm_pt.get_attack_bop_id() == obj_id]
        except Exception as e:
            print_exception(e)
            raise e

    def get_jm_observations(self, color):
        try:
            jm_points = self.get_my_see_points(color)
            return [jm_pt.to_jm_pt_dict() for jm_pt in jm_points]
        except Exception as e:
            print_exception(e)
            raise e

    def get_jm_observations_notes(self):
        return [{
            "obj_id": "攻击算子ID int",
            'weapon_id': "攻击武器ID int",
            'pos': "位置 int",
            'status': "当前状态 0-正在飞行 1-正在爆炸 2-无效",
            'fly_time': "剩余飞行时间 float",
            'boom_time': "剩余爆炸时间 float"
        }]

    def get_jm_judge_info(self, color, cur_step):
        try:

            jm_points = self.get_my_see_points(color)
            return [info for pt in jm_points for info in pt.get_jm_judge_info(cur_step)]
            # result = []
            # for pt in jm_points:
            #     result += pt.get_jm_judge_info(cur_step)
            # return result
        except Exception as e:
            print_exception(e)
            raise e

    def get_jm_judge_notes(self):
        return [{
            "cur_step": "当前步长",
            "type": "伤害类型 str",
            "att_obj_id": "攻击算子ID, int",
            "distance": "距离",
            "align_status": "较射类型 int 0-无较射 1-格内较射 2-目标较射",
            "target_obj_id": "目标算子ID int",
            "att_obj_blood": "攻击算子血量",
            "wp_id": "武器ID int",
            "offset": "偏移 bool",
            "random1": "随机数1 int",
            "ori_damage": "原始战损",
            "random2_rect": "随机数2修正值",
            "random2": "随机数2",
            "rect_damage": "战损修正值",
            "damage": "最终战损"
        }]


if __name__ == "__main__":
    a = [[1] * 5] * 15
    import time
    t1 = time.time()
    for i in range(10):
        print([a1 for b in a for a1 in b])
    t2 = time.time()

    for i in range(10):
        result = []
        for a1 in a:
            result += a1
        print(result)

    t3 =time.time()

    print(t2-t1, t3-t2)


