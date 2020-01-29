#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-12-10 下午3:42
# @Author  : sgr
# @Site    : 
# @File    : random_ai.py



import random
from common.m_exception import print_exception
from ai.base_ai import BaseAI
from wgconst.const import StateType



class RandomAI(BaseAI):
    def __init__(self, color, obj_interface, interface_wgruler):
        super(RandomAI, self).__init__(color, obj_interface, interface_wgruler)
        self.observations = None
        self.game_over = None


    def step(self, state_data):
        '''
        更新态势,判断游戏是否结束,若尚未结束则调用_do_action()生成并执行动作
        :return: True
        '''
        try:
            self.obj_interface.update_observation(state_data)
            super(RandomAI, self).step(state_data)
            self.observations = state_data
            return self._do_action()
        except Exception as e:
            print_exception(e)
            raise e

    # def step(self):
    #     '''
    #     更新态势,判断游戏是否结束,若尚未结束则调用_do_action()生成并执行动作
    #     :return: True
    #     '''
    #     try:
    #         self.update_state_data()
    #         if self.game_over:
    #             print("Game Over")
    #             return False
    #
    #         return self._do_action()
    #     except Exception as e:
    #         print_exception(e)
    #         raise e

    def _do_action(self):
        try:
            result = []

            # 从可执行
            for obj_id, valid_actions in self.obj_interface.valid_actions.items():

                # 从可执行动作类型中随机选择一种动作
                valid_action_types = list(valid_actions.keys())
                random_actionType = random.choice(valid_action_types)

                # 随机从当前可执行动作类型下选择可执行动作参数
                valid_paras = valid_actions[random_actionType]
                random_para = random.choice(valid_paras) if valid_paras else None

                # 补充动作参数
                if random_actionType == StateType.Move:  # 生成机动路线
                    bop = self.get_bop_by_id(obj_id)
                    random_para = self._choose_move_paras(bop)
                elif random_actionType == StateType.JMPlan:  # 生成间瞄目标点
                    target_pos = self._choose_random_pos()
                    random_para.update({"jm_pos": target_pos})

                # 生成动作
                action = self.create_action_msg(obj_id=obj_id, action_type=random_actionType, paras=random_para)
                result.append(action)

            if result:  # 如果生成了动作则打印并执行动作
                print(result)
            return result
        except Exception as e:
            print_exception(e)
            raise e

    def _choose_move_paras(self, bop):
        """
        :param paras None
        :return: {"move_path": []}
        """
        try:
            target_pos = self._choose_random_pos()
            move_path = self.obj_interface.terrain.get_path(bop.cur_hex, target_pos, mod=0)
            # print("start_pos={}, target_pos={}, \n move_path={}".format(bop.cur_hex, target_pos, move_path))
            return {"move_path": move_path}
        except Exception as e:
            print_exception(e)
            raise e

    def _choose_random_pos(self):
        return random.randint(3, 55) * 100 + random.randint(3, 50)


if __name__ == "__main__":
    pass