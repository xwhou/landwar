#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-12-16 下午11:35
# @Author  : sgr
# @Site    : 
# @File    : move_to_stop.py


from common.m_exception import print_exception
from wgstate.state import State
from wgconst.const import StateType
from wgconst.const import TimeParameter


class MovingToStop(State):
    """
    状态类（抽象类）
    """
    need_time = TimeParameter.MoveToStopTime

    def __init__(self, bop, state_data, action_msg_sets):
        """

        :param bop:
        :param state_data:
        :param action_msg_sets:
        """
        super(MovingToStop, self).__init__(bop=bop, state_data=state_data, action_msg_sets=action_msg_sets)
        self.type = StateType.MoveToStop
        try:
            self.clock = self.state_data.get_clock()
        except Exception as e:
            print_exception(e)
            raise e

    def enter(self, action_msg):
        try:
            self.bop.move_to_stop_remain_time = self.need_time
        except Exception as e:
            print_exception(e)
            raise e

    def refresh(self, action_msg):
        self.enter(action_msg)

    def update(self, state_manager):
        try:
            self.bop.move_to_stop_remain_time -= self.clock.get_tick()
            if self.bop.move_to_stop_remain_time <= 0:
                self._end(state_manager)
        except Exception as e:
            print_exception(e)
            raise e

    def stop(self, state_manager):
        self.bop.move_to_stop_remain_time = 0
        self.bop.set_stop_status(1)

        bop_id = self.bop.get_bop_id()

        valid_states = state_manager.get_valid_state_type_by_bop(obj_id=bop_id)
        assert StateType.WeaponUnFold not in valid_states, "WeaponUnfold should not appear when MoveToStop!"
        if not self.bop.can_move_shoot():
            state_manager.start_state(obj_id=bop_id, state_type=StateType.WeaponUnFold, action_msg=None)

        super(MovingToStop, self).stop(state_manager)
        self.__del__()

    def _end(self, state_manager):
        try:
            state_manager.stop_state(obj_id=self.bop.obj_id, state_type=self.type)
        except Exception as e:
            print_exception(e)
            raise e

    def __del__(self):
        super(MovingToStop, self).__del__()
        self.clock = None