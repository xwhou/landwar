#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-29 上午9:16
# @Author  : sgr
# @Site    : 
# @File    : restore_tire.py


from common.m_exception import print_exception
from wgstate.state import State
from wgconst.const import StateType
from wgconst.const import TimeParameter


class RestoringTire(State):
    """
    状态类（抽象类）
    """
    need_time = TimeParameter.RestoreTireTime

    def __init__(self, bop, state_data, action_msg_sets):
        """

        :param bop:
        :param state_data:
        :param action_msg_sets:
        """
        super(RestoringTire, self).__init__(bop=bop, state_data=state_data, action_msg_sets=action_msg_sets)
        self.type = StateType.RestoreTire
        try:
            self.clock = self.state_data.get_clock()
        except Exception as e:
            print_exception(e)
            raise e

    def enter(self, action_msg):
        try:
            if self.bop.tire in self.need_time.keys():
                self.bop.tire_accumulate_time = self.need_time[self.bop.tire]
            else:
                self.bop.tire_accumulate_time = 0
        except Exception as e:
            print_exception(e)
            raise e

    def refresh(self, action_msg):
        try:
            self.enter(action_msg)
        except Exception as e:
            print_exception(e)
            raise e

    def update(self, state_manager):
        try:
            self.bop.tire_accumulate_time -= self.clock.get_tick()
            if self.bop.tire_accumulate_time <= 0:
                self.bop.tire = max(0, self.bop.tire - 1)
                if self.bop.tire in self.need_time.keys():
                    self.bop.tire_accumulate_time = self.need_time[self.bop.tire]
                else:
                    self._end(state_manager)

        except Exception as e:
            print_exception(e)
            raise e

    def stop(self, state_manager):
        """Todo 中断疲劳恢复与结束疲劳恢复应该不同"""
        try:
            self.bop.tire_accumulate_time = 0
            super(RestoringTire, self).stop(state_manager)
        except Exception as e:
            print_exception(e)
            raise e

    def _end(self, state_manager):
        try:
            state_manager.stop_state(obj_id=self.bop.obj_id, state_type=self.type)
        except Exception as e:
            print_exception(e)
            raise e