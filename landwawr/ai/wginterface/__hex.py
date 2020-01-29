# -*- coding: utf-8 -*- 2

############################################
#
# PAL_Wargame
#
# 2017年4月25日/gsliu
#   单位六角格像素信息 HEX_PIXEL类, 统计绘制拼接地图需要的像素尺度上的信息
# 2017年4月27日/gsliu
#   添加偏移坐标与立方坐标 HEX_OFF / HEX_CUBE 类以及常用的坐标转换函数
#
############################################

import numpy as np
import __common as common

####################################
'''偏移坐标六角格类'''


class HEX_OFF:
    row = None
    col = None

    def __init__(self, y, x):
        assert y >= 0 and x >= 0
        self.row = y
        self.col = x

    def __str__(self):
        return ('row = %d, col = %d') % (self.row, self.col)

    '''
    将当前的偏移坐标(Off)转换到立方坐标(Cube)
  '''

    def cvtToCube(self):
        try:
            assert self.col >= 0  and self.row >= 0
            q = self.col - (self.row - (self.row & 1)) // 2
            r = self.row
            s = 0 - q - r
            return HEX_CUBE(q, r, s)
        except Exception as e:
            common.echosentence_color('error in class HEX_OFF cvtToCube():[row:col={}:{}]:{}'.format(self.col, self.row, str(e)))
            raise

    '''
    计算当前坐标在指定方向上的相邻坐标
  '''

    def getSpecifiedNeighFromDirList(self, list_dir_index=None):

        try:
            assert self.col and self.row and len(list_dir_index) <= 6
            list_neigh_loc = []
            ji_flag = self.row % 2 == 1
            list_neighdir_offset = common.list_neighdir_offset_ji if ji_flag else common.list_neighdir_offset_ou
            for dir_index in list_dir_index:
                assert dir_index < 6 and dir_index >= 0
                list_neigh_loc.append(tuple(np.add((self.row, self.col), list_neighdir_offset[dir_index])))
            return list_neigh_loc

        except Exception as e:
            common.echosentence_color('error in class HEX_OFF getSpecifiedNeigh():{}'.format(str(e)))
            raise

    ''' 计算当前坐标下6个方向上的相邻坐标'''
    def getSixNeighInOrder(self):
        try:
            assert self.col and self.row
            list_dir_index = range(6)
            return self.getSpecifiedNeighFromDirList(list_dir_index)
        except Exception as e:
            common.echosentence_color('error in class HEX_OFF getSixNeighInOrder():{}'.format(str(e)))
            raise

####################################

'''立方坐标下的六角格'''


class HEX_CUBE:
    q = None
    r = None
    s = None

    def __init__(self, q, r, s):
        self.q = q
        self.s = s
        self.r = r

    ''' 测试自身的有效性'''

    def isValid(self):
        # return self.q or self.r or self.s
        return True
        # return True

    '''返回内部数据'''

    def getLocDataInTuple(self):
        try:
            assert self.isValid()
            return (self.q, self.r, self.s)
        except Exception as e:
            common.echosentence_color('error in class HEX_CUBE getLocDataInTuple():{}'.format(str(e)))
            raise

    '''转换到偏移坐标'''

    def cvtToOff(self):
        try:
            assert self.isValid()
            col = self.q + (self.r - (self.r & 1)) // 2
            row = self.r
            return HEX_OFF(row, col)
        except Exception as e:
            common.echosentence_color('error in class HEX_CUBE cvtToOff():{}'.format(str(e)))
            raise
        
####################################

    def addOffVec(self, tuple_offvec):
        t_result = tuple([x + y for x,y in zip(self.getLocDataInTuple(), tuple_offvec)])
        return HEX_CUBE(*t_result)


'''立方坐标有关的算法'''

'''计算两个立方坐标下的六角格的距离
   输入： HEX_CUBE 对象2个
   输出： 之间的六角格距离
   方法： 曼哈顿距离的1/2
'''


def getDistanceInCube(hexa, hexb):
    try:
        return sum(abs(a_e - b_e) for a_e, b_e in zip(hexa.getLocDataInTuple(), hexb.getLocDataInTuple())) // 2
    except Exception as e:
        common.echosentence_color('error in getDistanceInCube():{}'.format(str(e)))
        raise


'''计算两个偏移坐标下的距离
   输入： HEX_OFF 对象两个
   输出： 之间的六角格距离
   方法： 内部调用getDistanceInCube()
'''


def getDistanceInOff(hexa, hexb):
    try:
        hexa_cube = hexa.cvtToCube()
        hexb_cube = hexb.cvtToCube()
        return getDistanceInCube(hexa_cube, hexb_cube)
    except Exception as e:
        common.echosentence_color('error in getDistanceInOff():{}'.format(str(e)))
        raise



''' 计算hex_src在hex_des的哪个个方向上
    返回0 - 5, 找不到方向时，返回-1
'''
def getSpecifiedDirection(hex_src, hex_des):
    try:
        final_des2src = -1
        list_neighdir_offset = common.list_neighdir_offset_ji if hex_des.row % 2 == 1 else common.list_neighdir_offset_ou
        for tmp_dir in range(6):
            if tuple(np.add((hex_des.row, hex_des.col), list_neighdir_offset[tmp_dir])) == tuple([hex_src.row, hex_src.col]):
                final_des2src = tmp_dir
                break
        return final_des2src
    except Exception as e:
        common.echosentence_color('error in class HEX_OFF getSpecifiedNeigh()'.format(str(e)))
        raise

# todo 计算两个6位坐标的六角格距离
'''获取两个两个6位坐标的距离'''
def getDisBy2int6loc(int6loc_a, int6loc_b):
    try:
        hex_a_y, hex_a_x = common.cvtInt6loc2HexOffset(int6loc_a)
        hex_a = HEX_OFF(hex_a_y, hex_a_x)
        hex_b_y, hex_b_x = common.cvtInt6loc2HexOffset(int6loc_b)
        hex_b = HEX_OFF(hex_b_y, hex_b_x)
        return getDistanceInOff(hex_a, hex_b)
    except Exception as e:
        raise e

'''获取两个tuple(row,col)类型位置之间的距离'''
def getDisBy2tupleloc(tuple_loc_a, tuple_loc_b):
    hex_a_y, hex_a_x = tuple_loc_a
    hex_a = HEX_OFF(hex_a_y, hex_a_x)
    hex_b_y, hex_b_x = tuple_loc_b
    hex_b = HEX_OFF(hex_b_y, hex_b_x)
    return getDistanceInOff(hex_a, hex_b)

'''
    给定6位坐标，返回所有相邻点6位坐标组成的列表
'''


def getC6NeighborsOfC6(int6loc):
    try:
        hex_a_y, hex_a_x = common.cvtInt6loc2HexOffset(int6loc)
        hex_a = HEX_OFF(hex_a_y, hex_a_x)
        list_neighbors = hex_a.getSixNeighInOrder()
        list_neighbors = [common.cvtHexOffset2Int6loc(row, col) for row, col in list_neighbors]
        return list_neighbors
    except Exception as e:
        common.echosentence_color('error in getNeighborsOfint6loc:{}'.format(str(e)))
        raise e


if __name__ == '__main__':
    pass

