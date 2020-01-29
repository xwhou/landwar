#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-8 下午3:29
# @Author  : sgr
# @Site    : 
# @File    : Shooting.py


from common.m_exception import print_exception
from wgmessage.action_result import ActionResult
from wgconst.const import ActionStatus
from wgconst.const import StateType
from wgconst.const import OperatorSubType
from wgconst.const import OperatorType
from wgmap.terrain import check_bop_see
from wgconst.const import InvalidDamage
from wgconst.const import MoveState


def _check(action_msg, state_data):
    """
    动作合法性检查
    :param action_msg:
    :param state_data:
    :return:
    """
    try:
        assert action_msg.get_action_type() == StateType.Shoot, \
            'State={} receive error action msg type = {}'.format(StateType.Shoot, action_msg.get_action_type())
        operator_sets = state_data.get_operator_sets()
        op_id = action_msg.get_op_id()
        bop = operator_sets.get_bop_by_id(op_id=op_id)
        if not bop:
            action_msg.set_result(ActionResult.CantFindOperator)  # 算子不存在
            return False
        flag_shoot, code = bop.can_shoot()
        if not flag_shoot:
            action_msg.set_result(code)
            return False

        target_id = action_msg.get_target_obj_id()
        weapon_id = action_msg.get_weapon_id()

        target_bop = operator_sets.get_bop_by_id(target_id)
        if not target_bop:
            action_msg.set_result(ActionResult.CantFindOperator)  # 算子不存在
            return False

        flag, result = _check_shoot_paras(attack_bop=bop, target_bop=target_bop, weapon_id=weapon_id, state_data=state_data)
        if not flag:
            action_msg.set_result(result)
            return False

        return True
    except Exception as e:
        print_exception(e)
        raise e


def _check_shoot_paras(attack_bop, target_bop, weapon_id, state_data, need_check_see=True):
    """

    :param attack_bop:
    :param target_bop:
    :param weapon_id:
    :param state_data:
    :return: (True, attack_level) or (False, ResultCode)
    """
    try:
        if weapon_id not in attack_bop.get_carry_weapons():
            return False, ActionResult.OperatorNotCarryThisWeapon
        weapon_sets = state_data.get_weapon()
        if not weapon_sets.is_zm_weapon(weapon_id):
            return False, ActionResult.CantFindWeapon
        target_type = target_bop.get_bop_type()
        if target_type not in weapon_sets.get_wp_att_types(wp_id=weapon_id):
            return False, ActionResult.CantShootOfErrorObjectType
        if target_bop.get_bop_sub_type() == OperatorSubType.FlyMissile:
            return False, ActionResult.CantShootToFlyMissile

        terrain = state_data.get_terrain()
        attack_pos = attack_bop.get_hex_pos()
        target_pos = target_bop.get_hex_pos()

        distance = terrain.get_dis_between_hex(attack_pos, target_pos)
        wp_dis = weapon_sets.get_weapon_att_range(weapon_id, target_type)
        if not wp_dis[0] <= distance <= wp_dis[1]:
            return False, ActionResult.CantShootOfOutOfAim
        if attack_bop.get_bop_sub_type() != OperatorSubType.FlyMissile:
            if weapon_sets.is_missle(weapon_id):
                if attack_bop.get_missile_num() < 1:
                    return False, ActionResult.LackAmmunition
            else:
                if attack_bop.get_bullet_num() < 1:
                    return False, ActionResult.LackAmmunition

        if need_check_see:
            if not check_bop_see(bop_a=attack_bop, bop_b=target_bop, t_terrain=terrain):
                return False, ActionResult.CantShootCauseCantSee

        att_level, info = weapon_sets.get_attack_level(bop_attacker=attack_bop, bop_obj=target_bop, weapon_id=weapon_id)
        if att_level <= InvalidDamage.InvalidAttackLevel:
            return False, ActionResult.CantShootCauseInvalidAttackLevel

        return True, att_level
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
        weapon_sets = state_data.get_weapon()
        op_id = action_msg.get_op_id()
        bop = operator_sets.get_bop_by_id(op_id=op_id)
        if not bop:
            action_msg.set_result(ActionResult.CantFindOperator)  # 算子不存在
            return ActionStatus.Done
        target_id = action_msg.get_target_obj_id()
        weapon_id = action_msg.get_weapon_id()

        target_bop = operator_sets.get_bop_by_id(target_id)
        if not target_bop:
            action_msg.set_result(ActionResult.CantFindOperator)  # 算子不存在
            return ActionStatus.Done

        damage, info = weapon_sets.get_zm_damage(bop_attacker=bop, bop_obj=target_bop, weapon_id=weapon_id)
        _execute_shoot_paras(bop, target_bop, damage, state_manager, operator_sets)

        if bop.get_bop_sub_type() != OperatorSubType.FlyMissile:
            if weapon_sets.is_missle(weapon_id):
                missile_num = bop.get_missile_num()
                assert missile_num > 0
                bop.set_missile_num(missile_num - 1)
            else:
                bullet_num = bop.get_bullet_num()
                assert bullet_num > 0
                bop.set_bullet_num(bullet_num - 1)

        if info:
            cur_step = state_data.get_clock().get_cur_step()
            info["cur_step"] = cur_step
            info["type"] = "直瞄射击"
            action_msg.set_judge_result(judge_info=info)
        return ActionStatus.Done
    except Exception as e:
        print_exception(e)
        raise e


def _execute_shoot_paras(attack_bop, target_bop, damage, state_manager, operator_sets):
    try:
        _execute_damage(target_bop=target_bop, damage=damage, state_manager=state_manager, operator_sets=operator_sets)

        _execute_shoot(attack_bop=attack_bop, state_manager=state_manager)

        if attack_bop.get_move_state() == MoveState.Hide:
            attack_bop.set_move_state(MoveState.NormalMove)
        # 巡飞弹攻击后自毁
        if attack_bop.get_bop_sub_type() == OperatorSubType.FlyMissile:
            attack_bop.set_blood(0)
            died_bop_ids = operator_sets.on_bop_died(attack_bop)
            for obj_id in died_bop_ids:
                state_manager.stop_all_valid_states(obj_id)
    except Exception as e:
        print_exception(e)
        raise e


def _execute_damage(target_bop, damage, state_manager, operator_sets):
    try:
        if damage > InvalidDamage.InvalidDamageValue:
            died = target_bop.set_damage(damage)
            if died:
                died_bop_ids = operator_sets.on_bop_died(target_bop)
                for bop_id in died_bop_ids:
                    state_manager.stop_all_valid_states(bop_id)
            else:
                if target_bop.get_passenger_ids():
                    for p_id in target_bop.get_passenger_ids():
                        p_bop = operator_sets.get_bop_by_id(p_id)
                        p_bop.set_blood(target_bop.get_blood())
            if not target_bop.is_died() and target_bop.is_kept():
                target_id = target_bop.get_bop_id()
                valid_states = state_manager.get_valid_state_type_by_bop(obj_id=target_id)
                if StateType.RestoreKeep in valid_states:
                    state_manager.refresh_state(obj_id=target_id, state_type=StateType.RestoreKeep, action_msg=None)
                else:
                    state_manager.start_state(obj_id=target_id, state_type=StateType.RestoreKeep, action_msg=None)
                if target_bop.get_bop_type() == OperatorType.People and StateType.Move in valid_states:
                    state_manager.stop_state(obj_id=target_id, state_type=StateType.Move)
    except Exception as e:
        print_exception(e)
        raise e


def _execute_shoot(attack_bop, state_manager):
    try:
        attack_bop_id = attack_bop.get_bop_id()
        valid_states = state_manager.get_valid_state_type_by_bop(obj_id=attack_bop_id)
        assert StateType.WeaponCool not in valid_states
        state_manager.start_state(obj_id=attack_bop_id, state_type=StateType.WeaponCool, action_msg=None)

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
    :return: (True, [{"target_obj_id": "目标ID int", "weapon_id": "武器ID int", "attack_level": "攻击等级 int"}]) or (False,code)
    """
    try:
        operator_sets = state_data.get_operator_sets()
        bop = operator_sets.get_bop_by_id(op_id=obj_id)
        if not bop:
            return False, ActionResult.CantFindOperator

        enemy_bops = operator_sets.get_my_see_valid_enemy_bops(color=bop.color)
        if not enemy_bops:
            return False, ActionResult.CantShootCauseCantSee

        flag, code = bop.can_shoot()
        if not flag:
            return False, code

        l_wps = bop.get_carry_weapons()
        if not l_wps:
            return False, ActionResult.CantFindWeapon

        paras = []
        for target_bop in enemy_bops:
            for wp_id in l_wps:
                flag, result = _check_shoot_paras(attack_bop=bop, target_bop=target_bop, weapon_id=wp_id, state_data=state_data)
                if flag:
                    paras.append({"target_obj_id": target_bop.obj_id, "weapon_id": wp_id, "attack_level": result})
                else:
                    continue
        if paras:
            return True, paras
        else:
            return False, None
    except Exception as e:
        print_exception(e)
        raise e


class Shooting:
    """
    射击状态
    """
    def __init__(self):
        """
        tar_op_id   # 目标算子ID
        waepon_id   # 武器编号
        cool_time   # 冷却时间
        unfold_time # 展开时间
        """
        pass