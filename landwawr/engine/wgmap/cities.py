#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-8 下午2:56
# @Author  : sgr
# @Site    : 
# @File    : cities.py

from common.m_exception import print_exception
from wgconst.const import Color
from wgmap.terrain import cvt_int6_to_int4


class Cities:
    """
    夺控点类
    """
    def __init__(self, loader):
        """
        df_cities   # 夺控点(coord, value, flag, name)
        """
        self.loader = loader
        self.dic_cities = {}    # {coord: {'coord': int, 'value': int, 'flag': int, 'name': str}}

        try:
            self.load()
        except Exception as e:
            print_exception(e)
            raise e

    def load(self):
        """
        加载数据
        :return:
        """
        try:
            data = self.loader.load_cities()
            self.dic_cities = {}
            for _, ser in data.iterrows():
                coord = cvt_int6_to_int4(int(ser['MapID']))
                self.dic_cities[coord] = {
                    'coord': coord,
                    'value': int(ser['C1']),
                    'flag': self._flag_change(ser['UserFlag']),
                    'name': ser['CityName']
                }

        except Exception as e:
            print_exception(e)
            raise e

    def reset(self):
        try:
            self.load()
        except Exception as e:
            print_exception(e)
            raise e

    def load_component(self, city_data):
        """

        :param city_data: list(dict)
        :return:
        """
        try:
            self.dic_cities = {}
            for city in city_data:
                coord = city["coord"]
                self.dic_cities[coord] = city
        except Exception as e:
            print_exception(e)
            raise e

    def _flag_change(self, str_flag):
        """
        将 RED/BLUE/GREEN 映射到 0/1/-1
        :param str_flag:
        :return:
        """
        if str_flag in Color.name_to_color.keys():
            return Color.name_to_color[str_flag]
        return Color.GREEN

    def get_city_by_coord(self, coord):
        try:
            if coord in self.dic_cities.keys():
                return self.dic_cities[coord]
            return None
        except Exception as e:
            print_exception(e)
            raise e

    def get_city_color(self, city):
        return city["flag"]

    def set_city_flag(self, coord, flag):
        """
        设置标志
        :param coord: 坐标
        :param flag: 标志(颜色)
        :return:
        """
        self.dic_cities[coord]['flag'] = flag

    def get_citites_obsevation(self):
        return list(self.dic_cities.values())

    def get_citites_obsevation_notes(self):
        return [
            {
                "coord": "坐标 int",
                "value": "分值 int",
                "flag": "阵营 0-红 1-蓝",
                "name": "名称 str"
            }
        ]

    def get_cities_scores_by_color(self, color):
        try:
            score = 0
            for _, city in self.dic_cities.items():
                if city["flag"] == color:
                    score += city["value"]
            return int(score)
        except Exception as e:
            print_exception(e)
            raise e


if __name__ == "__main__":
    from wgloader.file_loader import FileLoader
    fl = FileLoader(0)

    ci = Cities(fl)
    print(ci.get_city_by_coord(1624))
    print('done')