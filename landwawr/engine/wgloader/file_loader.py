#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-14 上午8:23
# @Author  : sgr
# @Site    : 
# @File    : file_loader.py


import os
import pandas
import numpy
from common.m_exception import print_exception
from wgloader.loader import Loader
from common.my_numpy import MyNumpy


class FileLoader(Loader):
    def __init__(self, scenario, data_dir="../../"):
        self.data_dir = data_dir
        str_dir_weapons = os.path.join(data_dir, "Data/weapons")
        self.str_wp_data = os.path.join(str_dir_weapons, 'WpData.xls')
        self.str_wp2peo_judge_0 = os.path.join(str_dir_weapons, 'anyweapen2people_0_forPythonJuder')
        self.str_wp2peo_judge_1 = os.path.join(str_dir_weapons, 'anyweapen2people_1_forPythonJuder')
        self.str_wp2air_judge = os.path.join(str_dir_weapons, 'anyweapen2air')
        self.str_zm2car_judge_0 = os.path.join(str_dir_weapons, 'zm2car_0_forPythonJuder')
        self.str_zm2car_judge_1 = os.path.join(str_dir_weapons, 'zm2car_1_forPythonJuder')
        self.str_zm2car_judge_2 = os.path.join(str_dir_weapons, 'zm2car_2_forPythonJuder')
        self.str_ele_rect_to_peo = os.path.join(str_dir_weapons, 'ele_rect_to_peo')
        self.str_ele_rect_to_car = os.path.join(str_dir_weapons, 'ele_rect_to_car')
        self.str_jm_offset_0 = os.path.join(str_dir_weapons, 'jm_offset_0')
        self.str_jm_offset_1 = os.path.join(str_dir_weapons, 'jm_offset_1')
        self.str_jm_offset_2 = os.path.join(str_dir_weapons, 'jm_offset_2')

        self.str_dir_operators = os.path.join(data_dir, "Data/operators")
        super(FileLoader, self).__init__(scenario=scenario, data_dir=data_dir)

    def load_operator(self):
        try:
            file = os.path.join(self.str_dir_operators, 'operators_'+str(self.operators_id)+'.xlsx')
            df_operators = pandas.read_excel(file, 'operators')
            return df_operators
        except Exception as e:
            print_exception(e)
            raise e

    def load_terrain(self):
        return super(FileLoader, self).load_terrain()

    def load_weapon(self):
        """
        Bug Fix 2019年12月05日 ndarray中数据类型为int64 or int32,无法序列化为json object. 做强制类型转化MyNumpy;
            问题: 只支持__getitem__,  __setitem__, shape
        """
        try:
            assert os.path.isfile(self.str_wp_data), '{} not exist'.format(self.str_wp_data)
            assert os.path.isfile(self.str_wp2peo_judge_0), '{} not exist'.format(self.str_wp2peo_judge_0)
            assert os.path.isfile(self.str_wp2peo_judge_1), '{} not exist'.format(self.str_wp2peo_judge_1)
            assert os.path.isfile(self.str_wp2air_judge), '{} not exist'.format(self.str_wp2air_judge)
            assert os.path.isfile(self.str_zm2car_judge_0), '{} not exist'.format(self.str_zm2car_judge_0)
            assert os.path.isfile(self.str_zm2car_judge_1), '{} not exist'.format(self.str_zm2car_judge_1)
            assert os.path.isfile(self.str_zm2car_judge_2), '{} not exist'.format(self.str_zm2car_judge_2)
            assert os.path.isfile(self.str_ele_rect_to_peo), '{} not exist'.format(self.str_ele_rect_to_peo)
            assert os.path.isfile(self.str_ele_rect_to_car), '{} not exist'.format(self.str_ele_rect_to_car)
            assert os.path.isfile(self.str_jm_offset_0), '{} not exist'.format(self.str_jm_offset_0)
            assert os.path.isfile(self.str_jm_offset_1), '{} not exist'.format(self.str_jm_offset_1)
            assert os.path.isfile(self.str_jm_offset_2), '{} not exist'.format(self.str_jm_offset_2)

            dic_weapon = dict()
            dic_weapon['df_wp_data'] = pandas.read_excel(self.str_wp_data)
            dic_weapon['np_wp2peo_judge_0'] = MyNumpy(numpy.loadtxt(self.str_wp2peo_judge_0, dtype=numpy.int))
            dic_weapon['np_wp2peo_judge_1'] = MyNumpy(numpy.loadtxt(self.str_wp2peo_judge_1, dtype=numpy.int))
            dic_weapon['np_wp2air_judge'] = MyNumpy(numpy.loadtxt(self.str_wp2air_judge, dtype=numpy.int))
            dic_weapon['np_zm2car_judge_0'] = MyNumpy(numpy.loadtxt(self.str_zm2car_judge_0, dtype=numpy.int))
            dic_weapon['np_zm2car_judge_1'] = MyNumpy(numpy.loadtxt(self.str_zm2car_judge_1, dtype=numpy.int))
            dic_weapon['np_zm2car_judge_2'] = MyNumpy(numpy.loadtxt(self.str_zm2car_judge_2, dtype=numpy.int))
            dic_weapon['np_jm_offset_0'] = MyNumpy(numpy.loadtxt(self.str_jm_offset_0, dtype=numpy.int))
            dic_weapon['np_jm_offset_1'] = MyNumpy(numpy.loadtxt(self.str_jm_offset_1, dtype=numpy.int))
            dic_weapon['np_jm_offset_2'] = MyNumpy(numpy.loadtxt(self.str_jm_offset_2, dtype=numpy.int))
            dic_weapon['np_ele_rect_to_peo'] = MyNumpy(numpy.loadtxt(self.str_ele_rect_to_peo, dtype=numpy.int))
            dic_weapon['np_ele_rect_to_car'] = MyNumpy(numpy.loadtxt(self.str_ele_rect_to_car, dtype=numpy.int))
            return dic_weapon
        except Exception as e:
            print_exception(e)
            raise e

    def load_cities(self):
        return super(FileLoader, self).load_cities()

    def load_clock(self):
        pass


if __name__ == "__main__":
    # class Student():
    #     def __init__(self, np):
    #         self.np = np
    #
    #     def __getitem__(self, item):
    #         print(item)
    #         return self.np[item]
    #
    # s = Student(numpy.zeros((2, 3, 4)))
    # print(s[0, 0][0])

    fl = FileLoader(0)
    d = fl.load_weapon()
    e = fl.load_operator()
    print(d)
    print(e)
    print('done')