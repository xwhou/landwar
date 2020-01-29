#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-7-5 上午10:31
# @Author  : sgr
# @Site    : 
# @File    : db_operator.py


from common.mysql_op import MYSQLOperator
from common.m_exception import print_exception
from wgconst.const import DBConfig


def prepare_database():
    try:
        obj_db = MYSQLOperator(host=DBConfig.Host,
                                port=int(DBConfig.Port),
                                         user=DBConfig.User,
                                         pwd=DBConfig.Pwd,
                                         database=DBConfig.WarGameDB, charset='utf8')

        l_col_infos = [{'name': 'MatchID', "type": "nvarchar", "length": 100, "allow_null": False},
                       {'name': 'State', "type": "int", "allow_null": False},
                       {'name': 'Scenario', "type": "int"},
                       {'name': 'Mode', "type": "int"},
                       {'name': 'RedUser', "type": "nvarchar", "length": 100},
                       {'name': 'BlueUser', "type": "nvarchar", "length": 100},
                       {'name': 'RoomID', "type": "int"},
                       {'name': 'StartTime', "type": "nvarchar", "length": 100},
                       {'name': 'EndTime', "type": "nvarchar", "length": 100},
                       {'name': 'Engine', "type": "float"}
                       ]

        obj_db.create_table(DBConfig.RoomTable, l_col_infos=l_col_infos, force=True)

        # obj_db.add_table_field(table=DBConfig.RoomTable, dic_col_info=dic_col)

        # obj_db.create_database(DBConfig.ReviewDB)
        obj_db.close()

    except Exception as e:
        print_exception(e)
        raise e


class DBOperator:
    """服务端数据库操作类"""
    def __init__(self):
        try:
            self.host = DBConfig.Host
            self.port = int(DBConfig.Port)
            self.user = DBConfig.User
            self.pwd = DBConfig.Pwd
            self.db_wargame = DBConfig.WarGameDB
            self.db_review = DBConfig.ReviewDB

            self.db_table_room = DBConfig.RoomTable
            self.obj_db_conn = None

        except Exception as e:
            print_exception(e)
            raise e

    def connect_wargame(self):
        try:
            self.obj_db_conn = MYSQLOperator(host=self.host, port=self.port, user=self.user,
                                                       pwd=self.pwd, database=self.db_wargame, charset='utf8')
        except Exception as e:
            print_exception(e)
            raise e

    def connect_review(self):
        try:
            self.obj_db_conn = MYSQLOperator(host=self.host, port=self.port,
                                                       user=self.user, pwd=self.pwd,
                                                       database=self.db_review, charset='utf8')
        except Exception as e:
            print_exception(e)
            raise e

    def insert_room(self, dic_info):
        """
        向Room表中插入一条数据
        :param dic_info: {'MatchID': str,
                        'State': int,
                        'Scenario': int,
                        'MapName': str,
                        'Mode': int,
                        'RedUser': str,
                        'BlueUser': str,
                        'RoomID': int,
                        'StartTime': str,
                        'Engine': int}
        :return:
        """
        try:
            l_cols = list(dic_info.keys())
            l_vals = list(dic_info.values())

            self.obj_db_conn.insert_single(table=self.db_table_room, l_columns=l_cols, l_values=l_vals)
        except Exception as e:
            print_exception(e)
            raise e

    def select_room(self, condition):
        """
        查询
        :param condition:
        :return:
        """
        try:
            return self.obj_db_conn.select(table=self.db_table_room, condition=condition)
        except Exception as e:
            print_exception(e)
            raise e

    def update_room(self, dic_info, match_id):
        """
        更新Room表中指定条目的部分字段
        :param dic_info: {'State': int, 'EndTime': str}
        :param match_id: 指定match_id
        :return:
        """
        try:
            self.obj_db_conn.update(table=self.db_table_room, dic_key_values=dic_info, condition="MatchID='{}'".format(match_id))
        except Exception as e:
            print_exception(e)
            raise e

    def create_match_review_table(self, match_id):
        """创建表名为match_id的存回放数据的表格"""
        try:
            l_col_infos = [{'name': 'ID', 'type': 'int', 'allow_null': False, 'auto_increment': True, "primary_key": True},
                           {'name': 'State', 'type': 'longtext'},
                           ]
            self.obj_db_conn.create_table(table=match_id, l_col_infos=l_col_infos, force=True)
        except Exception as e:
            print_exception(e)
            raise e

    def insert_review_state(self, match_id, l_states):
        """向回放数据表中插入数据"""
        try:
            if l_states:
                self.obj_db_conn.insert_many(table=match_id, l_values=l_states, l_columns=["State"])
        except Exception as e:
            print_exception(e)
            raise e

    def close(self):
        if self.obj_db_conn is not None:
            self.obj_db_conn.close()
            self.obj_db_conn = None


def run():
    import json
    try:
        obj_db = DBOperator()
        # obj_db.connect_wargame()
        # match_id = 'hello_abd'
        # obj_db.insert_room({"MatchID": match_id, "State": 0})
        # obj_db.update_room({'State': 1, 'Scenario': 0}, match_id)
        # obj_db.close()
        obj_db.connect_review()
        match_id = "test"
        obj_db.create_match_review_table(match_id)
        obj_db.insert_review_state(match_id, ["1", "2"])
        obj_db.close()
    except Exception as e:
        print_exception(e)
        raise e


if __name__ == '__main__':
    # prepare_database()
    run()