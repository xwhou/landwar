#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-28 上午8:43
# @Author  : sgr
# @Site    : 
# @File    : jm_plan.py


from common.m_exception import print_exception
from wgconst.const import StateType
from wgconst.const import ActionStatus
from wgmessage.action_result import ActionResult
from wgstate.shooting import _execute_shoot


def _check(action_msg, state_data):
    """
    动作合法性检查
    :param action_msg:
    :param state_data:
    :return:
    """
    try:
        assert action_msg.get_action_type() == StateType.JMPlan, \
            'State={} receive error action msg type = {}'.format(StateType.GuideShoot, action_msg.get_action_type())
        operator_sets = state_data.get_operator_sets()
        op_id = action_msg.get_op_id()
        bop = operator_sets.get_bop_by_id(op_id=op_id)
        if not bop:
            action_msg.set_result(ActionResult.CantFindOperator)
            return False
        flag, code = bop.can_jm_plan()
        if not flag:
            action_msg.set_result(code)
            return flag

        weapon_id = action_msg.get_weapon_id()
        target_pos = action_msg.get_jm_pos()

        flag, code = _check_jm_plan_paras(attack_bop=bop, weapon_id=weapon_id, jm_pos=target_pos, state_data=state_data)
        if not flag:
            action_msg.set_result(code)
            return False

        return True
    except Exception as e:
        print_exception(e)
        raise e


def _check_jm_plan_paras(attack_bop, weapon_id, jm_pos, state_data):
    try:
        if weapon_id not in attack_bop.get_carry_weapons():
            return False, ActionResult.CantFindWeapon
        weapon_sets = state_data.get_weapon()
        if not weapon_sets.is_jm_weapon(weapon_id):
            return False, ActionResult.CantJMCauseWrongWeapon
        terrain = state_data.get_terrain()
        if not terrain.is_pos_valid(jm_pos):
            return False, ActionResult.CantJMOutOfMap
        return True, ActionResult.Success
    except Exception as e:
        print_exception(e)
        raise e


def _execute(action_msg, state_manager, state_data):
    try:
        op_id = action_msg.get_op_id()
        attack_bop = state_data.get_operator_sets().get_bop_by_id(op_id)
        if attack_bop is None:
            return ActionStatus.Done
        weapon_id = action_msg.get_weapon_id()
        target_pos = action_msg.get_jm_pos()
        jm_point_sets = state_data.get_jm_point_sets()
        jm_point_sets.add_jm_point(op_id=op_id, weapon_id=weapon_id, target_pos=target_pos)

        _execute_shoot(attack_bop=attack_bop,
                       state_manager=state_manager)

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
    """

    :param obj_id:
    :param state_data:
    :return: (True, [weapon_id]) or (False, None)
    """
    try:
        operator_sets = state_data.get_operator_sets()
        bop = operator_sets.get_bop_by_id(op_id=obj_id)
        if not bop:
            return False, ActionResult.CantFindOperator
        flag, code = bop.can_jm_plan()
        if not flag:
            return False, code
        l_wps = bop.get_carry_weapons()
        if not l_wps:
            return False, ActionResult.CantFindWeapon
        weapon_sets = state_data.get_weapon()
        paras = []
        for weapon_id in l_wps:
            if weapon_sets.is_jm_weapon(weapon_id):
                paras.append({"weapon_id": weapon_id})
        if paras:
            return True, paras
        else:
            return False, None
    except Exception as e:
        print_exception(e)
        raise e