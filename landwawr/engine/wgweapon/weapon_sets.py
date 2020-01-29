#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-12 下午3:55
# @Author  : sgr
# @Site    : 
# @File    : weapon_sets.py

import random

from common.m_exception import print_exception
from wgweapon.jm_weapon import JMWeapon
from wgweapon.zm_weapon import ZMWeapon
from wgmessage.action_result import ActionResult
from wgconst.const import OperatorType
from wgconst.const import InvalidDamage
from wgconst.const import HexType
from wgconst.const import JMAlignStatus


class WeaponSets:
    """
    武器集合类
    """

    def __init__(self, loader, terrain):
        self.loader = loader
        self.terrain = terrain
        self.dic_zm_weapon = {}  # {wp_id: ZMWeapon}
        self.dic_jm_weapon = {}  # {wp_id: JMWeapon}

        self.df_wp_data = None
        self.np_wp2peo_judge_0 = None
        self.np_wp2peo_judge_1 = None
        self.np_wp2car_judge_0 = None
        self.np_wp2car_judge_1 = None
        self.np_wp2car_judge_2 = None
        self.np_wp2air_judge = None
        self.np_jm_offset_0 = None
        self.np_jm_offset_1 = None
        self.np_jm_offset_2 = None
        self.np_ele_rect_to_peo = None
        self.np_ele_rect_to_car = None
        try:
            self.load()
        except Exception as e:
            print_exception(e)
            raise e

    def load(self):
        try:
            dic_result = self.loader.load_weapon()
            df_wp_data = dic_result['df_wp_data']
            self.np_wp2peo_judge_0 = dic_result['np_wp2peo_judge_0']
            self.np_wp2peo_judge_1 = dic_result['np_wp2peo_judge_1']
            self.np_wp2car_judge_0 = dic_result['np_zm2car_judge_0']
            self.np_wp2car_judge_1 = dic_result['np_zm2car_judge_1']
            self.np_wp2car_judge_2 = dic_result['np_zm2car_judge_2']
            self.np_wp2air_judge = dic_result['np_wp2air_judge']
            self.np_jm_offset_0 = dic_result['np_jm_offset_0']
            self.np_jm_offset_1 = dic_result['np_jm_offset_1']
            self.np_jm_offset_2 = dic_result['np_jm_offset_2']
            self.np_ele_rect_to_peo = dic_result['np_ele_rect_to_peo']
            self.np_ele_rect_to_car = dic_result['np_ele_rect_to_car']

            self._init_weapon_data(df_wp_data)
        except Exception as e:
            print_exception(e)
            raise e

    def _init_weapon_data(self, df_wp_data):
        try:
            wp_ids = df_wp_data['WeaponID'].drop_duplicates()
            for idx in wp_ids.index:
                id_i = wp_ids[idx]
                df_i = df_wp_data.query("WeaponID=={}".format(id_i))
                if df_i['F2'].iloc[0] == 0:
                    self.dic_zm_weapon[id_i] = ZMWeapon(df_i)
                elif df_i['F2'].iloc[0] == 1:
                    self.dic_jm_weapon[id_i] = JMWeapon(df_i)
        except Exception as e:
            print_exception(e)
            raise e

    def is_zm_weapon(self, wp_id):
        return wp_id in self.dic_zm_weapon.keys()

    def is_jm_weapon(self, wp_id):
        return wp_id in self.dic_jm_weapon.keys()

    def is_missle(self, wp_id):
        if wp_id in self.dic_zm_weapon.keys():
            return self.dic_zm_weapon[wp_id].is_missile()
        elif wp_id in self.dic_jm_weapon.keys():
            return self.dic_zm_weapon[wp_id].is_missle()
        return False

    def can_weapon_be_guided(self, wp_id):
        if wp_id not in self.dic_zm_weapon.keys():
            return False
        if not self.dic_zm_weapon[wp_id].can_be_guided():
            return False
        return True

    def get_wp_att_types(self, wp_id):
        if wp_id in self.dic_zm_weapon.keys():
            return self.dic_zm_weapon[wp_id].get_att_obj_types()
        return []

    def get_weapon_att_range(self, wp_id, tar_type):
        if wp_id in self.dic_zm_weapon.keys():
            return self.dic_zm_weapon[wp_id].get_att_range(tar_type)
        return [-1, -1]

    def get_attack_level(self, bop_attacker, bop_obj, weapon_id):
        """
        获取攻击等级
        :param bop_attacker: 攻击算子 BasicOperator
        :param bop_obj: 被攻击算子 BasicOperator
        :param weapon_id: 武器ID int
        :return:
        """
        try:
            if bop_attacker is None or bop_obj is None or bop_attacker.get_blood() <= 0:
                return InvalidDamage.InvalidAttackLevel, None
            if weapon_id not in self.dic_zm_weapon.keys():
                return InvalidDamage.InvalidAttackLevel, None
            obj_type = bop_obj.get_bop_type()
            att_pos = bop_attacker.get_hex_pos()
            obj_pos = bop_obj.get_hex_pos()
            distance = self.terrain.get_dis_between_hex(att_pos, obj_pos)
            # 获取攻击等级
            attack_level = int(self.dic_zm_weapon[weapon_id].get_zm_attack_level(length=distance,
                                                                           obj_type=obj_type,
                                                                           att_blood=bop_attacker.get_blood()))

            if attack_level <= InvalidDamage.InvalidAttackLevel:
                return InvalidDamage.InvalidAttackLevel, None

            ele_diff = self.terrain.get_height_change_level(att_pos, obj_pos)

            if bop_obj.get_bop_type() in [OperatorType.People, OperatorType.Car]:
                # 人或车要进行高差修正
                attack_level_rect = self._get_attack_level_rect_by_ele(ele_diff, distance, obj_type)
                attack_level += attack_level_rect
                attack_level = max(attack_level, InvalidDamage.InvalidAttackLevel)

            info = {
                "distance": distance,
                "ele_diff": ele_diff,
                "att_obj_blood": bop_attacker.get_blood()
            }
            return attack_level, info
        except Exception as e:
            print_exception(e)
            raise e

    def get_zm_damage(self, bop_attacker, bop_obj, weapon_id):
        """
        计算直瞄战损
        :param bop_attacker:
        :param bop_obj:
        :param weapon_id:
        :return: damage: 最终战果  -1/无效，0-压制，>0血量
                 info:
                 {
                    "att_obj_id": "攻击算子ID, int",
                    "target_obj_id": "目标算子ID int",
                    "guide_obj_id": "引导算子ID int",
                    "distance": "距离",
                    "ele_diff": "高差等级"，
                    "att_obj_blood": "攻击算子血量",
                    "att_level": "攻击等级 int"
                    "wp_id": "武器ID int"
                    'random1': "随机数1 int",
                    'ori_damage': "原始战损",
                    'random2_rect': "随机数2修正值",
                    'random2': "随机数2",
                    'rect_damage': "战损修正值",
                    'damage': "最终战损"
                }
        """
        try:
            if bop_attacker is None or bop_obj is None or bop_attacker.get_blood() <= 0:
                return InvalidDamage.InvalidDamageValue, {}
            if weapon_id not in self.dic_zm_weapon.keys():
                return InvalidDamage.InvalidDamageValue, {}
            attack_level, al_info = self.get_attack_level(bop_attacker, bop_obj, weapon_id)
            if attack_level <= InvalidDamage.InvalidAttackLevel:
                return InvalidDamage.InvalidDamageValue, {}

            if bop_obj.get_bop_type() == OperatorType.People:
                damage, info = self._get_zm_damage_to_peo(bop_attacker, bop_obj, attack_level)
            elif bop_obj.get_bop_type() == OperatorType.Car:
                damage, info = self._get_zm_damage_to_car(bop_attacker, bop_obj, attack_level)
            else:
                damage, info = self._get_zm_damage_to_plane(attack_level)

            if not info:
                info = dict()
            info['att_level'] = attack_level
            info['wp_id'] = weapon_id
            info["att_obj_id"] = bop_attacker.get_bop_id()
            info["target_obj_id"] = bop_obj.get_bop_id()
            info.update(al_info)
            return damage, info
        except Exception as e:
            print_exception(e)
            raise e

    def get_jm_damage(self, attacker_blood, bop_obj, weapon_id, offset):
        """
        计算间瞄战损
        :param attacker_blood:
        :param bop_obj:
        :param weapon_id:
        :param offset:
        :return:
        """
        try:
            if bop_obj is None or attacker_blood <= 0:
                return InvalidDamage.InvalidDamageValue, {}
            # if weapon_id not in self.dic_jm_weapon.keys() or not self.dic_jm_weapon[weapon_id].i:
            if weapon_id not in self.dic_jm_weapon.keys():
                return InvalidDamage.InvalidDamageValue, {}
            if bop_obj.get_bop_type() not in self.dic_jm_weapon[weapon_id].get_att_obj_types():
                return InvalidDamage.InvalidDamageValue, {}
            random1 = random.randint(1, 6) + random.randint(1, 6)
            damage = self.dic_jm_weapon[weapon_id].get_jm_attack_level(random=random1, off_set=offset)
            random_rect = self._get_jm_random_rect(attacker_blood=attacker_blood, bop_obj=bop_obj)

            ori_random2 = random.randint(1, 6)
            random2 = ori_random2 + random_rect

            final_rect = [-2, -1, 0, 1]
            final_fun = [lambda r: r <= 1, lambda r: 2 <= r <= 4, lambda r: 5 <= r <= 7, lambda r: 8 <= r]
            damage_rect = 0
            for i in range(len(final_rect)):
                if final_fun[i](random2):
                    damage_rect = final_rect[i]
            last_damage = damage + damage_rect
            last_damage = max(InvalidDamage.InvalidDamageValue, last_damage)
            # last_damage = min(last_damage, bop_obj.get_blood())

            info = {
                "att_obj_blood": attacker_blood,
                "target_obj_id": bop_obj.get_bop_id(),
                'random1': random1,
                'offset': offset,
                'wp_id': weapon_id,
                'ori_damage': damage,
                'random2': ori_random2,
                'random2_rect': random_rect,
                "rect_damage": damage_rect,
                'damage': last_damage
            }
            return last_damage, info
        except Exception as e:
            print_exception(e)
            raise e

    def get_jm_offset(self, distance, align_status):
        """
        获取间瞄偏移状态
        :param distance:
        :param align_status:
        :return:
        """
        try:
            assert align_status in [JMAlignStatus.NoAlign, JMAlignStatus.HexAlign, JMAlignStatus.TargetAlign]
            col = self._get_jm_distance_to_offset_col(distance)
            dic_s = {
                JMAlignStatus.NoAlign: self.np_jm_offset_0,
                JMAlignStatus.HexAlign: self.np_jm_offset_1,
                JMAlignStatus.TargetAlign: self.np_jm_offset_2
            }
            random_offset = random.randint(1, 6) + random.randint(1, 6)
            if align_status in [JMAlignStatus.NoAlign, JMAlignStatus.HexAlign]:
                return dic_s[align_status][random_offset - 2][col], random_offset
            else:
                return dic_s[align_status][random_offset - 2], random_offset
        except Exception as e:
            print_exception(e)
            raise e

    def _get_attack_level_rect_by_ele(self, ele_diff, distance, obj_type):
        try:
            if obj_type not in [OperatorType.People, OperatorType.Car]:
                return 0

            if ele_diff <= 0 or distance <= 0:
                return 0

            np_ele_rect = self.np_ele_rect_to_peo if OperatorType.People else self.np_ele_rect_to_car
            row_index = min(np_ele_rect.shape[0] - 1, ele_diff - 1)
            col_index = min(np_ele_rect.shape[1] - 1, distance - 1)

            return int(np_ele_rect[row_index, col_index])
        except Exception as e:
            print_exception(e)
            raise e

    def _get_zm_damage_to_plane(self, attack_level):
        """

        :param attack_level:
        :return:
        """
        try:
            if attack_level <= 0:
                return InvalidDamage.InvalidDamageValue, {}
            random1 = random.randint(1, 6) + random.randint(1, 6)
            damage = self.np_wp2air_judge[int(random1) - 2][attack_level - 1]
            info = {
                'random1': random1,
                'damage': damage
            }
            return damage, info
        except Exception as e:
            print_exception(e)
            raise e

    def _get_zm_damage_to_car(self, bop_attacker, bop_obj, attack_level):
        try:
            if bop_attacker is None or bop_obj is None or bop_attacker.get_blood() <= 0:
                return InvalidDamage.InvalidDamageValue, {}
            if attack_level <= 0:
                return InvalidDamage.InvalidDamageValue, {}
            col_index = self.np_wp2car_judge_0[int(bop_attacker.get_blood() - 1)][attack_level - 1]
            random1 = random.randint(1,6) + random.randint(1, 6)
            ori_damage = self.np_wp2car_judge_1[random1 - 2][col_index-1]
            random2_rect = self._get_zm_random_rect(bop_attacker, bop_obj)
            ori_random2 = random.randint(1, 6) + random.randint(1, 6)
            random2 = ori_random2 + random2_rect
            random2 = min(12, random2)
            random2 = max(-3, random2)
            damage_rect = self.np_wp2car_judge_2[random2 + 3][int(bop_obj.get_armor())]
            last_damage = ori_damage + damage_rect
            last_damage = max(InvalidDamage.InvalidDamageValue, last_damage)
            # last_damage = min(last_damage, bop_obj.get_blood())
            info = {
                'random1': random1,
                'ori_damage': ori_damage,
                'random2_rect': random2_rect,
                'random2': ori_random2,
                'rect_damage': damage_rect,
                'damage': last_damage
            }
            return last_damage, info

        except Exception as e:
            print_exception(e)
            raise e

    def _get_zm_damage_to_peo(self, bop_attacker, bop_obj, attack_level):
        try:
            if bop_attacker is None or bop_obj is None or bop_attacker.get_blood() <= 0:
                return InvalidDamage.InvalidDamageValue, {}
            if attack_level <= 0:
                return InvalidDamage.InvalidDamageValue, {}
            random1 = random.randint(1, 6) + random.randint(1, 6)
            ori_damage = self.np_wp2peo_judge_0[random1-2][attack_level-1]
            ori_random2 = random.randint(1, 6)
            random2_rect = self._get_zm_random_rect(bop_attacker, bop_obj)
            random2 = ori_random2 + random2_rect
            random2 = min(8, random2)
            random2 = max(0, random2)
            damage_rect = self.np_wp2peo_judge_1[random2][1]
            last_damage = damage_rect + ori_damage
            last_damage = max(InvalidDamage.InvalidDamageValue, last_damage)
            # last_damage = min(last_damage, bop_obj.get_blood())
            info = {
                    'random1': random1,
                    'ori_damage': ori_damage,
                    'random2': ori_random2,
                    'random2_rect': random2_rect,
                    'rect_damage': damage_rect,
                    'damage': last_damage}
            return last_damage, info
        except Exception as e:
            print_exception(e)
            raise e

    def _get_zm_random_rect(self, bop_attacker, bop_obj):
        try:
            rect = 0
            if bop_attacker.is_kept():
                rect -= 1
            if bop_attacker.is_moving():
                rect -= 1
            if bop_obj.is_hiding():
                rect -= 2
            if bop_obj.is_moving():
                rect -= 2
            if bop_obj.is_marching():
                rect += 4
            if bop_obj.is_stack():
                rect += 2

            hex_type = self.terrain.get_grid_type(bop_obj.get_hex_pos())
            if hex_type == HexType.Village:
                rect -= 1
            if hex_type == HexType.Forest:
                rect -= 2
            if hex_type == HexType.Water:
                rect -= 2

            return rect

        except Exception as e:
            print_exception(e)
            raise e

    def _get_jm_random_rect(self, attacker_blood, bop_obj):
        try:
            rect = 0
            if bop_obj.is_hiding():
                rect -= 2
            if bop_obj.is_moving():
                rect += 2
            if bop_obj.is_marching():
                rect += 4
            if bop_obj.is_stack():
                rect += 2

            hex_type = self.terrain.get_grid_type(bop_obj.get_hex_pos())
            if hex_type == HexType.Village:
                rect -= 1
            if hex_type == HexType.Forest:
                rect -= 2

            blood_to_rect = {
                1: -4,
                2: -2,
                3: 0,
                4: 2
            }
            if attacker_blood in blood_to_rect.keys():
                rect += blood_to_rect[attacker_blood]

            armor_to_rect = {
                4: -3,
                3: -1,
                2: 0,
                1: 1
            }
            armor = bop_obj.get_armor()
            if armor in armor_to_rect.keys():
                rect += armor_to_rect[armor]

            return rect
        except Exception as e:
            print_exception(e)
            raise e

    def _get_jm_distance_to_offset_col(self, dis):
        '''
            根据距离映射到裁决表中的列
            TODO : 这个映射关系应该也是可以加载的,这里写的有些死
        :param dis: 距离
        :return: 列ss
        '''
        return max(min(dis//20, 3), 0)


if __name__ == "__main__":
    from wgloader.file_loader import FileLoader
    fl = FileLoader(0)
    ws = WeaponSets(loader=fl, terrain=None)
    # ws.np_wp2air_judge.np[ws.np_wp2air_judge.np == 0] = -1
    # import numpy
    # numpy.savetxt("a.txt", ws.np_wp2air_judge.np, fmt="%i")
    print('done')
