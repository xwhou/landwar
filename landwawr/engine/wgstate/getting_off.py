#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-8 下午3:28
# @Author  : sgr
# @Site    : 
# @File    : getting_off.py


from common.m_exception import print_exception
from wgmessage.action_result import ActionResult
from wgconst.const import ActionStatus
from wgstate.state import State
from wgconst.const import StateType
from wgconst.const import OperatorSubType
from wgconst.const import TimeParameter


def _check(action_msg, state_data):
    """
    动作合法性检查
    :param action_msg:
    :param state_data:
    :return:
    """
    try:
        operator_sets = state_data.get_operator_sets()
        op_id = action_msg.get_op_id()
        bop = operator_sets.get_bop_by_id(op_id=op_id)
        if not bop:
            action_msg.set_result(ActionResult.CantFindOperator)  # 算子不存在
            return False
        flag, code = bop.can_get_off()
        if not flag:
            action_msg.set_result(code)
            return False
        passenger_id = action_msg.get_passenger_id()
        passenger = operator_sets.get_bop_by_id(passenger_id)
        if not passenger:
            action_msg.set_result(ActionResult.CantFindOperator)
            return False

        flag, code = _check_get_off_paras(bop, passenger, operator_sets)
        if not flag:
            action_msg.set_result(code)
            return False

        return True
    except Exception as e:
        print_exception(e)
        raise e


def _check_get_off_paras(car, passenger, operator_sets):
    try:
        if passenger.get_bop_id() not in car.get_passenger_ids():
            return False, ActionResult.CantGetOffCauseNoPassengers
        if passenger.is_getting_off():
            return False, ActionResult.CantGetOffWhenGettingOff
        if passenger.get_bop_sub_type() == OperatorSubType.FlyMissile:
            launch_ids = car.get_launch_ids()
            getting_off_ids = car.get_getting_off_partner_id()
            if operator_sets.count_spec_type_nums(op_ids=launch_ids + getting_off_ids, op_type=passenger.get_bop_sub_type()) >= 1:
                return False, ActionResult.CantGetOffCauseAlreadyFlyMissile
        return True, ActionResult.Success
    except Exception as e:
        print_exception(e)
        raise e


def _execute(action_msg, state_manager, state_data):
    """
    执行动作
    :param action_msg:
    :param state_manager:
    :param state_data:
    :return:
    """
    try:
        operator_sets = state_data.get_operator_sets()
        op_id = action_msg.get_op_id()
        car = operator_sets.get_bop_by_id(op_id=op_id)
        passenger_id = action_msg.get_passenger_id()
        passenger = operator_sets.get_bop_by_id(passenger_id)
        if not passenger or not car:
            action_msg.set_result(ActionResult.CantFindOperator)
            return ActionStatus.Done

        valid_states = state_manager.get_valid_state_type_by_bop(obj_id=passenger_id)
        # if StateType.Move in valid_states:
        #     state_manager.stop_state(obj_id=op_id, state_type=StateType.Move)
        assert StateType.GetOff not in valid_states, "Getting on wants to execute get on action!"

        state_manager.start_state(obj_id=passenger_id, state_type=StateType.GetOff, action_msg=action_msg)
        return ActionStatus.Doing
    except Exception as e:
        print_exception(e)
        raise e


def handle_action(message, state_manager, state_data):
    """
    处理动作
    :param message:
    :param state_manager:
    :param state_data:
    :return:
    """
    try:
        valid = _check(action_msg=message, state_data=state_data)
        if not valid:
            return ActionStatus.Done
        status = _execute(action_msg=message, state_manager=state_manager, state_data=state_data)
        return status
    except Exception as e:
        print_exception(e)
        raise e


def get_valid_paras(obj_id, state_data):
    """

    :param obj_id:
    :param state_data:
    :return: (True, [target_obj_id]) or (False, None)
    """
    try:
        operator_sets = state_data.get_operator_sets()
        bop = operator_sets.get_bop_by_id(op_id=obj_id)
        if not bop:
            return False, ActionResult.CantFindOperator
        flag, code = bop.can_get_off()
        if not flag:
            return False, code
        my_passengers = operator_sets.get_passengers_by_color(color=bop.color)
        # my_passengers = operator_sets.get_valid_bops_by_color(color=bop.color)
        paras = []
        for passenger in my_passengers:
            flag, result = _check_get_off_paras(passenger=passenger, car=bop, operator_sets=operator_sets)
            if flag:
                paras.append({"target_obj_id": passenger.obj_id})
        if paras:
            return True, paras
        else:
            return False, None
    except Exception as e:
        print_exception(e)
        raise e


class GettingOff(State):
    """
    下车状态
    """
    need_time = TimeParameter.GettingOffTime

    def __init__(self, bop, state_data, action_msg_sets):
        """
        Modify: bop为乘客算子
        """
        super(GettingOff, self).__init__(bop=bop, state_data=state_data, action_msg_sets=action_msg_sets)
        self.type = StateType.GetOff
        try:
            self.clock = self.state_data.get_clock()
            self.operator_sets = self.state_data.get_operator_sets()

            self.car = None
        except Exception as e:
            print_exception(e)
            raise e

    def enter(self, action_msg):
        """
        Todo 多个算子同时下车怎么处理
        :param action_msg:
        :return:
        """
        try:
            self.action_msg = action_msg
            self.bop.get_off_remain_time = self.need_time
            car_id = action_msg.get_op_id()
            self.car = self.operator_sets.get_bop_by_id(car_id)
            assert self.car is not None, "{} cant find car ".format(self.__class__.__name__)
            self.bop.get_off_partner_id = [car_id]
            self.car.get_off_partner_id.append(self.bop.get_bop_id())
        except Exception as e:
            print_exception(e)
            raise e

    def update(self, state_manager):
        """

        :param state_manager:
        :return:
        """
        try:
            tick = self.clock.get_tick()
            self.bop.get_off_remain_time -= tick
            if self.bop.get_off_remain_time <= 0:
                self._end(state_manager)
        except Exception as e:
            print_exception(e)
            raise e

    def stop(self, state_manager):
        try:
            self.bop.get_off_remain_time = 0
            self.bop.get_off_partner_id = []

            if self.car is not None:
                self.car.get_off_partner_id.remove(self.bop.obj_id)

            if self.action_msg is not None:
                assert self.action_msg_sets is not None, 'State {} need action_msg_sets'.format(self.__class__.__name__)
                self.action_msg_sets.set_action_status(action_id=self.action_msg.get_msg_id(), status=ActionStatus.Done)

            super(GettingOff, self).stop(state_manager)
        except Exception as e:
            print_exception(e)
            raise e

    def _end(self, state_manager):
        try:
            self.bop.on_board = 0
            self.bop.launcher = self.car.obj_id
            self.bop.car = None

            self.car.passenger_ids.remove(self.bop.obj_id)
            self.car.launch_ids.append(self.bop.obj_id)

            state_manager.stop_state(obj_id=self.bop.obj_id, state_type=self.type)

            if self.bop.get_bop_sub_type() == OperatorSubType.FlyMissile:
                state_manager.start_state(obj_id=self.bop.obj_id, state_type=StateType.FlyMissileDestroy, action_msg=None)
        except Exception as e:
            print_exception(e)
            raise e