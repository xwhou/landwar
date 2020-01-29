#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-29 上午9:15
# @Author  : sgr
# @Site    : 
# @File    : remove_keep.py


from common.m_exception import print_exception
from wgmessage.action_result import ActionResult
from wgconst.const import ActionStatus
from wgconst.const import StateType


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
        move_flag, code = bop.can_remove_keep()
        if not move_flag:
            action_msg.set_result(code)
            return False
        return True
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
        bop = operator_sets.get_bop_by_id(op_id=op_id)
        if not bop:
            action_msg.set_result(ActionResult.CantFindOperator)  # 算子不存在
            return ActionStatus.Done
        bop.keep = 0
        assert bop.blood > 1
        bop.blood -= 1
        valid_state_types = state_manager.get_valid_state_type_by_bop(op_id)
        if StateType.RestoreKeep in valid_state_types:
            state_manager.stop_state(op_id, StateType.RestoreKeep)
        return ActionStatus.Done
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
        flag, code = bop.can_remove_keep()
        if not flag:
            return False, code
        return True, None
    except Exception as e:
        print_exception(e)
        raise e