#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-29 上午9:15
# @Author  : sgr
# @Site    : 
# @File    : occupy.py

from common.m_exception import print_exception
from wgmessage.action_result import ActionResult
from wgconst.const import ActionStatus
from wgconst.const import OperatorType


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
        flag, code = bop.can_occupy()
        if not flag:
            action_msg.set_result(code)
            return False

        flag, code = _check_occupy_paras(bop, state_data)
        if not flag:
            action_msg.set_result(code)
            return False

        return True
    except Exception as e:
        print_exception(e)
        raise e


def _check_occupy_paras(bop, state_data):
    try:
        terrain = state_data.get_terrain()
        cities = state_data.get_cities()
        operator_sets = state_data.get_operator_sets()

        city = cities.get_city_by_coord(coord=bop.get_hex_pos())
        if not city:
            return False, ActionResult.CantOccupyCauseNotInCity
        if cities.get_city_color(city) == bop.color:
            return False, ActionResult.CantOccupyCauseAlreadyMy

        neighbors = terrain.get_neighbors(city['coord'])
        neighbors = neighbors + [city['coord']]
        enemy_bops = operator_sets.get_valid_enemy_bops_by_color(color=bop.color)
        flag = True
        for bop in enemy_bops:
            if bop.get_hex_pos() in neighbors and bop.get_bop_type() != OperatorType.Plane:
                flag = False
                break
        if not flag:
            return False, ActionResult.CantOccupyCauseEnemyDefending
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
        cities = state_data.get_cities()
        op_id = action_msg.get_op_id()
        bop = operator_sets.get_bop_by_id(op_id=op_id)
        if not bop:
            action_msg.set_result(ActionResult.CantFindOperator)  # 算子不存在
            return ActionStatus.Done
        city = cities.get_city_by_coord(coord=bop.get_hex_pos())
        if not city:
            return ActionStatus.Done, ActionResult.CantOccupyCauseNotInCity
        cities.set_city_flag(coord=city['coord'], flag=bop.color)

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
        flag, code = bop.can_occupy()
        if not flag:
            return False, code
        flag, code = _check_occupy_paras(bop, state_data)
        if not flag:
            return False, code
        return True, None
    except Exception as e:
        print_exception(e)
        raise e