#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-8 下午3:01
# @Author  : sgr
# @Site    : 
# @File    : action_msg_sets.py


import pandas

from common.m_exception import print_exception
from wgconst.const import ActionStatus
from wgmessage.action_msg import ActionMsg


class ActionMsgSets:
    """
    动作管理类
    Attributes:
        clock: 时钟对象的引用
        total_action_msg: 所有动作消息对象 {"动作唯一ID int": "动作消息对象 ActionMessage"}
        action_index: 动作索引 DataFrame(cols=["ActionID", "ObjID", "ActionType", "ReceiveStep", "ActionStatus"])
        all_judge_info: 所有裁决信息 {"裁决发生步长 int": "裁决信息 list(dict)"}
    """

    def __init__(self, clock):
        self.clock = clock
        self.dic_cols = {'ActionID': -1,  # 动作唯一ID
                         'ObjID': -1,  # 算子ID
                         'ActionType': -1,  # 动作类型
                         'ReceiveStep': -1,  # 收到动作时游戏步长
                         'ActionStatus': -1,  # 状态 0-待处理 1-正在处理 2-处理完毕
                         }

        self.total_action_msg = {}
        self.action_index = pandas.DataFrame(columns=self.dic_cols.keys())  # 动作快速索引
        self.all_judge_info = {}
        self.action_total_nums = 0

    def receive(self, list_action_msg):
        """
        收到动作消息：
        为每个动作消息生成ID,
        做参数合法性检查，
        根据检查结果加入到相应的队列中
        :param list_action_msg: [dict]
        :return:
        """
        try:
            if list_action_msg:
                cur_step = self.clock.get_cur_step()
                l_index = []
                for dic_action_msg in list_action_msg:
                    ac_msg = ActionMsg(dic_action_msg=dic_action_msg, cur_step=cur_step, msg_id=self.action_total_nums)
                    valid = ac_msg.check_paras()
                    self.total_action_msg[self.action_total_nums] = ac_msg
                    action_status = ActionStatus.Todo if valid else ActionStatus.Done
                    l_index.append({'ActionID': self.action_total_nums,  # 动作唯一ID
                                     'ObjID': ac_msg.get_op_id(),  # 算子ID
                                     'ActionType': ac_msg.get_action_type(),  # 动作类型
                                     'ReceiveStep': cur_step,  # 收到动作时游戏步长
                                     'ActionStatus': action_status,  # 状态 0-待处理 1-正在处理 2-处理完毕
                                     })
                    self.action_total_nums += 1
                self.action_index = self.action_index.append(l_index, ignore_index=True)

        except Exception as e:
            print_exception(e)
            raise e

    def reset(self):
        try:
            self.total_action_msg = {}
            self.action_index = pandas.DataFrame(columns=self.dic_cols.keys())  # 动作快速索引
            self.all_judge_info = {}
            self.action_total_nums = 0
        except Exception as e:
            print_exception(e)
            raise e

    def update(self, state_manager):
        """Todo 效率低"""
        try:
            todo_action_id = self._get_spec_status_action_id(ActionStatus.Todo)
            for ai in todo_action_id:
                action_msg = self.total_action_msg[ai]
                status = state_manager.handle_action(message=action_msg)
                self.set_action_status(ai, status)
        except Exception as e:
            print_exception(e)
            raise e

    def set_action_status(self, action_id, status):
        try:
            spec_index = self.action_index[self.action_index['ActionID'] == action_id].index
            self.action_index.loc[spec_index, 'ActionStatus'] = status
            if status == ActionStatus.Done:
                if self.total_action_msg[action_id] is not None:
                    if self.total_action_msg[action_id].dic_judge_msg is not None:
                        cur_step = self.clock.get_cur_step()
                        if cur_step not in self.all_judge_info.keys():
                            self.all_judge_info[cur_step] = []
                        self.all_judge_info[cur_step].append(self.total_action_msg[action_id].dic_judge_msg)

        except Exception as e:
            print_exception(e)
            raise e

    def get_judge_info(self, cur_step):
        try:
            if cur_step in self.all_judge_info.keys():
                return self.all_judge_info[cur_step]
            return []
        except Exception as e:
            print_exception(e)
            raise e

    def get_judge_info_notes(self):
        return [{
                    "cur_step": "当前步长",
                    "type": "伤害类型 str",
                    "att_obj_id": "攻击算子ID, int",
                    "target_obj_id": "目标算子ID int",
                    "guide_obj_id": "引导算子ID int",
                    "distance": "距离",
                    "ele_diff": "高差等级",
                    "att_obj_blood": "攻击算子血量",
                    "align_status": "较射类型 int 0-无较射 1-格内较射 2-目标较射",
                    "offset": "偏移 bool",
                    "att_level": "攻击等级 int ",
                    "wp_id": "武器ID int",
                    "random1": "随机数1 int",
                    "ori_damage": "原始战损",
                    "random2_rect": "随机数2修正值",
                    "random2": "随机数2",
                    "rect_damage": "战损修正值",
                    "damage": "最终战损"
                }]

    def get_save_message(self):
        try:
            return [action_msg.to_dict() for action_msg in self.total_action_msg.values()]
        except Exception as e:
            print_exception(e)
            raise e

    def get_receive_action_msg(self, step):
        try:
            action_ids = list(self.action_index[self.action_index["ReceiveStep"] == step]["ActionID"])
            return [self.total_action_msg[action_id].to_dict() for action_id in action_ids]
        except Exception as e:
            print_exception(e)
            raise e

    def get_receive_action_msg_note(self):
        return [
            {
                "cur_step": "当前步长 int",
                "message": {
                    "obj_id": "算子ID int",
                    "type": "动作类型 ['1-机动', '2-射击', '3-上车', '4-下车', '5-夺控', '6-切换状态', '7-移除压制', '8-间瞄', '9-引导射击']",
                    "move_path": "机动路径 list(int)",
                    "target_obj_id": "目标算子ID or 车辆算子ID or 下车算子ID int",
                    "weapon_id": "武器编号 int",
                    "jm_pos": "间瞄点位置 int",
                    "target_state": "目标状态 int",
                    "guided_obj_id": "被引导算子单位ID"
                },
                "error": {
                    "code": "错误码 int",
                    "message": "错误原因 str"
                }
            }
        ]

    def _get_spec_status_action_id(self, status):
        try:
            return list(self.action_index[self.action_index['ActionStatus'] == status]['ActionID'])
        except Exception as e:
            print_exception(e)
            raise e


if __name__ == "__main__":
    class TClock:
        def get_cur_step(self):
            return 1

    class TStateManager:
        def handle_action(self, message):
            message.set_result(2)
            return 2

    am = ActionMsgSets(TClock())
    am.receive([{'obj_id': 12, 'type': 1, 'move_path': [15, 18]}, {'obj_id': 11, 'type': 1, 'move_path': [16, 19]}])
    print(am.action_index)
    am.update(TStateManager())
    print(am.action_index)
