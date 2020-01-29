#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-29 下午2:32
# @Author  : sgr
# @Site    : 
# @File    : data_transfer.py


from common.m_exception import print_exception


def str2int_list(lstr):
    try:
        ilist = []
        if len(lstr.strip()) != 0 and str(lstr) != "nan":
            slist = lstr.split(',')
            for i in range(len(slist)):
                ilist.append(int(slist[i]))
        return ilist
    except Exception as e:
        print_exception(e)
        raise e
