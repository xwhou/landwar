#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-29 上午9:17
# @Author  : sgr
# @Site    : 
# @File    : weapon_colling.py


from common.m_exception import print_exception
from wgstate.state import State
from wgconst.const import StateType
from wgconst.const import OperatorSubType
from wgconst.const import TimeParameter


class WeaponCooling(State):
    """
    状态类（抽象类）
    """
    need_time = TimeParameter.WeaponCoolTime

    def __init__(self, bop, state_data, action_msg_sets):
        """

        :param bop:
        :param state_data:
        :param action_msg_sets:
        """
        super(WeaponCooling, self).__init__(bop=bop, state_data=state_data, action_msg_sets=action_msg_sets)
        self.type = StateType.WeaponCool
        try:
            self.clock = self.state_data.get_clock()
        except Exception as e:
            print_exception(e)
            raise e

    def enter(self, action_msg):
        try:
            obj_id = self.bop.get_bop_sub_type()
            if obj_id in self.need_time.keys():
                self.bop.weapon_cool_time = self.need_time[obj_id]
            else:
                self.bop.weapon_cool_time = 0
        except Exception as e:
            print_exception(e)
            raise e

    def refresh(self, action_msg):
        self.enter(action_msg)

    def update(self, state_manager):
        try:
            self.bop.weapon_cool_time -= self.clock.get_tick()
            if self.bop.weapon_cool_time <= 0:
                self._end(state_manager)
        except Exception as e:
            print_exception(e)
            raise e

    def stop(self, state_manager):
        self.bop.weapon_cool_time = 0
        super(WeaponCooling, self).stop(state_manager)

    def _end(self, state_manager):
        try:
            state_manager.stop_state(obj_id=self.bop.obj_id, state_type=self.type)
        except Exception as e:
            print_exception(e)
            raise e