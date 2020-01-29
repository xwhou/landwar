#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-8 下午3:24
# @Author  : sgr
# @Site    : 
# @File    : switching_state.py


from common.m_exception import print_exception
from wgmessage.action_result import ActionResult
from wgconst.const import ActionStatus
from wgconst.const import MoveState
from wgconst.const import OperatorType
from wgconst.const import StateType
from wgstate.state import State
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
        flag, code = bop.can_switch_state()
        if not flag:
            action_msg.set_result(code)
            return False
        target_state = action_msg.get_target_state()
        flag, code = _check_change_state_paras(bop=bop, target_state=target_state, state_data=state_data)
        if not flag:
            action_msg.set_result(code)
            return False
        return True
    except Exception as e:
        print_exception(e)
        raise e


def _check_change_state_paras(bop, target_state, state_data):
    try:
        cur_state = bop.get_move_state()
        if cur_state == target_state:
            return False, ActionResult.CantChangeStateCauseNotChange
        if target_state in [MoveState.Charge_1, MoveState.Charge_2]:
            if bop.get_bop_type() != OperatorType.People:
                return False, ActionResult.CantChangeStateCauseOnlyPeoCanCharge
            if target_state == MoveState.Charge_1:
                if bop.tire >= 2:
                    return False, ActionResult.CantCharge1UnderTireLv2
            elif target_state == MoveState.Charge_2:
                if bop.tire >= 1:
                    return False, ActionResult.CantCharge2UnderTireLv1
        elif target_state == MoveState.March:
            if bop.get_bop_type() != OperatorType.Car:
                return False, ActionResult.CantMarchNotCar
            terrain = state_data.get_terrain()
            if not terrain.has_road(bop.get_hex_pos()):
                return False, ActionResult.CantMarchOnNotRoad
        elif target_state == MoveState.Hide:
            if bop.get_bop_type() == OperatorType.Plane:
                return False, ActionResult.CantHideForPlane
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
        obj_id = action_msg.get_op_id()
        bop = operator_sets.get_bop_by_id(op_id=obj_id)
        if not bop:
            action_msg.set_result(ActionResult.CantFindOperator)  # 算子不存在
            return ActionStatus.Done
        target_state = action_msg.get_target_state()
        # cur_state = bop.move_state
        # valid_states = state_manager.get_valid_state_type_by_bop(obj_id=obj_id)

        if target_state in [MoveState.Charge_2, MoveState.Charge_1]:
            bop.move_state = target_state
        elif target_state == MoveState.NormalMove:
            if bop.move_state == MoveState.March:
                state_manager.start_state(obj_id=obj_id, state_type=StateType.ChangeState, action_msg=action_msg)
            else:
                bop.move_state = target_state
        elif target_state in [MoveState.Hide, MoveState.March]:
            state_manager.start_state(obj_id=obj_id, state_type=StateType.ChangeState, action_msg=action_msg)

        # if cur_state == MoveState.March:
        #     if StateType.WeaponUnFold in valid_states:
        #         state_manager.refresh_state(obj_id=obj_id, state_type=StateType.WeaponUnFold, action_msg=None)
        #     else:
        #         state_manager.start_state(obj_id=obj_id, state_type=StateType.WeaponUnFold, action_msg=None)

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
    try:
        operator_sets = state_data.get_operator_sets()
        bop = operator_sets.get_bop_by_id(op_id=obj_id)
        if not bop:
            return False, ActionResult.CantFindOperator
        flag, code = bop.can_switch_state()
        if not flag:
            return False, code

        paras = []
        for state in MoveState.all_states:
            flag, result = _check_change_state_paras(bop, target_state=state, state_data=state_data)
            if flag:
                paras.append({"target_state": state})

        if paras:
            return True, paras
        else:
            return False, None
    except Exception as e:
        print_exception(e)
        raise e


class SwitchingState(State):
    """
    切换状态
    """
    need_time = TimeParameter.SwitchStateTime

    def __init__(self, bop, state_data, action_msg_sets):
        """
        cur_state   # 当前状态
        target_state    # 目标状态
        remain_time # 剩余时间
        cost_time   # 需要耗费时间
        """
        try:
            super(SwitchingState, self).__init__(bop=bop, state_data=state_data, action_msg_sets=action_msg_sets)
            self.type = StateType.ChangeState

            self.clock = self.state_data.get_clock()
            self.terrain = self.state_data.get_terrain()

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
            target_state = action_msg.get_target_state()
            self.bop.target_state = target_state
            if target_state in self.need_time.keys():
                self.bop.change_state_remain_time = self.need_time[target_state]
            else:
                self.bop.change_state_remain_time = 0
        except Exception as e:
            print_exception(e)
            raise e

    def refresh(self, action_msg):
        """

        :param action_msg:
        :return:
        """
        try:
            self.enter(action_msg)
        except Exception as e:
            print_exception(e)
            raise e

    def update(self, state_manager):
        """

        :param state_manager:
        :return:
        """
        try:
            self.bop.change_state_remain_time -= self.clock.get_tick()
            if self.bop.change_state_remain_time <= 0:
                self.bop.move_state = self.bop.target_state
                self._end(state_manager=state_manager)
        except Exception as e:
            print_exception(e)
            raise e

    def stop(self, state_manager):
        """

        :return:
        """
        try:
            self.bop.change_state_remain_time = 0
            self.bop.target_state = None
            if self.action_msg is not None:
                assert self.action_msg_sets is not None, 'State {} need action_msg_sets'.format(self.__class__.__name__)
                self.action_msg_sets.set_action_status(action_id=self.action_msg.get_msg_id(), status=ActionStatus.Done)
            super(SwitchingState, self).stop(state_manager)
        except Exception as e:
            print_exception(e)
            raise e

    def _end(self, state_manager):
        try:
            state_manager.stop_state(obj_id=self.bop.obj_id, state_type=self.type)
            if self.bop.move_state == MoveState.NormalMove:     # 转为机动，此处只可能是由行军状态转换而来,开始武器展开
                valid_states = state_manager.get_valid_state_type_by_bop(self.bop.obj_id)
                assert StateType.WeaponUnFold not in valid_states, "WeaponUnfold already in March to NormalMove State"
                state_manager.start_state(obj_id=self.bop.obj_id, state_type=StateType.WeaponUnFold, action_msg=None)
        except Exception as e:
            print_exception(e)
            raise e

