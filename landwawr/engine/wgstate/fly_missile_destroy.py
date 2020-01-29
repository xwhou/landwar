#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-12-18 下午4:44
# @Author  : sgr
# @Site    : 
# @File    : fly_missile_destroy.py


from common.m_exception import print_exception
from wgstate.state import State
from wgconst.const import StateType
from wgconst.const import TimeParameter


class FlyMissileDestroy(State):
    """
    状态类（抽象类）
    """
    max_time = TimeParameter.FlyMissileAliveTime

    def __init__(self, bop, state_data, action_msg_sets):
        """

        :param bop:
        :param state_data:
        :param action_msg_sets:
        """
        super(FlyMissileDestroy, self).__init__(bop=bop, state_data=state_data, action_msg_sets=action_msg_sets)
        self.type = StateType.FlyMissileDestroy
        try:
            self.clock = self.state_data.get_clock()
            self.operator_sets = self.state_data.get_operator_sets()
        except Exception as e:
            print_exception(e)
            raise e

    def enter(self, action_msg):
        try:
            self.bop.alive_remain_time = self.max_time
        except Exception as e:
            print_exception(e)
            raise e

    def refresh(self, action_msg):
        self.enter(action_msg)

    def update(self, state_manager):
        try:
            self.bop.alive_remain_time -= self.clock.get_tick()
            if self.bop.alive_remain_time <= 0:
                self._end(state_manager)
        except Exception as e:
            print_exception(e)
            raise e

    def stop(self, state_manager):
        try:
            super(FlyMissileDestroy, self).stop(state_manager)
            self.__del__()
        except Exception as e:
            print_exception(e)
            raise e

    def _end(self, state_manager):
        try:
            self.bop.obj_blood = 0
            died_bop_ids = self.operator_sets.on_bop_died(self.bop)
            for o_id in died_bop_ids:
                state_manager.stop_all_valid_states(obj_id=o_id)
        except Exception as e:
            print_exception(e)
            raise e

    def __del__(self):
        super(FlyMissileDestroy, self).__del__()
        self.clock = None
        self.operator_sets = None