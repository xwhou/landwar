#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-12-10 下午3:42
# @Author  : sgr
# @Site    : 
# @File    : demo_ai.py


import sys
sys.path.append("../wginterface/")
import random
from common.m_exception import print_exception
from ai.base_ai import BaseAI
import __wgobject as wgobject
import numpy as np


class DemoAI(BaseAI):
    def __init__(self, color, obj_interface, interface_wgruler):
        super(DemoAI, self).__init__(color, obj_interface, interface_wgruler)
        self.count = 0


    def run(self):
        '''
        更新态势,判断游戏是否结束,若尚未结束则调用_do_action()生成并执行动作
        :return: True
        '''
        try:
            # super(RandomAI, self).step()
            # 态势更新
            self.update_state_data()
            if self.game_over:
                print("Game Over")
                return False

            if len(self.operators) == 0:
                self.obj_interface.setNull()
                return True

            if self.count >= len(self.operators):
                self.count = 0
            cur_bop = self.operators[self.count]  # RJ_operator
            self.count += 1
            return self._do_action(self.color, cur_bop)
        except Exception as e:
            print_exception(e)
            raise e

    def _do_action(self, flag_color, cur_bop):
        '''
        生成并执行动作
        :param flag_color: int型,游戏方阵营颜色
        :param cur_bop: 当前生成动作的算子
        :return: True
        '''
        try:
            l_enemybops = self.enemy_operators
            l_cities = self.cities
            # if len(l_enemybops)>0:
            #     obop = wgobject.Gen_Op(cur_bop)
            #     ubop = wgobject.Gen_Op(l_enemybops[0])
            #     np_wicg_map_mask = self.obj_interface.cal_blind_map(obop,ubop)

            # 夺控动作
            if self.genOccupyAction(cur_bop):
                if self.obj_interface.setOccupy(cur_bop.ID) == 0:
                    return True

            # 射击动作
            for obj_bop in l_enemybops:
                flag, weaponID = self.genShootAction(cur_bop, obj_bop)
                if flag:
                    flag_shoot, _ = self.obj_interface.setFire(cur_bop.ID, obj_bop.ID,
                                                               (int)(weaponID))
                    if flag_shoot == 0:
                        return True

            # 人员下车
            if cur_bop.ObjTypeX == 1 and cur_bop.ObjSonNum > 0:
                for city in l_cities:
                    _,dis = self.obj_interface.getMapDistance(cur_bop.ObjPos, city['coord_int6'])
                    if dis <= 3:
                        if cur_bop.ObjKeep == 0:
                            if self.obj_interface.setGetoff(cur_bop.ID) == 0:
                                return True

            # 随机选择非我方夺控点并机动
            list_loc_notmycity = self.interface_wgruler.updateNotMyCityList(l_cities, flag_color)
            city = random.choice(list_loc_notmycity) if list_loc_notmycity else \
                random.choice(l_cities)
            city_loc = city['coord_int6']

            # 机动
            flag_move = True
            if cur_bop.ObjTypeX in [1, 2]:
                for ubop in l_enemybops:
                    _,flag_see = self.obj_interface.flagISU(cur_bop, ubop)
                    _, distance = self.obj_interface.getMapDistance(cur_bop.ObjPos, ubop.ObjPos)
                    if flag_see and (distance <= (10 if cur_bop.ObjTypeX == 2 else 20)):
                        self.obj_interface.setNull()
                        return True

            if flag_move:
                if cur_bop.ObjPos != city_loc:
                    flag, l_path = self.genMoveAction(cur_bop, city_loc)
                    if flag and l_path:
                        if self.obj_interface.setMove(cur_bop.obj_id, l_path) == 0:
                            return True
            self.obj_interface.setNull()
            return True

        except Exception as e:
            print_exception(e)
            raise e

    def _choose_move_paras(self, bop):
        '''
        生成机动路径字段
        :param bop: 执行机动动作的算子
        :return: {"move_path": [机动路径]}
        '''
        try:
            target_pos = self._choose_random_pos()
            move_path = self.obj_interface.spath.get_path(bop.cur_hex, target_pos, mod=0)
            return {"move_path": move_path}
        except Exception as e:
            print_exception(e)
            raise e

    def _choose_random_pos(self):
        return random.randint(3, 55) * 100 + random.randint(3, 50)

    def genOccupyAction(self, cur_bop):
        '''
        判断是否可以夺控
        :param cur_bop:
        :return: True/可以夺控,False/不能夺控
        '''
        try:
            list_loc_notmycity = self.interface_wgruler.updateNotMyCityList(self.cities, cur_bop.color)
            list_ubops = self.enemy_operators

            if self.interface_wgruler.OccupyCheck(cur_bop, list_loc_notmycity, list_ubops) == 'O':
                return True
            return False
        except Exception as e:
            print_exception(e)
            raise
        except KeyboardInterrupt as k:
            print_exception(k)
            raise

    def genShootAction(self,bop_attacker, bop_obj):
        '''
        判断能否射击
        :param bop_attacker:
        :param bop_obj:
        :return: (True,wp_index)/(能射击,武器编号),(False,None)/(不能射击，None)
        '''
        try:
            flag_str_shooting = self.interface_wgruler.ShootCheck(bop_attacker, bop_obj)
            # _, dis = self.obj_interface.getMapDistance(bop_attacker.ObjPos, bop_obj.ObjPos)
            # if dis > 2 and bop_obj.ObjType == 3:
            #     flag_str_shooting = 'N'

            if flag_str_shooting != 'N':
                flag_success, wp_index = self.obj_interface.chooseWeaponIndex(bop_attacker, bop_obj)  # 获取武器编号
                if flag_success == 0:
                    return (True, wp_index)
            return (False, None)
        except Exception as e:
            print_exception(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            print_exception(" " + str(k))
            self.__del__()
            raise

    def genMoveAction(self, cur_bop, obj_pos):
        '''
        判断是否机动,若机动，返回机动路线
        :param cur_bop: 机动算子
        :param obj_pos: 目标位置
        :return: (True,list)/(需要机动，机动路线),(False,None)/(不机动，None)
        '''
        try:
            flag_str_moving = self.interface_wgruler.MoveCheck(cur_bop)
            assert flag_str_moving in ['N', 'M', 'O']
            if flag_str_moving == 'M':
                flag_result, list_movepath = self.obj_interface.getMovePath(cur_bop, obj_pos)
                # flag_result, list_movepath = obj_interface.getMovePath(cur_bop, obj_pos)
                if (flag_result == 0):
                    return True, list_movepath
            return False, None
        except Exception as e:
            print_exception(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            print_exception(" " + str(k))
            self.__del__()
            raise
