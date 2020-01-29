#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-8 下午1:40
# @Author  : sgr
# @Site    : 
# @File    : operator_sets.py


from common.m_exception import print_exception
from wgoperator.basic_operator import BasicOperator
from wgconst.const import Color
from wgmap.terrain import check_bop_see
from wgconst.const import OperatorType
from wgconst.const import OperatorSubType
from wgconst.const import MaxPassengerNums
from wgstate.getting_on import get_on_end_operation


class OperatorSets:
    """
    算子集合类
    维护算子集合，封装算子查找，检查，修改相关操作
    """
    def __init__(self, loader, terrain, weapon, clock, auto_get_on=True):
        """
        l_ops   # 算子列表 list
        """
        self.loader = loader
        self.terrain = terrain
        self.weapon = weapon
        self.clock = clock

        self.operators = {}  # {'op_id': BasicOperator}
        self.flag_auto_get_on = auto_get_on
        try:
            self.reset()
        except Exception as e:
            print_exception(e)
            raise e

    def load(self):
        """
        Todo 加载数据
        :return:
        """
        try:
            df_operators = self.loader.load_operator()
            for index, ser in df_operators.iterrows():
                bop = BasicOperator(self.terrain, ser)
                self.operators[bop.obj_id] = bop
        except Exception as e:
            print_exception(e)
            raise e

    def reset(self):
        try:
            self.load()
            # if self.flag_auto_get_on:
            #     self.auto_get_on()
        except Exception as e:
            print_exception(e)
            raise e

    def auto_get_on(self):
        try:
            for _, passenger in self.operators.items():
                if passenger.get_bop_sub_type() in MaxPassengerNums.keys():
                    car_bops = self.get_bops_by_condition(pos=passenger.get_hex_pos(), sub_type=OperatorSubType.Chariot,
                                                          color=passenger.get_color())
                    for car in car_bops:
                        if passenger.get_bop_sub_type() not in car.get_valid_passenger_types():
                            continue
                        max_passenger_num = car.get_max_passenger_nums(passenger.get_bop_sub_type())
                        passenger_ids = car.get_passenger_ids()
                        passenger_num = self.count_spec_type_nums(op_ids=passenger_ids,
                                                                           op_type=passenger.get_bop_sub_type())
                        if passenger_num >= max_passenger_num:
                            continue

                        get_on_end_operation(passenger, car)
        except Exception as e:
            print_exception(e)
            raise e

    def load_component(self, operator_data):
        """
        从现有数据中加载核心元素
        :param operator_data: list(dict)
        :return:
        """
        try:
            self.operators = {}
            for op in operator_data:
                bop = BasicOperator(terrain=self.terrain, data_source=op)
                self.operators[bop.obj_id] = bop
        except Exception as e:
            print_exception(e)
            raise e

    def get_bops_by_condition(self, obj_id=None, pos=None, sub_type=None, color=None):
        try:
            if obj_id is not None:
                return [self.operators[obj_id]]
            result = [bop for _, bop in self.operators.items()]
            if pos is not None:
                result = [bop for bop in result if bop.get_hex_pos() == pos]
            if sub_type is not None:
                result = [bop for bop in result if bop.get_bop_sub_type() == sub_type]
            if color is not None:
                result = [bop for bop in result if bop.get_color() == color]
            return result
        except Exception as e:
            print_exception(e)
            raise e

    def get_valid_bops(self):
        try:
            r = []
            for _, bop in self.operators.items():
                flag, result = bop.can_control()
                if flag:
                    r.append(bop)
            return r
        except Exception as e:
            print_exception(e)
            raise e

    def get_valid_bops_by_pos(self, pos):
        """
        根据位置获取算子列表
        :param pos: 四位坐标
        :return:
        """
        try:
            r = []
            for bop in self.get_valid_bops():
                if bop.cur_hex == pos:
                    r.append(bop)
            return []
        except Exception as e:
            print_exception(e)
            raise e

    def get_valid_enemy_bops_by_color(self, color):
        """

        :param color:
        :return:
        """
        try:
            r = []
            if color in Color.enemy_colors.keys():
                enemy_color = Color.enemy_colors[color]
                for e_color in enemy_color:
                    r += self.get_valid_bops_by_color(e_color)
            return r
        except Exception as e:
            print_exception(e)
            raise e

    def get_bop_by_id(self, op_id):
        """
        根据id获取算子
        :param op_id:
        :return:
        """
        if op_id in self.operators.keys():
            return self.operators[op_id]
        return None

    def get_valid_bops_by_color(self, color):
        """
        获取指定颜色的可操作算子
        :param color:
        :return:
        """
        try:
            r = []
            for bop in self.get_valid_bops():
                if bop.color == color:
                    r.append(bop)
            return r
        except Exception as e:
            print_exception(e)
            raise e

    def get_alive_bops_by_color(self, color):
        try:
            bops = []
            for _, bop in self.operators.items():
                if bop.color == color and bop.blood > 0:
                    bops.append(bop)
            return bops
        except Exception as e:
            print_exception(e)
            raise e

    def get_bops_by_color(self, color):
        try:
            bops = []
            for _, bop in self.operators.items():
                if bop.color == color:
                    bops.append(bop)
            return bops
        except Exception as e:
            print_exception(e)
            raise e

    def get_passengers_by_color(self, color):
        try:
            result = []
            for _, bop in self.operators.items():
                if bop.color == color and bop.is_on_board():
                    result.append(bop)
            return result
        except Exception as e:
            print_exception(e)
            raise e

    def get_my_see_bops(self, color):
        """
        获取我方可见所有算子
        :param color:
        :return:
        """
        pass

    def get_my_see_valid_bops(self, color):
        """
        获取我方可见可控制算子
        :param color:
        :return:
        """
        pass

    def get_my_see_valid_enemy_bops(self, color):
        """
        获取我方可见敌方算子
        :param color:
        :return:
        """
        try:
            my_valid_bops = self.get_valid_bops_by_color(color)
            see_enemy_ids = [t_id for bop in my_valid_bops for t_id in bop.get_my_see_enemy_bop_ids()]
            see_enemy_ids = list(set(see_enemy_ids))

            see_bops = []
            for t_id in see_enemy_ids:
                bop = self.get_bop_by_id(t_id)
                if bop is not None:
                    see_bops.append(bop)
            return see_bops
        except Exception as e:
            print_exception(e)
            raise e

    def get_my_see_pos(self, color):
        """
        获取我方算子通视位置
        :param color:
        :return:
        """
        pass

    def count_spec_type_nums(self, op_ids, op_type):
        try:
            count = 0
            for o_id in op_ids:
                bop = self.get_bop_by_id(o_id)
                if bop is not None:
                    if bop.get_bop_sub_type() == op_type:
                        count += 1
            return count
        except Exception as e:
            print_exception(e)
            raise e

    def update(self):
        """
        更新算子各自观察情况
        :return:
        """
        try:
            dic_bops = dict()
            for color in Color.all_colors:
                if color not in dic_bops.keys():
                    dic_bops[color] = self.get_valid_bops_by_color(color)

            for color, observers in dic_bops.items():
                for enemy_color in Color.enemy_colors[color]:
                    enemy_bops = dic_bops[enemy_color]
                    for see_bop in observers:
                        see_bop.set_my_see_enemy_bop_ids([])
                        for be_seen_bop in enemy_bops:
                            if check_bop_see(see_bop, be_seen_bop, self.terrain):
                                see_bop.see_enemy_bop_ids.append(be_seen_bop.obj_id)
        except Exception as e:
            print_exception(e)
            raise e

    def on_bop_hex_changed(self, bop, last_hex):
        try:
            # 更新堆叠状态
            now_hex_bops = self.get_valid_bops_by_pos(bop.get_hex_pos())
            now_hex_bops = [t_bop for t_bop in now_hex_bops if bop.color == t_bop.color and
                            t_bop.get_bop_type() != OperatorType.Plane and t_bop.get_bop_id() != bop.get_bop_id()]
            if now_hex_bops:
                bop.stack = 1
                for t_bop in now_hex_bops:
                    t_bop.stack = 1
            else:
                bop.stack = 0

            last_hex_bops = self.get_valid_bops_by_pos(last_hex)
            last_hex_bops = [t_bop for t_bop in last_hex_bops if bop.color == t_bop.color and
                             t_bop.get_bop_type() != OperatorType.Plane]
            if len(last_hex_bops) == 1:
                last_hex_bops[0].stack = 0

        except Exception as e:
            print_exception(e)
            raise e

    def on_bop_died(self, bop):
        """
        算子死亡
            运载车辆死亡：
                未下车的算子死亡;
                已发射的步兵失去引导单位;
                已发射的无人车失去控制;
                已发射的巡飞弹死亡;
            步兵，无人机，无人车死亡：
                所属发射器的已发射单位中移除该死亡;
        返回失去控制的算子ID列表
        :param bop:
        :return: 返回失去控制的算子ID列表 list()
        """
        try:
            bop.blood = 0
            died_bop_ids = [bop.get_bop_id()]
            if bop.get_bop_sub_type() == OperatorSubType.Chariot:
                passenger_ids = bop.get_passenger_ids()
                if passenger_ids:
                    for p_id in passenger_ids:
                        p_bop = self.get_bop_by_id(p_id)
                        p_bop.blood = 0
                    bop.set_passenger_ids([])
                    died_bop_ids += passenger_ids

                launch_ids = bop.get_launch_ids()
                if launch_ids:
                    for l_id in launch_ids:
                        l_bop = self.get_bop_by_id(l_id)
                        if l_bop.get_bop_sub_type() == OperatorSubType.Soldier:
                            l_bop.set_launcher(None)
                        elif l_bop.get_bop_sub_type() == OperatorSubType.AutoChariot:
                            l_bop.set_lose_control()
                            l_bop.set_launcher(None)
                            died_bop_ids.append(l_id)
                        elif l_bop.get_bop_sub_type() == OperatorSubType.FlyMissile:
                            l_bop.set_blood(0)
                            l_bop.set_launcher(None)
                            died_bop_ids.append(l_id)
                        else:
                            raise ValueError
            elif bop.get_bop_sub_type() in [OperatorSubType.Soldier, OperatorSubType.FlyMissile, OperatorSubType.AutoChariot]:
                launcher = self.get_bop_by_id(bop.get_launcher())
                if launcher is not None:
                    launcher.get_launch_ids().remove(bop.get_bop_id())
                    bop.set_launcher(None)

            return died_bop_ids

        except Exception as e:
            print_exception(e)
            raise e

    def get_bop_observations(self, color=-1):
        try:
            if color in Color.all_colors:
                bop_list = self.get_valid_bops_by_color(color) + self.get_my_see_valid_enemy_bops(color)
            else:
                bop_list = self.get_valid_bops()

            obs = [bop.bop_to_dict() for bop in bop_list]
            return obs
        except Exception as e:
            print_exception(e)
            raise e

    def get_bop_observation_notes(self):
        try:
            return [self.get_valid_bops()[0].bop_to_dict_note()]
        except Exception as e:
            print_exception(e)
            raise e

    def get_remain_and_lost_scores_by_color(self, color):
        try:
            l_alive_bops = self.get_bops_by_color(color)

            remain_score = 0
            lost_score = 0
            for ops in l_alive_bops:
                remain_score += ops.cal_remain_score()
                lost_score += ops.cal_lost_score()

            return remain_score, lost_score
        except Exception as e:
            print_exception(e)
            raise e


if __name__ == "__main__":
    from wgloader.file_loader import FileLoader
    fl = FileLoader(3531)
    ws = OperatorSets(loader=fl, terrain=None, weapon=None, clock=None)
    print(ws.get_bop_observations())
    for operator in ws.operators.values():
        print(operator.name, operator.observe_distance, operator.B1)

    print('done')