#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-8 下午2:38
# @Author  : sgr
# @Site    : 
# @File    : jm_weapon.py

import pandas
import numpy
from common.m_exception import print_exception
from common.my_numpy import MyNumpy
from wgconst.const import OperatorType


class JMWeapon:
    """
    间瞄武器类
    """
    MAX_LENGTH = 100
    
    def __init__(self, df_wp_data):
        """
        df_weapons  # 武器属性列表(ID, Name, Type, TarType, TarRange)
        np_no_aim_shoot # 无较射命中表
        np_hex_aim_shoot    # 格内较射命中表
        np_target_aim_shoot # 目标较射命中表
        np_bias_al_to_peo   # 偏差对人攻击等级表
        np_no_bias_al_to_peo   # 命中对人攻击等级表     {id: att[blood][dis] }  間瞄武器不能取人員使用
        np_bias_al_to_car   # 偏差对车攻击等级表
        np_no_bias_al_to_car   # 命中对车攻击等级表
        np_bias_al_to_plane   # 偏差对飞机攻击等级表
        np_no_bias_al_to_plane   # 命中对飞机攻击等级表
        np_bias_damage_to_peo   # 偏差对人战损表
        np_no_bias_damage_to_peo   # 命中对人战损表
        np_bias_damage_to_car   # 偏差对车战损表
        np_no_bias_damage_to_car   # 命中对车战损表
        np_bias_damage_to_plane   # 偏差对飞机战损表
        np_no_bias_damage_to_plane   # 命中对飞机战损表

        terrain # 对地图数据的引用
        """
        try:
            self.id = -1
            self.name = None
            self.flag_guide_ability = False
            self.flag_missile = False
            self.att_range = {0: [0, self.MAX_LENGTH], 1: [0, self.MAX_LENGTH], 2: [0, self.MAX_LENGTH]}
            self.att_types = [OperatorType.People, OperatorType.Car]
            self.np_jm_mz_table = MyNumpy(numpy.zeros(shape=(1, 1)))
            self.np_jm_py_table = MyNumpy(numpy.zeros(shape=(1, 1)))

            self._init_paras(df_wp_data)
        except Exception as e:
            raise e
    
    def _init_paras(self, df):
        try:
            self.id = int(df['WeaponID'].iloc[0])
            self.name = df['ObjName'].iloc[0]
            for idx in range(len(df)):
                df_i = df.iloc[idx]
                if df_i['TarType'] == 0:
                    # 偏移
                    self.np_jm_py_table = MyNumpy(numpy.zeros(shape=(21)))
                    for at_i in range(21):
                        self.np_jm_py_table[at_i] = int(df_i['{}'.format(at_i)])
                elif df_i['TarType'] == 1:
                    # 命中
                    self.np_jm_mz_table = MyNumpy(numpy.zeros(shape=(21)))
                    for at_i in range(21):
                        self.np_jm_mz_table[at_i] = int(df_i['{}'.format(at_i)])
        except Exception as e:
            print_exception(e)
            raise e

    def get_jm_attack_level(self, random, off_set):
        """
        获取攻击等级
        :param random:随机数
        :param off_set:目标算子类型
        :return:
        :return:
        """
        try:
            return int(self.np_jm_py_table[random - 2]) if off_set else int(self.np_jm_mz_table[random - 2])
        except Exception as e:
            print_exception(e)
            return -1

    def get_att_obj_types(self):
        return self.att_types

    def is_missile(self):
        return self.flag_missile

    def get_damage(self, attack_op, target_op, wp_id, aim_type):
        """
        获取战损
        :param attack_op: 攻击算子
        :param target_op: 目标算子
        :param wp_id: 武器编号
        :param aim_type: 较射类型
        :return:
        """
        pass
    

if __name__ == '__main__':
    pass