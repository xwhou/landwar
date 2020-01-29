# -- coding:utf-8 --

"""
    设置一个code最多可以玩MAX_COUNT次，每用一次，就把这个COUNT记录到COUNT_FILE_NAME里
    每次检查，都先读取判断使用次数是否超出MAX_COUNT
    如果在允许范围内，且code正确，则允许使用引擎

    入口函数： check

    测试说明：把MAX_COUNT设置为2， 运行3遍 python come_in.py 看看效果
"""

import time
import base64
import os

dirs = os.path.split(os.path.realpath(__file__))[0]
COUNT_FILE_NAME = os.path.join(dirs, "count.pyc")
MAX_COUNT = 50000


def check(team_name, team_leader_name, code):
    """
    检查team_name和code是否对应， code应该从微信公众号中查询获得
    :param: team_name: 队伍名称
    :param: team_leader_name: 队长名称
    :param: code:  从微信公众号获得的队伍编码
    :return: 如果编码和队伍名称匹配，返回True；否则返回False
    """
    count, count_dict = get_count(COUNT_FILE_NAME, code)
    if count > MAX_COUNT:
        return False
    if encode(team_name, team_leader_name) != code:
        return False
    add_count(COUNT_FILE_NAME, code)
    return True


def file_to_dict(input_file_name):
    result_dict = {}
    if not os.path.exists(input_file_name):
        return result_dict
    with open(input_file_name, 'r', encoding='utf-8') as input_file:
        for line in input_file:
            line = line.strip()
            line_parts = line.split("\t")
            if len(line_parts) < 2:
                continue
            key, value = line_parts[0], int(line_parts[1])
            result_dict[key] = value
    return result_dict


def dict_to_file(input_dict, output_file_name):
    with open(output_file_name, 'w', encoding='utf-8') as output_file:
        for key, value in input_dict.items():
            output_file.write("{}\t{}".format(key, value))


def get_count(count_file_name, code):
    count_dict = file_to_dict(count_file_name)
    count = count_dict.setdefault(code, 1)
    return count, count_dict


def add_count(count_file_name, code):
    count, count_dict = get_count(count_file_name, code)
    count_dict[code] = count + 1
    dict_to_file(count_dict, count_file_name)


# 用team_name和team_leader_name生成一个跟当天时间相关的验证码
def encode(team_name, team_leader_name):
    input = team_name + ":" + time.strftime("%Y|%m|%d", time.localtime()) + ":" + team_leader_name
    code = base64.b64encode(input.encode('utf-8'))
    code = str(code, 'utf-8')
    return code[:6]


if __name__ == "__main__":
    print(check('陆战之王', '李四', '6ZmG5o'))
