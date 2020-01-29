#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-6-27 上午10:26
# @Author  : sgr
# @Site    : 
# @File    : m_exception.py

import datetime


def echosentence_color(str_sentence = None, color = None):
    try:
        if color is not None:
            list_str_colors = ['darkbrown', 'red', 'green', 'yellow', 'blue', 'purple', 'yank', 'white']
            assert  str_sentence is not None and color in list_str_colors
            id_color = 30 + list_str_colors.index(color)
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print('\33[1;35;{}m'.format(id_color) + now + " " + str_sentence + '\033[0m')
        else:
            print(str_sentence)

    except Exception as e:
        print('error in echosentence_color {}'.format(str(e)))
        raise


def print_exception(e, color='red'):
    echosentence_color('File: ' + e.__traceback__.tb_frame.f_globals['__file__'] + ',  line ' +
                       str(e.__traceback__.tb_lineno) + ': \n\t' + str(e), color=color)


def test():
    try:
        pass
    except Exception as e:
        print_exception(e)
        raise e


if __name__ == "__main__":
    test()