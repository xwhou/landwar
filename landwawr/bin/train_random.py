#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-12-3 下午1:53
# @Author  : sgr
# @Site    : 
# @File    : train_rule.py

import sys
import importlib
from argparse import ArgumentParser
from datetime import datetime

sys.path.append("../")
sys.path.append("../engine")
sys.path.append("../ai")
from common.m_exception import print_exception
from engine.train_env import TrainEnv
import wginterface.interface as wginterface
import wgruler.ruler as wgruler
import time

scenario = {
    1531: "城镇居民地连级想定",
    3531: "城镇居民地营级想定",
    1631: "岛上台地连级想定",
    3631: "岛上台地营级想定",
    1231: "高原通道连级想定",
    3231: "高原通道营级想定",

}
def run_one_game(module, cls, scenario, num_plays, team_name, team_leader_name, team_code, save_replay = 1):
    '''
    :param module: 调用AI模型地址
    :param cls: AI类名
    :param match_id: 比赛ID
    :param scenario: 想定编号
    :param save_replay: 是否保存录像
    :return:
    '''
    try:
        #启动一个训练环境

        env = TrainEnv(team_name=team_name, team_leader_name=team_leader_name,
                       code=team_code,
                       scenario=scenario, data_dir="../", flag_save_replay=save_replay)

        # 初始化接口
        interface_wgruler = wgruler.Rule()
        red_interface = wginterface.AI_InterFace(color=0,  env=env, ruler=interface_wgruler,scenario = scenario)
        blue_interface = wginterface.AI_InterFace(color=1,  env=env, ruler=interface_wgruler,scenario = scenario)

        # 加载AI类
        AI = importlib.import_module(module)
        AI = getattr(AI, cls)
        ai_red = AI(color=0, obj_interface=red_interface, interface_wgruler=interface_wgruler)
        ai_blue = AI(color=1, obj_interface=blue_interface, interface_wgruler=interface_wgruler)

        for i in range(num_plays):
            match_id = "s{}_{}_{}".format(start, scenario, i)
            print("match_id = {}".format(match_id))
            observations, game_over = env.reset()
            ai_red.reset()
            ai_blue.reset()

            engine_time = 0
            ai_time = 0
            while not game_over:
                t1 = time.time()
                actions = ai_red.step(observations[ai_red.color])
                actions_blue = ai_blue.step(observations[ai_blue.color])
                t2 = time.time()
                ai_time += (t2 - t1)
                if actions or actions_blue:
                    print("cur_step={}".format(env.engine.state_data.clock.get_cur_step()))
                observations, game_over = env.step(actions + actions_blue, count=1)
                engine_time += (time.time() - t2)
            env.save_replay(match_id)
            print("time: {}".format(ai_time + engine_time))
    except Exception as e:
        print_exception(e)
        raise e


if __name__ == "__main__":
    parser = ArgumentParser()
    # parser.add_argument("-c", "--config", default="./config/netconfig4qdai_0.json", help="config for qdai")
    parser.add_argument("-t", "--team_name", default="陆战之王", help="队名")
    parser.add_argument("-tl", "--team_leader", default="李四", help="队长姓名")
    parser.add_argument("-c", "--code", default="6ZmG5o", help="队伍编码")
    parser.add_argument("-s", "--scenario", default=1231, help="想定编号")
    args = parser.parse_args()
    # 想定列表
    scenario_list = [1531, 3531, 1631, 3631, 1231, 3231]

    time_list = {key: 0 for key in scenario_list}
    num_plays = 1  # 比赛次数
    start = datetime.now().strftime("%m%d%H%M")
    for scenario in scenario_list:
        t1 = time.time()
        run_one_game(module="ai.random_ai", cls="RandomAI",  scenario=scenario,
                     num_plays=num_plays,
                     team_name=args.team_name,
                     team_code=args.code,
                     team_leader_name=args.team_leader)
        print("done")
        t2 = time.time()
        time_list[scenario] = t2 - t1
    print(time_list)