#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-8 下午3:08
# @Author  : sgr
# @Site    : 
# @File    : action_msg.py


from common.m_exception import print_exception
from wgconst.const import StateType
from wgmessage.action_result import ActionResult
from wgconst.const import SupportActionsNotes


class ActionMsg:
    """
    动作消息
    """
    def __init__(self, dic_action_msg, cur_step=-1, msg_id=-1):
        """
        id  # 唯一标识
        receive_step    # 收到时步长
        result  # 执行结果
        obj_id   # 算子ID
        msg_type  # 类型
        paras   # 参数
        """
        try:
            self.message = dic_action_msg

            self.msg_id = msg_id
            self.receive_step = cur_step
            self.result = -1
            self.dic_judge_msg = None

            self.msg_type = None
            self.obj_id = None
            self.move_path = None
            self.target_obj_id = None   # 目标算子ID
            self.weapon_id = None   # 武器ID
            self.guided_obj_id = None   # 被引导算子
            self.jm_pos = None  # 间瞄点
            self.target_state = None    # 目标状态
        except Exception as e:
            print_exception(e)
            raise e

    def check_paras(self):
        try:
            if not isinstance(self.message, dict):
                self.set_result(ActionResult.ErrorActionMsgType)
                return False
            if 'type' not in self.message.keys() or 'obj_id' not in self.message.keys():
                self.set_result(ActionResult.ErrorActionMsgParas)
                return False

            self.msg_type = self.message['type']
            self.obj_id = self.message['obj_id']

            if self.msg_type == StateType.Move:
                if 'move_path' not in self.message.keys():
                    self.set_result(ActionResult.ErrorActionMsgParas)
                    return False
                self.move_path = [int(loc) for loc in self.message['move_path']]
            elif self.msg_type == StateType.Shoot:
                if 'target_obj_id' not in self.message.keys() or 'weapon_id' not in self.message.keys():
                    self.set_result(ActionResult.ErrorActionMsgParas)
                    return False
                self.target_obj_id = self.message['target_obj_id']
                self.weapon_id = self.message['weapon_id']
            elif self.msg_type == StateType.GuideShoot:
                if 'target_obj_id' not in self.message.keys() or 'weapon_id' not in self.message.keys() or 'guided_obj_id' not in self.message.keys():
                    self.set_result(ActionResult.ErrorActionMsgParas)
                    return False
                self.target_obj_id = self.message['target_obj_id']
                self.weapon_id = self.message['weapon_id']
                self.guided_obj_id = self.message['guided_obj_id']
            elif self.msg_type == StateType.JMPlan:
                if 'weapon_id' not in self.message.keys() or 'jm_pos' not in self.message.keys():
                    self.set_result(ActionResult.ErrorActionMsgParas)
                    return False
                self.weapon_id = self.message['weapon_id']
                self.jm_pos = self.message['jm_pos']
            elif self.msg_type == StateType.GetOn:
                if 'target_obj_id' not in self.message.keys():
                    self.set_result(ActionResult.ErrorActionMsgParas)
                    return False
                self.target_obj_id = self.message['target_obj_id']
            elif self.msg_type == StateType.GetOff:
                if 'target_obj_id' not in self.message.keys():
                    self.set_result(ActionResult.ErrorActionMsgParas)
                    return False
                self.target_obj_id = self.message['target_obj_id']
            elif self.msg_type == StateType.ChangeState:
                if 'target_state' not in self.message.keys():
                    self.set_result(ActionResult.ErrorActionMsgParas)
                    return False
                self.target_state = self.message['target_state']
            elif self.msg_type == StateType.Occupy:
                pass
            elif self.msg_type == StateType.RestoreKeep:
                pass
            return True
        except Exception as e:
            print_exception(e)
            raise e

    def get_msg_id(self):
        return self.msg_id

    def get_op_id(self):
        """
        返回操作算子的ID
        :return:
        """
        return self.obj_id

    def get_action_type(self):
        """
        返回动作类型
        :return:
        """
        return self.msg_type

    def get_move_path(self):
        return self.move_path

    def get_target_obj_id(self):
        return self.target_obj_id

    def get_weapon_id(self):
        return self.weapon_id

    def get_guided_obj_id(self):
        return self.guided_obj_id

    def get_jm_pos(self):
        return self.jm_pos

    def get_car_id(self):
        return self.target_obj_id

    def get_passenger_id(self):
        return self.target_obj_id

    def get_target_state(self):
        return self.target_state

    def set_result(self, result):
        self.result = result

    def set_judge_result(self, judge_info):
        try:
            self.dic_judge_msg = judge_info
        except Exception as e:
            print_exception(e)
            raise e

    def get_judge_result(self):
        return self.dic_judge_msg

    def to_dict(self):
        """

        :return: {"cur_step": "当前步长 int",
                  "message": {}
                  }
        """
        try:
            result = {"cur_step": self.receive_step,
                      "message": self.message,
                      }
            if isinstance(self.result, dict) and self.result["code"] != ActionResult.Success:
                result["error"] = self.result
            return result
        except Exception as e:
            print_exception(e)
            raise e


def gen_action_notes():
    return {
        "obj_id": "算子ID int",
        "type": "动作类型 {}".format(SupportActionsNotes),
        "move_path": "机动路径 list(int)",
        "target_obj_id": "目标算子ID or 车辆算子ID or 下车算子ID int",
        "weapon_id": "武器编号 int",
        "jm_pos": "间瞄点位置 int",
        "target_state": "目标状态 int",
        "guided_obj_id": "被引导算子单位ID"
    }


if __name__ == "__main__":
    import json
    with open("action.json", "w") as f:
        json.dump(gen_action_notes(), f, ensure_ascii=False)