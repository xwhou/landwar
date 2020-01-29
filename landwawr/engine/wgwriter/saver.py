#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-12-2 下午1:01
# @Author  : sgr
# @Site    : 
# @File    : saver.py


import os
import json
import shutil
import copy
from common.my_json_encoder import to_json_string
from common.m_exception import print_exception
# from wgwriter.db_operator import DBOperator
# from wgconst.const import MatchStatus
# from wgconst.const import EngineVersion
# from wgconst.const import ScenarioInfo


class Saver:
    def __init__(self):
        try:
            # self.db_operator = DBOperator()
            self.save_file_path = "../logs/replay/"
            if not os.path.exists(self.save_file_path):
                os.makedirs(self.save_file_path)
        except Exception as e:
            print_exception(e)
            raise e

    # def save_replay(self, match_id, scenario, mode, data, create_table=True):
    #     try:
    #         self.db_operator.connect_wargame()
    #         if not self.db_operator.select_room(condition="MatchID=\'{}\'".format(match_id)):
    #             info = {'MatchID': match_id,
    #                     'State': MatchStatus.Ended,
    #                     'Scenario': scenario,
    #                     'MapName': ScenarioInfo[scenario]["MapName"],
    #                     'Mode': mode,
    #                     'Engine': EngineVersion.RTS}
    #             self.db_operator.insert_room(info)
    #         self.db_operator.close()
    #         self.db_operator.connect_review()
    #         if create_table:
    #             self.db_operator.create_match_review_table(match_id)
    #         self.db_operator.insert_review_state(match_id, l_states=data)
    #         self.db_operator.close()
    #         # self.save_player_in_local_file(match_id=match_id, data=data)
    #     except Exception as e:
    #         print_exception(e)
    #         raise e

    def save_player_in_local_dirs(self, match_id, data):
        try:
            dir = os.path.join(self.save_file_path, "{}".format(match_id))
            if os.path.exists(dir):
                shutil.rmtree(dir)
            os.makedirs(dir)
            per_file_data_nums = 120    # 一个文件存的最大条目数
            file_nums = (len(data) + per_file_data_nums - 1) // per_file_data_nums
            for i in range(file_nums):

                str_file = os.path.join(dir, "{}.json".format(i))

                end = min((i + 1)*per_file_data_nums, len(data))
                with open(str_file, "w") as f:
                    # json.dump(data, f, ensure_ascii=False)
                    f.write(to_json_string(data[i * per_file_data_nums: end]))
        except Exception as e:
            print_exception(e)
            raise e

    def save_replay_in_local_file(self, match_id, data):
        try:
            # data = self.reduce_state_data(data, increment=True)
            str_file = os.path.join(self.save_file_path, "{}.json".format(match_id))

            with open(str_file, "w", encoding="gbk") as f:
                # json.dump(data, f, ensure_ascii=False)
                f.write(to_json_string(data))
        except Exception as e:
            print_exception(e)
            raise e

    # def save_replay_in_local_file(self, match_id, data):
    #     try:
    #         import time
    #         t1 = time.time()
    #         data1 = self.reduce_state_data(data, increment=True)
    #         str_file = os.path.join(self.save_file_path, "{}.json".format(match_id))
    #
    #         with open(str_file, "w") as f:
    #             # json.dump(data, f, ensure_ascii=False)
    #             f.write(to_json_string(data1))
    #         t2 = time.time()
    #         print(t2 - t1)
    #
    #         data2 = self.reduce_state_data(data, increment=False)
    #         str_file = os.path.join(self.save_file_path, "{}_ori.json".format(match_id))
    #
    #         with open(str_file, "w") as f:
    #             # json.dump(data, f, ensure_ascii=False)
    #             f.write(to_json_string(data2))
    #
    #         print(time.time() - t2)
    #
    #     except Exception as e:
    #         print_exception(e)
    #         raise e

    def reduce_state_data(self, data, increment=False):
        try:
            result = []
            d_new = copy.deepcopy(data)
            for index, d in enumerate(d_new):
                d.update(valid_actions=[])
                if increment and index > 0:
                    operators_increase = get_diff_between_operators(d_new[index-1]["operators"], d["operators"])
                    d["operators"] = operators_increase
                result.append(d)
            return result
        except Exception as e:
            print_exception(e)
            raise e

    def save_action_in_local_file(self, match_id, data):
        try:
            # data = self.reduce_state_data(data, increment=True)
            str_file = os.path.join(self.save_file_path, "{}_action.json".format(match_id))

            with open(str_file, "w") as f:
                # json.dump(data, f, ensure_ascii=False)
                f.write(to_json_string(data))
        except Exception as e:
            print_exception(e)
            raise e


def get_diff_between_operators(operators1, operators2):
    try:
        op1_id = [op["obj_id"] for op in operators1]
        op2_id = [op["obj_id"] for op in operators2]

        same_ids = list(set(op2_id) & set(op1_id))
        more_ids = list(set(op2_id) - (set(op2_id) & set(op1_id)))

        result = []

        for t_id in same_ids:
            diff_dict = {"obj_id" : t_id}
            diff_dict.update(get_diff_between_dict(operators1[op1_id.index(t_id)],
                                                     operators2[op2_id.index(t_id)]))

            result.append(diff_dict)
        for t_id in more_ids:
            result.append(operators2[op2_id.index(t_id)])

        return result
    except Exception as e:
        print_exception(e)
        raise e


def get_diff_between_dict(dic_1, dic_2):
    try:
        dic_1 = copy.deepcopy(dic_1)
        dic_2 = copy.deepcopy(dic_2)
        ori_list_keys = []
        ori_dict_keys = []

        for key, value in dic_1.items():
            if isinstance(value, list):
                dic_1[key] = tuple(value)
            if isinstance(value, dict):
                dic_1[key] = str(value)

        for key, value in dic_2.items():
            if isinstance(value, list):
                dic_2[key] = tuple(value)
                ori_list_keys.append(key)
            if isinstance(value, dict):
                dic_2[key] = str(value)
                ori_dict_keys.append(key)

        result = dict(dic_2.items() - (dic_2.items() & dic_1.items()))
        for key in ori_list_keys:
            if key in result.keys():
                result[key] = list(result[key])
        for key in ori_dict_keys:
            if key in result.keys():
                result[key] = eval(result[key])

        return result
    except Exception as e:
        print_exception(e)
        raise e


def t_get_diff_between_operators():
    op1 = [{"obj_id": 0, "color": 0}, {"obj_id": 1, "color": 1}]
    op2 = [{"obj_id": 0, "color": 0}, {"obj_id": 2, "color": 3}]
    diff = get_diff_between_operators(op1, op2)
    print(diff)


if __name__ == "__main__":
    # s1 = json.dumps({"a": 0, "b": 1})
    # l = [s1] * 10
    # saver = Saver()
    # saver.save_player_in_local_file("test", l)
    # t_get_diff_between_operators()
    path = "../../logs/replay/s12281011_3531_0.json"
    with open(path, 'r') as f:
        a = json.load(f)
        print(a[0])