#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-12-4 下午9:39
# @Author  : sgr
# @Site    : 
# @File    : my_numpy.py

import numpy


class MyNumpy(object):
    def __init__(self, np):
        self.np = np
        self.shape = self.np.shape

    def check(self, target):
        if type(target) is numpy.ndarray:
            return MyNumpy(target)
        else:
            return target.item()

    def __getitem__(self, args):
        return self.check(self.np[args])

    def __setitem__(self, key, value):
        self.np[key] = value


if __name__ == "__main__":
    a = MyNumpy(numpy.zeros((300, 500)))
    a[0, 1] = 5
    print(a[0, 1])
    print(a.shape)

    import time

    def count_time(func):
        def int_time(*args, **kwargs):
            start_time = time.time()
            func()
            end_time = time.time()
            print(end_time - start_time)
        return int_time

    @count_time
    def t1():
        b = MyNumpy(numpy.zeros((3000, 5000)))
        for i in range(1000):
            assert (b[0, 0] == 0)


    @count_time
    def t2():
        c = numpy.zeros((3000, 5000))
        for i in range(1000):
            assert (c[0, 0] == 0)

    t1()
    t2()
    print("done")