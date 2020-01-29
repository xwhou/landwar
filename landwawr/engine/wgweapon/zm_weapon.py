#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-8 下午2:30
# @Author  : sgr
# @Site    : 
# @File    : zm_weapon.py

import numpy
from common.m_exception import print_exception
from wgconst.const import OperatorType
from wgmessage.action_result import ActionResult
from wgconst.const import InvalidDamage
from common.my_numpy import MyNumpy


class ZMWeapon:
    """
    直瞄武器类
    """
    def __init__(self, df_wp_data):
        """
        df_weapons  # 武器属性列表(ID, Name, Type, TarType, TarRange)
        df_al_to_peo    # 对人攻击等级表
        df_al_to_car    # 对车攻击等级表
        df_al_to_plane  # 对飞机攻击等级表
        np_damage_to_peo    # 对人损伤表
        np_damage_to_car    # 对车损伤表
        np_damage_to_plane  # 对飞机损伤表
        terrain # 对地图数据的引用
        """
        self.id = -1
        self.name = None
        self.flag_guide_ability = False
        self.flag_missile = False
        self.att_range = {}  # { Tartype: [min_dis, max_dis]} Todo 此处不准确 同一武器对同一类型算子射程还受攻击方算子血量影响
        self.att_types = []
        self.to_peo_table = MyNumpy(numpy.zeros(shape=(1, 1)))
        self.to_car_table = MyNumpy(numpy.zeros(shape=(1, 1)))
        self.to_plane_table = MyNumpy(numpy.zeros(shape=(1, 1)))
        try:
            self._init_paras(df_wp_data)
        except Exception as e:
            print_exception(e)
            raise e
    
    def _init_paras(self, df):
        try:
            self.id = int(df['WeaponID'].iloc[0])
            self.name = df['ObjName'].iloc[0]
            for idx in range(len(df)):
                df_i = df.iloc[idx]
                if df_i['TarType'] not in self.att_types:
                    self.att_types.append(int(df_i['TarType']))
                    self.att_range[int(df_i['TarType'])] = [int(df_i['AttMin']), int(df_i['AttMax'])]
                    self.flag_missile = False if int(df_i['F0']) == 0 else True
                    self.flag_guide_ability = False if int(df_i['F1']) == 0 else True
                    if int(df_i['TarType']) == 1:
                        self.to_peo_table = MyNumpy(numpy.zeros(shape=(5, 21)))
                    elif int(df_i['TarType']) == 2:
                        self.to_car_table = MyNumpy(numpy.zeros(shape=(21)))
                    elif int(df_i['TarType']) == 3:
                        self.to_plane_table = MyNumpy(numpy.zeros(shape=(21)))
                if int(df_i['TarType']) == 1:
                    for at_i in range(21):
                        self.to_peo_table[int(df_i['ObjBlood']) - 1, at_i] = int(df_i['{}'.format(at_i)])
                elif int(df_i['TarType']) == 2:
                    for at_i in range(21):
                        self.to_car_table[at_i] = int(df_i['{}'.format(at_i)])
                elif int(df_i['TarType']) == 3:
                    for at_i in range(21):
                        self.to_plane_table[at_i] = int(df_i['{}'.format(at_i)])
        except Exception as e:
            print_exception(e)
            raise e

    def get_zm_attack_level(self, length, obj_type, att_blood=4):
        """
        返回攻击等级
        :param length:攻击距离
        :param obj_type:目标算子类型
        :param att_blood:攻击算子的班淑
        :return: 无效返回InvalidDamage 有效返回int
        """
        try:
            level = InvalidDamage.InvalidAttackLevel
            if obj_type in self.att_types:
                if obj_type == OperatorType.People:
                    level = self.to_peo_table[att_blood-1, length]
                elif obj_type == OperatorType.Car:
                    level = self.to_car_table[length]
                elif obj_type == OperatorType.Plane:
                    level = self.to_plane_table[length]
            return level
        except Exception as e:
            print_exception(e)
            return InvalidDamage.InvalidAttackLevel

    def get_att_obj_types(self):
        return self.att_types

    def get_att_range(self, tar_type):
        if tar_type in self.att_range.keys():
            return self.att_range[tar_type]
        return [-1, -1]

    def is_missile(self):
        return self.flag_missile

    def can_be_guided(self):
        return self.flag_guide_ability