#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-5 上午9:37
# @Author  : sgr
# @Site    : 
# @File    : train_engine.py


import time
import copy

from common.m_exception import print_exception
from wgloader.file_loader import FileLoader
from state_data import StateData
from wgmessage.action_msg_sets import ActionMsgSets
from wgstate.state_manager import StateManager
from wgconst.const import Color
from common.my_json_encoder import to_json_string


class TrainEngine:
    """
    训练引擎, 管理训练所需组件, 提供训练所需接口
    Attributes:
        loader: 资源数据加载类
        state_data: 态势数据管理类
        action_msg_sets: 动作消息集合
        state_manager: 状态管理类
    """

    def __init__(self, scenario_index, data_dir="../", auto_get_on=True):
        """
        :param scenario_index   # 想定编号(映射到地图编号，算子编号，武器编号，夺控点编号，时钟编号)
        :param data_dir  # Data文件夹的相对目录
        :param auto_get_on # 是否自动上车
        :return None
        """
        try:
            self.scenario_index = scenario_index
            self.loader = FileLoader(scenario=scenario_index, data_dir=data_dir)

            self.state_data = StateData(self.loader, auto_get_on=auto_get_on)

            self.action_msg_sets = ActionMsgSets(clock=self.state_data.get_clock())
            self.state_manager = StateManager(action_msg_sets=self.action_msg_sets, state_data=self.state_data)
            self.start_time = 0
        except Exception as e:
            print_exception(e)
            raise e

    def actions(self, list_action_msg):
        """
        动作接收函数
            将动作发送到 action_msg_sets 中解析并保存；
        :param list_action_msg: 动作消息; 消息格式见xx
        :return:
        """
        self.action_msg_sets.receive(list_action_msg=list_action_msg)

    def reset(self):
        """
        态势初始化
        :return:
            态势数据（格式见xx Todo）,
            游戏是否结束标志位 True-结束 False-未结束
        """
        try:
            self.state_data.reset()
            self.action_msg_sets.reset()
            self.state_manager.reset()
            return self.get_sd_data(), self.state_data.clock.game_over
        except Exception as e:
            print_exception(e)
            raise e

    def load_component(self, operator_data=None, clock_data=None, cities_data=None):
        try:
            self.reset()
            self.state_data.load_component(operator_data=operator_data, clock_data=clock_data, cities_data=cities_data)
        except Exception as e:
            print_exception(e)
            raise e

    def step(self, count=1):
        """
        态势推进count步
        :param count: 步长 int
        :return: 最新态势（格式见xx Todo）,
                游戏是否结束标志位 True-结束 False-未结束
        """
        try:
            flag_game_over = False
            for i in range(count):
                t1 = time.time()
                self.action_msg_sets.update(self.state_manager)
                self.state_manager.update()
                flag_game_over = self.state_data.update(self.state_manager)
                t2 = time.time()
                inter = t2 - t1
                remain_time = self.state_data.get_clock().get_take_time_per_step() - inter
                # print("remain_time = {} ".format(remain_time))
                time.sleep(max(0, remain_time))
            return self.get_sd_data(), flag_game_over
        except Exception as e:
            print_exception(e)
            raise e

    def check_game_over(self):
        return self.state_data.clock.game_over

    def get_sd_data(self):
        """
        获取态势数据
        :return: 态势数据(见xx Todo)
        """
        try:
            states = {}
            for color in Color.all_colors:
                states[color] = self.state_data.get_observations(color)
            states[Color.GREEN] = self.state_data.get_observations(Color.GREEN)

            cur_step = self.state_data.clock.get_cur_step() - 1
            cur_step = max(cur_step, 0)
            if cur_step == 0:
                states[Color.GREEN]["terrain_id"] = int(self.loader.terrain_id)

            judge_info = self.action_msg_sets.get_judge_info(cur_step=cur_step)
            judge_info_jm = self.state_data.jm_point_sets.get_jm_judge_info(color=Color.GREEN,
                                                                            cur_step=cur_step)

            judge_info = judge_info + judge_info_jm
            for color in Color.all_colors + [Color.GREEN]:
                states[color]["judge_info"] = judge_info

            valid_actions = self.get_valid_actions()
            for color, actions in valid_actions.items():
                if color in states.keys():
                    states[color]['valid_actions'] = actions

            receive_actions = self.action_msg_sets.get_receive_action_msg(cur_step)
            states[Color.GREEN]["actions"] = receive_actions
            return copy.deepcopy(states)
        except Exception as e:
            print_exception(e)
            raise e

    def get_valid_actions(self):
        """
        返回所有候选动作集合 (见xx Todo)
        :return:
        """
        try:
            return self.state_manager.get_valid_actions()
        except Exception as e:
            print_exception(e)
            raise e

    def get_sd_data_notes(self):
        ds = self.state_data.get_observarion_notes()
        da = self.state_manager.get_valid_actions_notes()
        dj = self.action_msg_sets.get_judge_info_notes()
        da1 = self.action_msg_sets.get_receive_action_msg_note()
        ds.update({"valid_actions": da})
        ds.update({"judge_info": dj})
        ds.update({"actions": da1})
        return ds


if __name__ == "__main__":
    tr = TrainEngine(scenario_index=3231, data_dir="../", auto_get_on=True)
    tr.state_data.cal_scores()
    print(tr.state_data.scores)
    tr1 = TrainEngine(scenario_index=3231, data_dir="../", auto_get_on=False)
    tr1.state_data.cal_scores()
    print(tr1.state_data.scores)
    # with open("state_data_note.json", "w") as f:
    #     f.write(to_json_string(tr.get_sd_data_notes()))
    # with open("state_data_example.json", "w") as f:
    #     f.write(to_json_string(tr.get_sd_data()[0]))
    print("done")
