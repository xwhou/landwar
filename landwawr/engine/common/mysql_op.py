#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-7-4 下午2:16
# @Author  : sgr
# @Site    : 
# @File    : mysql_op.py


import pymysql

from common.m_exception import print_exception


dic_return_msg = {1: "操作成功", 1001: "数据库已经存在,无需创建", 1002: "表不存在", 1003: "表已经存在，无需创建"}


class MYSQLOperator:
    def __init__(self, host, port, user, pwd, database, charset='utf8'):
        try:
            self.conn = None
            self.host = host
            self.port = port
            self.user = user
            self.pwd = pwd
            self.database = database
            self.charset = charset

            self._check_args()
            self.conn = pymysql.connect(host=host, port=int(port), user=user, password=pwd, database=database,
                                        charset=charset)
            self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
        except Exception as e:
            print_exception(e)
            raise e

    def create_database(self, database, force=False):
        try:
            if self.judge_database_exists(database):
                if force:
                    self.delete_database(database)
                else:
                    return 1001
            sql = "create database {};".format(database)
            self.cursor.execute(sql)
            self.conn.commit()
            return 1
        except Exception as e:
            print_exception(e)
            self.conn.rollback()
            # raise e

    def judge_database_exists(self, database):
        try:
            self.cursor.execute("show databases;")
            data = self._fetch_values()
            return database in data
        except Exception as e:
            print_exception(e)
            raise e

    def delete_database(self, database):
        try:
            self.cursor.execute("drop database if exists {};".format(database))
            return 1
        except Exception as e:
            print_exception(e)
            # raise e

    def create_table(self, table, l_col_infos, force=False):
        """
        创建表
        l_col_infos: [{"name":"test", "type":"int", "length":10, "allow_null": False, "auto_increment":True, "primary_key":True}]
        force: 为True时，若表已经存在，删除原表，重新创建
        :return: 1: 操作成功
        """
        try:
            if self.judge_table_exists(table):
                if force:
                    self.delete_table(table)
                else:
                    return 1003

            sql_col = ""
            for index in range(len(l_col_infos)):
                dic_col_info = l_col_infos[index]
                sql_col += self.explain_dic_col_info(dic_col_info)
                if index != len(l_col_infos) - 1:
                    sql_col += ', '

            sql = "create table {} ({}) ENGINE=InnoDB DEFAULT CHARSET=utf8;".format(table, sql_col)
            self.cursor.execute(sql)
            self.conn.commit()
            return 1
        except Exception as e:
            print_exception(e)
            self.conn.rollback()
            # raise e

    def judge_table_exists(self, table):
        try:
            self.cursor.execute('show tables;')
            data = self._fetch_values()
            return table in data
        except Exception as e:
            print_exception(e)
            raise e

    def delete_table(self, table):
        try:
            self.cursor.execute("drop table if exists {}".format(table))
            self.conn.commit()
            return 1
        except Exception as e:
            print_exception(e)
            self.conn.rollback()
            # raise e

    def add_table_field(self, table, dic_col_info):
        """
        增加表字段
         dic_col_info: {"name":"test", "type":"int", "length":10, "allow_null": False, "auto_increment":True, "primary_key":True}
         todo: 语法cuowu
        :return: 1: 操作成功
        """
        try:
            if not self.judge_table_exists(table):
                return 1002
            str_sql = self.explain_dic_col_info(dic_col_info)
            str_sql = "alter table {} add {};".format(table, str_sql)
            self.cursor.execute(str_sql)
            self.conn.commit()
            return 1
        except Exception as e:
            print_exception(e)
            self.conn.rollback()
            # raise e

    def insert_single(self, table, l_values, l_columns=None):
        """
        插入一行数据
        l_colums 为None， 不指定列。顺序
        :return:
        """
        try:
            if not self.judge_table_exists(table):
                return 1002

            str_values = ""
            if l_values:
                for i in range(len(l_values)):
                    value = l_values[i]
                    str_values += "{}".format(value) if not isinstance(value, str) else "'{}'".format(value)
                    if i != len(l_values) - 1:
                        str_values += ','

            # QUERY
            if l_columns:
                query = 'insert into {} ({}) values ({});'.format(table, ','.join(l_columns), str_values)
            else:
                query = 'insert into {} values ({});'.format(table, str_values)

            self.cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            print_exception(e)
            self.conn.rollback()
            # raise e

    def insert_many(self, table, l_values, l_columns):
        """
        批量插入数据
        :param table:
        :param l_values:
        :param l_columns:
        :return:
        """
        try:
            query = 'insert into {} ({}) values ({})'.format(table, ','.join(l_columns), ("%s,"*len(l_columns))[:-1])
            self.cursor.executemany(query, l_values)
            self.conn.commit()
        except Exception as e:
            print_exception(e)
            self.conn.rollback()
            # raise e

    def update(self, table, dic_key_values, condition=None):
        try:
            str_vs = ""
            for key, value in dic_key_values.items():
                if not isinstance(value, str):
                    str_vs += '{}={},'.format(key, value)
                else:
                    str_vs += '{}="{}",'.format(key, value)

            str_vs = str_vs[:-1]
            query = 'update {} set {}'.format(table, str_vs)
            if condition:
                query = query + " where {}".format(condition)

            self.cursor.execute(query)
            self.conn.commit()

        except Exception as e:
            print_exception(e)
            self.conn.rollback()
            # raise e

    def select(self, table, condition=None):
        """
        :param table:
        :param condition:
        :return: [{}]
        """
        try:
            query = 'select * from {}'.format(table)
            if condition:
                query += " where {}".format(condition)
            self.cursor.execute(query)
            self.conn.commit()
            data = self.cursor.fetchall()
            return data
        except Exception as e:
            print_exception(e)
            self.conn.rollback()
            # raise e

    def delete_rows(self, table, condition=None):
        try:
            query = 'delete from {}'.format(table)
            if condition:
                query += ' where {}'.format(condition)

            self.cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            print_exception(e)
            self.conn.rollback()
            # raise e

    def explain_dic_col_info(self, dic_col_info):
        try:
            sql_col = ""
            sql_col += "{} {}".format(dic_col_info["name"], dic_col_info["type"])

            if "length" in dic_col_info.keys():
                sql_col += "({})".format(dic_col_info["length"])
            elif dic_col_info["type"] == "nvarchar" or dic_col_info["type"] == "varchar":
                sql_col += "({})".format(100)
            if "allow_null" in dic_col_info.keys() and not dic_col_info["allow_null"]:
                sql_col += " not null"
            if "auto_increment" in dic_col_info.keys() and dic_col_info["auto_increment"]:
                sql_col += " auto_increment"
            if "primary_key" in dic_col_info.keys() and dic_col_info["primary_key"]:
                sql_col += " primary key"
            return sql_col
        except Exception as e:
            print_exception(e)
            raise e

    def _check_args(self):
        try:
            assert isinstance(self.host, str), "host must be a string!"
            assert isinstance(self.port, int), "port must be a integer!"
            assert isinstance(self.user, str), "user must be a string!"
            assert isinstance(self.pwd, str), "pwd must be a string!"
        except Exception as e:
            print_exception(e)
            raise e

    def _fetch_values(self):
        try:
            results = self.cursor.fetchall()
            if isinstance(self.cursor, pymysql.cursors.DictCursor):
                data = [value for tp in results for _, value in tp.items()]
            else:
                data = [tp[0] for tp in results]
            return data
        except Exception as e:
            print_exception(e)
            raise e

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        if self.conn:
            self.conn.close()
            self.conn = None


def test_create_db():
    try:
        obj_mysql = MYSQLOperator(host='0.0.0.0', port=3306, user="root", pwd="root", database="mysql")
        print("初始化成功")
        database = "test_db"
        obj_mysql.delete_database(database)
        print("删除数据库{}".format(database))
        obj_mysql.create_database(database)
        print("成功创建数据库{}".format(database))
        print("数据库{} exists:{}".format(database, obj_mysql.judge_database_exists("test_db")))

    except Exception as e:
        print_exception(e)
        raise e


def test_create_table():
    try:
        database = "test_db"
        obj_mysql = MYSQLOperator(host='0.0.0.0', port=3306, user="root", pwd="root", database="test_db")
        print("数据库 {} 连接成功".format(database))
        table = "s1"
        print("表 {} exists:{}".format(table, obj_mysql.judge_table_exists(table)))
        l_col_infos = [{"name": 'ID', "type": "int", "allow_null": True, "auto_increment": True, "primary_key": True},
                       {"name": 'name', "type": "nvarchar", "length": 50, "allow_null": False},
                       {"name": 'time', "type": "datetime"}]
        obj_mysql.create_table(table=table, l_col_infos=l_col_infos, force=True)
        print("成功创建表{}".format(table))
        dic_col_info = {"name": 'code', "type": "nvarchar"}

        obj_mysql.add_table_field(table=table, dic_col_info=dic_col_info)
        print("成功增加新列")
    except Exception as e:
        print_exception(e)
        raise e


def test_change_table():
    import datetime
    try:
        database = "test_db"
        obj_mysql = MYSQLOperator(host='0.0.0.0', port=3306, user="root", pwd="root", database="test_db")
        print("数据库 {} 连接成功".format(database))
        table = "hello"
        print("表 {} exists:{}".format(table, obj_mysql.judge_table_exists("hello")))

        l_cols = ['name', 'time']
        l_values = ['me', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        # obj_mysql.insert_single(table, l_values, l_cols)
        # print("增加数据成功!")

        l_values1 = [l_values] * 3
        # obj_mysql.insert_many(table, l_values1, l_cols)
        # print("插入多条数据成功")

        obj_mysql.update(table, {"name": "him", "time": datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}, condition="name='me'")
        print("update 成功")
    except Exception as e:
        print_exception(e)
        raise e


def test_query_table():
    import pandas
    try:
        database = "test_db"
        obj_mysql = MYSQLOperator(host='0.0.0.0', port=3306, user="root", pwd="root", database="test_db")
        print("数据库 {} 连接成功".format(database))
        table = "hello"
        print("表 {} exists:{}".format(table, obj_mysql.judge_table_exists("hello")))

        results = obj_mysql.select(table)
        print(results)
        print(pandas.DataFrame(list(results)))
        results1 = obj_mysql.select(table, condition='ID=1')
        print(results1)
        print("query 成功")

        obj_mysql.delete_rows(table, condition="name='him'")
        print("删除成功")
        results = obj_mysql.select(table)
        print(results)
        print(pandas.DataFrame(list(results)))
        print()
    except Exception as e:
        print_exception(e)
        raise e


if __name__ == "__main__":
    # test_create_db()
    test_create_table()
    # test_change_table()
    # test_query_table()
