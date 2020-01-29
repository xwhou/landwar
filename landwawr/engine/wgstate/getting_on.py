#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-8 下午3:26
# @Author  : sgr
# @Site    : 
# @File    : getting_on.py

from common.m_exception import print_exception
from wgmessage.action_result import ActionResult
from wgconst.const import ActionStatus
from wgstate.state import State
from wgconst.const import StateType
from wgconst.const import TimeParameter


max_get_on_dis = 1


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
        flag, code = bop.can_get_on()
        if not flag:
            action_msg.set_result(code)
            return False
        car_id = action_msg.get_car_id()
        car_op = operator_sets.get_bop_by_id(car_id)
        if not car_op:
            action_msg.set_result(ActionResult.CantFindOperator)
            return False

        flag, code = _check_get_on_paras(bop, car_op, state_data)
        if not flag:
            action_msg.set_result(code)
            return False

        return True
    except Exception as e:
        print_exception(e)
        raise e


def _check_get_on_paras(passenger, car, state_data):
    try:
        terrain = state_data.get_terrain()
        operator_sets = state_data.get_operator_sets()
        if not passenger.get_color() == car.get_color():
            return False, ActionResult.CantGetOnCauseDiffColor
        flag, code = car.can_do_on_and_off_action()
        if not flag:
            return False, code
        dis = terrain.get_dis_between_hex(passenger.get_hex_pos(), car.get_hex_pos())
        if dis > max_get_on_dis:
            return False, ActionResult.CantGetOnCauseTooFar
        if passenger.get_bop_sub_type() not in car.get_valid_passenger_types():
            return False, ActionResult.CantGetOnCauseWrongObjectType
        if car.is_kept():
            return False, ActionResult.CantGetOnCauseCarKept

        max_passenger_num = car.get_max_passenger_nums(passenger.get_bop_sub_type())
        passenger_ids = car.get_passenger_ids()
        getting_on_ids = car.get_getting_on_partner_id()
        passenger_num = operator_sets.count_spec_type_nums(op_ids=passenger_ids + getting_on_ids,
                                                           op_type=passenger.get_bop_sub_type())
        if passenger_num >= max_passenger_num:
            return False, ActionResult.CantGetOnCauseMaxNum
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
        passenger = operator_sets.get_bop_by_id(op_id=op_id)
        car_id = action_msg.get_car_id()
        car = operator_sets.get_bop_by_id(car_id)
        if not passenger or not car:
            action_msg.set_result(ActionResult.CantFindOperator)
            return ActionStatus.Done
        valid_states = state_manager.get_valid_state_type_by_bop(obj_id=op_id)
        # if StateType.Move in valid_states:
        #     state_manager.stop_state(obj_id=op_id, state_type=StateType.Move)
        assert StateType.GetOn not in valid_states, "Getting on wants to execute get on action!"

        state_manager.start_state(obj_id=op_id, state_type=StateType.GetOn, action_msg=action_msg)
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
        flag, code = bop.can_get_on()
        if not flag:
            return False, code
        my_bops = operator_sets.get_bops_by_condition(pos=bop.get_hex_pos(), color=bop.get_color())
        paras = []
        for car in my_bops:
            flag, result = _check_get_on_paras(passenger=bop, car=car, state_data=state_data)
            if flag:
                paras.append({"target_obj_id": car.obj_id})
        if paras:
            return True, paras
        else:
            return False, None
    except Exception as e:
        print_exception(e)
        raise e


def get_on_end_operation(passenger, car):
    try:
        passenger.on_board = 1
        passenger.launcher = None
        passenger.car = car.obj_id
        car.passenger_ids.append(passenger.obj_id)
        if passenger.obj_id in car.launch_ids:
            car.launch_ids.remove(passenger.obj_id)
    except Exception as e:
        print_exception(e)
        raise e


class GettingOn(State):
    """
    上车状态
    """
    need_time = TimeParameter.GettingOnTime

    def __init__(self, bop, state_data, action_msg_sets):
        """
        need_time   # 上车需要时间
        remain_time # 剩余时间
        car_id  # 车算子ID
        """
        super(GettingOn, self).__init__(bop=bop, state_data=state_data, action_msg_sets=action_msg_sets)
        self.type = StateType.GetOn
        try:
            self.clock = self.state_data.get_clock()
            self.operator_sets = self.state_data.get_operator_sets()

            self.car = None
        except Exception as e:
            print_exception(e)
            raise e

    def enter(self, action_msg):
        """
        :param action_msg:
        :return:
        """
        try:
            self.action_msg = action_msg
            self.bop.get_on_remain_time = self.need_time
            car_id = self.action_msg.get_car_id()
            self.car = self.operator_sets.get_bop_by_id(op_id=car_id)
            if self.car is not None:
                self.bop.get_on_partner_id = [car_id]
                self.car.get_on_partner_id.append(self.bop.get_bop_id())
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
            self.bop.get_on_remain_time -= tick
            if self.bop.get_on_remain_time <= 0:
                self._end(state_manager)
        except Exception as e:
            print_exception(e)
            raise e

    def stop(self, state_manager):
        try:
            self.bop.get_on_remain_time = 0
            self.bop.get_on_partner_id = []

            if self.car is not None:
                self.car.get_on_partner_id.remove(self.bop.obj_id)

            if self.action_msg is not None:
                assert self.action_msg_sets is not None, 'State {} need action_msg_sets'.format(self.__class__.__name__)
                self.action_msg_sets.set_action_status(action_id=self.action_msg.get_msg_id(), status=ActionStatus.Done)

            super(GettingOn, self).stop(state_manager)
        except Exception as e:
            print_exception(e)
            raise e

    def _end(self, state_manager):
        try:
            get_on_end_operation(self.bop, self.car)
            state_manager.stop_state(obj_id=self.bop.obj_id, state_type=self.type)
        except Exception as e:
            print_exception(e)
            raise e