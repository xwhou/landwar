#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-27 下午11:17
# @Author  : sgr
# @Site    : 
# @File    : guide_shoot.py


from common.m_exception import print_exception
from wgmessage.action_result import ActionResult
from wgconst.const import ActionStatus
from wgconst.const import StateType
from wgconst.const import OperatorSubType
from wgstate.shooting import _check_shoot_paras
from wgstate.shooting import _execute_shoot_paras
from wgconst.const import MoveState


def _check(action_msg, state_data):
    """
    动作合法性检查
    :param action_msg:
    :param state_data:
    :return:
    """
    try:
        assert action_msg.get_action_type() == StateType.GuideShoot, 'State={} receive error action msg type = {}'.format(
            StateType.GuideShoot, action_msg.get_action_type())
        operator_sets = state_data.get_operator_sets()
        guide_id = action_msg.get_op_id()
        guide_bop = operator_sets.get_bop_by_id(op_id=guide_id)
        if not guide_bop:
            action_msg.set_result(ActionResult.CantFindOperator)  # 算子不存在
            return False

        flag, code = guide_bop.can_guide()
        if not flag:
            action_msg.set_result(code)
            return False

        target_id = action_msg.get_target_obj_id()
        weapon_id = action_msg.get_weapon_id()
        attack_id = action_msg.get_guided_obj_id()

        target_bop = operator_sets.get_bop_by_id(target_id)
        attack_bop = operator_sets.get_bop_by_id(attack_id)
        if not target_bop or not attack_bop:
            action_msg.set_result(ActionResult.CantFindOperator)  # 算子不存在
            return False

        flag, result = _check_guide_shoot_paras(guide_bop=guide_bop,
                                                attack_bop=attack_bop,
                                                target_bop=target_bop,
                                                weapon_id=weapon_id,
                                                state_data=state_data)
        if not flag:
            action_msg.set_result(result)
            return False

        return True
    except Exception as e:
        print_exception(e)
        raise e


def _check_guide_shoot_paras(guide_bop, attack_bop, target_bop, weapon_id, state_data):
    try:
        if guide_bop.get_bop_sub_type() in [OperatorSubType.Soldier, OperatorSubType.AutoChariot]:
            if guide_bop.get_launcher() != attack_bop.get_bop_id():
                return False, ActionResult.CantGuideCauseErrorLauncher
        flag, code = attack_bop.can_shoot()
        if not flag:
            return False, code
        if target_bop.get_bop_id() not in guide_bop.get_my_see_enemy_bop_ids():
            return False, ActionResult.CantGuideCauseNotSee
        weapon_sets = state_data.get_weapon()
        if not weapon_sets.can_weapon_be_guided(weapon_id):
            return False, ActionResult.CantGuideCauseErrorWeapon

        return _check_shoot_paras(attack_bop=attack_bop, target_bop=target_bop, weapon_id=weapon_id, state_data=state_data,
                                  need_check_see=False)
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
        guide_id = action_msg.get_op_id()
        guide_bop = operator_sets.get_bop_by_id(op_id=guide_id)
        if not guide_bop:
            action_msg.set_result(ActionResult.CantFindOperator)  # 算子不存在
            return ActionStatus.Done

        target_id = action_msg.get_target_obj_id()
        weapon_id = action_msg.get_weapon_id()
        attack_id = action_msg.get_guided_obj_id()

        target_bop = operator_sets.get_bop_by_id(target_id)
        attack_bop = operator_sets.get_bop_by_id(attack_id)
        if not target_bop or not attack_bop:
            action_msg.set_result(ActionResult.CantFindOperator)  # 算子不存在
            return ActionStatus.Done

        damage, info = weapon_sets.get_zm_damage(bop_attacker=attack_bop, bop_obj=target_bop, weapon_id=weapon_id)

        _execute_shoot_paras(attack_bop=attack_bop,
                             target_bop=target_bop,
                             damage=damage,
                             state_manager=state_manager,
                             operator_sets=operator_sets)

        _execute_guide_shoot_paras(guide_id=guide_id,
                                   state_manager=state_manager)

        if attack_bop.get_bop_sub_type() != OperatorSubType.FlyMissile:
            if weapon_sets.is_missle(weapon_id):
                missile_num = attack_bop.get_missile_num()
                assert missile_num > 0
                attack_bop.set_missile_num(missile_num - 1)
            else:
                bullet_num = attack_bop.get_bullet_num()
                assert bullet_num > 0
                attack_bop.set_bullet_num(bullet_num - 1)

        if guide_bop.get_move_state() == MoveState.Hide:
            guide_bop.set_move_state(MoveState.NormalMove)

        if info:
            cur_step = state_data.get_clock().get_cur_step()
            info["cur_step"] = cur_step
            info["type"] = "引导射击"
            info["guide_obj_id"] = guide_id
            action_msg.set_judge_result(judge_info=info)

        return ActionStatus.Done
    except Exception as e:
        print_exception(e)
        raise e


def _execute_guide_shoot_paras(guide_id, state_manager):
    try:
        valid_states = state_manager.get_valid_state_type_by_bop(obj_id=guide_id)
        assert StateType.WeaponCool not in valid_states
        if StateType.WeaponCool not in valid_states:
            state_manager.start_state(obj_id=guide_id, state_type=StateType.WeaponCool, action_msg=None)
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
        flag, code = bop.can_guide()
        if not flag:
            return False, code
        my_bops = operator_sets.get_valid_bops_by_color(color=bop.color)
        my_bops = [m_bop for m_bop in my_bops if m_bop.get_guide_ability()]
        enemy_bops = operator_sets.get_my_see_valid_enemy_bops(color=bop.color)
        if not my_bops or not enemy_bops:
            return False, ActionResult.CantFindOperator
        paras = []
        for guided_bop in my_bops:
            l_weapons = guided_bop.get_carry_weapons()
            if not l_weapons:
                continue
            for enemy_bop in enemy_bops:
                for weapon in l_weapons:
                    flag, result = _check_guide_shoot_paras(guide_bop=bop,
                                             attack_bop=guided_bop,
                                             target_bop=enemy_bop,
                                             weapon_id=weapon,
                                             state_data=state_data)
                    if flag:
                        paras.append({
                            "guided_obj_id": guided_bop.obj_id,
                            "target_obj_id": enemy_bop.obj_id,
                            "weapon_id": weapon,
                            "attack_level": result
                        })
        if paras:
            return True, paras
        else:
            return False, None
    except Exception as e:
        print_exception(e)
        raise e