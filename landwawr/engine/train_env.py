#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-12-2 上午8:42
# @Author  : sgr
# @Site    : 
# @File    : train_env.py

import os
import json
import gc
from common.m_exception import print_exception
from train_engine import TrainEngine
from wgconst.const import Color
from wgwriter.saver import Saver
from verify import come_in
from wgconst.const import ScenarioInfo


class TrainEnv:
    def __init__(self, team_name, team_leader_name, code, scenario, data_dir="../", flag_save_replay=True):
        self.scenario = scenario
        self.engine = None
        self.saver = None
        # self.all_state_datas = []
        self.all_dic_state_dates = []
        self.flag_save_replay = flag_save_replay
        self.team_name = team_name
        self.team_leader = team_leader_name
        self.code = code
        try:
            self.login(team_name, team_leader_name, code)
            assert(scenario in list(ScenarioInfo.keys())), "Invalid Scenario"
            self.engine = TrainEngine(scenario_index=scenario, data_dir=data_dir)
            self.saver = Saver()
            self.saved_state_once = False
        except Exception as e:
            print_exception(e)
            raise e

    def login(self, team_name, team_leader, code):
        try:
            assert come_in.check(team_name, team_leader, code)
        except Exception as e:
            print("Login Failed!")
            raise e

    def reset(self):
        """
        游戏初始化
        :return: 态势(见doc/state_data_note.json), True-游戏结束/False-游戏未结束
        """
        try:
            self.saved_state_once = False
            # self.all_state_datas = []
            self.all_dic_state_dates = []
            state_data, game_over = self.engine.reset()
            self.all_dic_state_dates.append(state_data[Color.GREEN])
            self.engine.state_data.operator_sets.auto_get_on()
            return self.engine.get_sd_data(), self.engine.check_game_over()
        except Exception as e:
            print_exception(e)
            raise e

    def step(self, action_msgs, count=1):
        """
        引擎推进
        :param action_msgs: 动作集 [dict]
        :param count: 推进步数
        :return: 态势(见doc/state_data_note.json), True-游戏结束/False-游戏未结束
        """
        try:
            self.engine.actions(list_action_msg=action_msgs)
            state_data, game_over = self.engine.step(count=count)

            if self.flag_save_replay:
                # self.all_state_datas.append(to_json_string(state_data[Color.GREEN]))
                self.all_dic_state_dates.append(state_data[Color.GREEN])

            return state_data, game_over
        except Exception as e:
            print_exception(e)
            raise e

    def save_replay(self, match_id):
        """
        保存复盘数据
        :param match_id 复盘文件保存到 match_id.json
        :return:
        """
        try:
            # if len(self.all_state_datas) == 500 or game_over:
            #     create_table = False if self.saved_state_once else True
            #     self.saver.save_replay(match_id=self.match_id, scenario=self.scenario, mode=MatchMode.JJ,
            #                            data=self.all_state_datas, create_table=create_table)
            #     self.all_state_datas = []
            #     self.saved_state_once = True

            self.saver.save_replay_in_local_file(match_id=match_id,
                                                 data=self.all_dic_state_dates)

            # actions = self.engine.action_msg_sets.get_save_message()
            # self.saver.save_action_in_local_file(match_id=self.match_id,
            #                                      data=actions)
        except Exception as e:
            print_exception(e)
            raise e

    def __del__(self):
        self.engine = None
        self.saver = None
        self.all_dic_state_dates = []
        gc.collect()


if __name__ == "__main__":
    try:
        env = TrainEnv('陆战之王', '李四', '6ZmG5o', scenario=0, data_dir="../")
        game_over = False
        # while not game_over:
        #     observations, game_over = env.step(None, count=1)
        # env.save_replay("s")
    except Exception as e:
        print_exception(e)
        raise e