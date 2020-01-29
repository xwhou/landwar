#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-8 下午3:13
# @Author  : sgr
# @Site    : 
# @File    : state.py


from common.m_exception import print_exception
from wgmessage.action_result import ActionResult
from wgconst.const import ActionStatus


def _check(action_msg, state_data):
    """
    动作合法性检查
    :param action_msg:
    :param state_data:
    :return:
    """
    try:
        return True
    except Exception as e:
        print_exception(e)
        raise e


def _check_shoot_paras(attack_bop, target_bop, weapon_id, state_data):
    try:
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


class State:
    """
    状态类（抽象类）
    """
    def __init__(self, bop, state_data, action_msg_sets):
        """

        :param bop:
        :param state_data:
        :param action_msg_sets:
        """
        self.bop = bop
        self.state_data = state_data
        self.action_msg_sets = action_msg_sets
        self.type = None
        self.action_msg = None
        self.done = False

    def enter(self, action_msg):
        pass

    def refresh(self, action_msg):
        pass

    def update(self, state_manager):
        pass

    def stop(self, state_manager):
        self.done = True

    def get_state_type(self):
        pass

    def is_finished(self):
        return self.done

    def __del__(self):
        self.bop = None
        self.state_data = None
        self.action_msg_sets = None
        self.type = None
        self.action_msg = None


