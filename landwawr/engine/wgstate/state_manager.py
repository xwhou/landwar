#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-24 下午8:46
# @Author  : sgr
# @Site    : 
# @File    : state_manager.py

import importlib
from collections import defaultdict
from common.m_exception import print_exception
from wgconst.const import StateClass
from wgmessage.action_result import ActionResult
from wgconst.const import ActionStatus
from wgconst.const import SupportActions
from wgconst.const import SupportActionsNotes
from wgconst.const import Color


class StateManager:
    def __init__(self, action_msg_sets, state_data):
        self.action_msg_sets = action_msg_sets
        self.state_data = state_data
        self.all_states = {}    # {state_type: {'class': Class, 'method': function, "valid_action_paras": function} }
        self.valid_bop_states = {}  # {'obj_id': {'state_type': State}}
        try:
            self._init_states()
        except Exception as e:
            print_exception(e)
            raise e

    def handle_action(self, message):
        """
        处理动作消息
        :param message:
        :param state_data
        :return: 当前动作状态 1-正在处理 2-处理完毕
        """
        try:
            action_type = message.get_action_type()
            handle_method = self._get_handle_action_method(action_type)
            if handle_method is None:
                message.set_result(ActionResult.ErrorActionType)
                return ActionStatus.Done
            status = handle_method(message=message,
                                   state_manager=self,
                                   state_data=self.state_data)
            return status
        except Exception as e:
            print_exception(e)
            raise e

    def reset(self):
        try:
            self.valid_bop_states = {}
        except Exception as e:
            print_exception(e)
            raise e

    def update(self):
        """
        2019年12月26日: Modify 状态更新后，因算子死亡，会导致很多状态无效，跳过这些状态的更新;
        :return:
        """
        try:
            bop_valid_states = list(self.valid_bop_states.values())
            for valid_state in bop_valid_states:
                states = list(valid_state.values())
                for state in states:
                    if not state.is_finished():
                        state.update(state_manager=self)
            # for _, states in self.valid_bop_states.items():
            #     for _, state in states.items():
            #         state.update(state_manager=self)
        except Exception as e:
            print_exception(e)
            raise e

    def _init_states(self):
        try:
            for cl, dic in StateClass.AllStates.items():
                module = importlib.import_module(dic['module'])
                tmp_class = self._m_getattr(module, dic["class"])
                tmp_method = self._m_getattr(module, StateClass.HandleActionFun)
                tmp_valid_action_paras = self._m_getattr(module, StateClass.ValidActionFun)
                self.all_states[cl] = {'class': tmp_class,
                                       'method': tmp_method,
                                       'valid_action_paras': tmp_valid_action_paras}
        except Exception as e:
            print_exception(e)
            raise e

    def _m_getattr(self, module, string):
        return getattr(module, string) if hasattr(module, string) else None

    def _get_handle_action_method(self, action_type):
        try:
            state_type = self._cvt_type_from_action_to_state(action_type)
            if state_type not in self.all_states.keys():
                return None
            else:
                return self.all_states[state_type]['method']
        except Exception as e:
            print_exception(e)
            raise e

    def _get_handle_valid_action_paras_method(self, action_type):
        try:
            state_type = self._cvt_type_from_action_to_state(action_type)
            if state_type not in self.all_states.keys():
                return None
            else:
                return self.all_states[state_type]['valid_action_paras']
        except Exception as e:
            print_exception(e)
            raise e

    def _cvt_type_from_action_to_state(self, action_type):
        """
        将动作类型转化为对应的态势类型并返回
        :param action_type:
        :return:
        """
        return action_type

    def get_valid_state_type_by_bop(self, obj_id):
        try:
            if obj_id in self.valid_bop_states.keys():
                return list(self.valid_bop_states[obj_id].keys())
            return []
        except Exception as e:
            print_exception(e)
            raise e

    def get_state_by_bop_and_type(self, obj_id, state_type):
        try:
            if obj_id in self.valid_bop_states.keys():
                if state_type in self.valid_bop_states[obj_id].keys():
                        return self.valid_bop_states[obj_id][state_type]
            return None
        except Exception as e:
            print_exception(e)
            raise e

    def stop_state(self, obj_id, state_type):
        try:
            state = self.get_state_by_bop_and_type(obj_id=obj_id, state_type=state_type)
            if state is not None:
                state.stop(self)
                self.valid_bop_states[obj_id].pop(state_type)
                if not self.valid_bop_states[obj_id]:
                    self.valid_bop_states.pop(obj_id)
        except Exception as e:
            print_exception(e)
            raise e

    def stop_all_valid_states(self, obj_id):
        try:
            if obj_id in self.valid_bop_states.keys():
                valid_state_types = list(self.valid_bop_states[obj_id].keys())
                for state_type in valid_state_types:
                    self.stop_state(obj_id, state_type)
        except Exception as e:
            print_exception(e)
            raise e

    def start_state(self, obj_id, state_type, action_msg):
        try:
            self.stop_state(obj_id, state_type)
            bop = self.state_data.get_operator_sets().get_bop_by_id(obj_id)
            if bop is not None:
                state = self.all_states[state_type]['class'](bop=bop,
                                                             state_data=self.state_data,
                                                             action_msg_sets=self.action_msg_sets)
                if obj_id not in self.valid_bop_states.keys():
                    self.valid_bop_states[obj_id] = {}
                self.valid_bop_states[obj_id][state_type] = state
                state.enter(action_msg=action_msg)
        except Exception as e:
            print_exception(e)
            raise e

    def refresh_state(self, obj_id, state_type, action_msg):
        try:
            state = self.get_state_by_bop_and_type(obj_id=obj_id, state_type=state_type)
            if state is not None:
                state.refresh(action_msg=action_msg)
        except Exception as e:
            print_exception(e)
            raise e

    def get_valid_actions(self):
        """

        :return: {
                    color: {
                                obj_id: {
                                            action_type: [paras]
                                        }
                           }
                 }
        """
        try:
            result = dict()
            result[Color.GREEN] = {}
            for color in Color.all_colors:
                result[color] = self._get_valid_actions_by_color(color)
                result[Color.GREEN].update(result[color])
            return result
        except Exception as e:
            print_exception(e)
            raise e

    def _get_valid_actions_by_color(self, color):
        """

        :param color:
        :return: {"obj_id": {"action_type": []}}
        """
        try:
            operator_sets = self.state_data.get_operator_sets()
            my_bops = operator_sets.get_valid_bops_by_color(color=color)
            result = defaultdict(dict)
            for bop in my_bops:
                for action_type in SupportActions:
                    handle_method = self._get_handle_valid_action_paras_method(action_type)
                    if handle_method is None:
                        continue
                    flag, paras = handle_method(bop.obj_id, self.state_data)
                    if flag:
                        result[bop.obj_id][action_type] = paras
            return result
        except Exception as e:
            print_exception(e)
            raise e

    def get_valid_actions_notes(self):
        return {
            "算子ID": {
                "1-机动": None,
                "2-射击": [{"target_obj_id": "目标ID int", "weapon_id": "武器ID int", "attack_level": "攻击等级 int"}],
                "3-上车": [{"target_obj_id": "车辆ID int"}],
                "4-下车": [{"target_obj_id": "乘客ID int"}],
                "5-夺控": None,
                "6-切换状态": [{"target_state": "目标状态 0-正常机动 1-行军 2-一级冲锋 3-二级冲锋 4-掩蔽"}],
                "7-移除压制": None,
                "8-间瞄": [{"weapon_id": "武器ID"}],
                "9-引导射击": [{"guided_obj_id": "被引导算子ID int", "target_obj_id": "目标算子ID",
                            "weapon_id": "武器ID int", "attack_level": "攻击等级 int"}]
            }
        }


if __name__ == "__main__":
    sm = StateManager(action_msg_sets=None,
                      state_data=None)
    print(sm.get_valid_actions_notes())
    print('done')