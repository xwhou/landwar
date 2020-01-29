#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-8 下午2:58
# @Author  : sgr
# @Site    : 
# @File    : clock.py


from common.m_exception import print_exception
from wgconst.const import ClockParas


class Clock:
    """
    时钟类
    """
    def __init__(self, loader):
        """
        max_step    # 最大步长
        max_time    # 最大时长（S）
        cur_step    # 当前步长
        cur_time    # 当前时间
        tick    # s/每步长
        """
        self.loader = loader
        self.cur_step = 0
        self.tick = 1.0 / ClockParas.FPS
        scenario = self.loader.get_scenario()
        if scenario in ClockParas.MaxTime.keys():
            self.max_time = ClockParas.MaxTime[scenario]
        else:
            self.max_time = ClockParas.MaxTimeDefault
        self.max_step = self.max_time / self.tick
        self.take_time_per_step = self.tick / ClockParas.SpeedUpRatio
        # print(self.take_time_per_step)
        self.game_over = False

    def load(self):
        """
        Todo 加载数据
        :return:
        """
        try:
            pass
        except Exception as e:
            print_exception(e)
            raise e

    def reset(self):
        self.cur_step = 0
        self.game_over = False

    def load_component(self, clock_data):
        try:
            self.cur_step = clock_data["cur_step"]
            self.game_over = self._judge_game_over()
        except Exception as e:
            print_exception(e)
            raise e

    def update(self):
        """
        :return: 是否结束
        """
        try:
            self.cur_step += 1
            if self._judge_game_over():
                self.game_over = True
            return self.game_over
        except Exception as e:
            print_exception(e)
            raise e

    def _judge_game_over(self):
        return self.cur_step >= self.max_step

    def get_cur_step(self):
        return self.cur_step

    def get_tick(self):
        return self.tick

    def get_take_time_per_step(self):
        return self.take_time_per_step

    def get_time_observation(self):
        try:
            return {
                'cur_step': self.cur_step,
                'tick': self.tick
            }
        except Exception as e:
            print_exception(e)
            raise e

    def get_time_observation_notes(self):
        return {
            "cur_step": "当前步长 int",
            "tick": "s/步 float"
        }