"""
    0:83, # 城镇   czjmd
    1:19, # 山地    gytd
    2:86, # 山岳    sycl
    3:43, # 水网    swdt
    4:84, # 中等    zdqfd
    5:82, # 岛上台地 dstd
"""
"""
dic_xd2elequa = {
    83: 10,
    19: 20,
    86: 10,
    43: 10,
    84: 10,
    82: 20,
}

ji_neigh_offset = [(0, 1), (-1, 1), (-1, 0), (0, -1), (1, 0), (1, 1)]
ou_neigh_offset = [(0, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0)]
list_trans_neigh_edgeloc = [3, 4, 5, 0, 1, 2]
list_neighdir_offset_ji = ji_neigh_offset
list_neighdir_offset_ou = ou_neigh_offset
"""


def cvtInt4loc2Int6loc(int4loc):       #int4loc的取值范围?????
    '''转换四位整形坐标int4loc到六位整形坐标int6loc'''
    try:
        assert isinstance(int4loc, int)
        tmp_row, tmp_col = int4loc // 100, int4loc % 100
        return cvtHexOffset2Int6loc(tmp_row, tmp_col)
    except Exception as e:
        #echosentence_color('common > cvtInt4loc2Int6loc():{}'.format(str(e)))
        raise

def cvtInt6loc2Int4loc(int6loc):
    '''转换6位坐标int6loc到四位坐标int4loc'''
    try:
        assert isinstance(int6loc, int)
        y , x = cvtInt6loc2HexOffset ( int6loc )
        return y * 100 + x
    except Exception as e:
        #echosentence_color('common cvtInt6loc2Int4loc():{}'.format(str(e)))
        raise

def cvtHexOffset2Int6loc(row, col):
    '''转换（row,col）到6位整型坐标'''
    try:
        if row % 2 == 1:
            tmpfirst = (row - 1) // 2
            tmplast = col * 2 + 1
        else:
            tmpfirst = row // 2
            tmplast = col * 2
        assert (tmpfirst >= 0 and tmplast >= 0)
        return int(tmpfirst * 10000 + tmplast)
    except Exception as e:
        #echosentence_color('common > cvtHexOffset2Int6():{}'.format(str(e)))
        raise

def cvtInt6loc2HexOffset(int6loc):
    '''转换6位整形坐标int6loc转换为偏移坐标（y,x）2元组'''
    try:
        str6loc = str(int6loc)
        len_oristr6loc = len(str6loc)
        assert (len_oristr6loc <= 6)
        if len_oristr6loc < 6:
            str6loc = '0' * (6 - len_oristr6loc) + str6loc

        int_first_2, int_last_3 = int(str6loc[0:2]), int(str6loc[3:])
        if int_last_3 % 2 == 1:
            row , col = int_first_2 * 2 + 1 , (int_last_3 - 1) // 2
        else:
            row , col = int_first_2 * 2 , int_last_3 // 2
        return (row,col)
    except Exception as e:
        #echosentence_color('comnon > cvtInt6loc2HexOffset():{}'.format(str(e)))
        raise

def tranlocInto4Str(y, x):
    '''将两个偏移整形坐标拼接成为四位字符串'''
    try:
        assert(x >=0 and x < 100 and y >=0 and y < 100)
        re = ''
        re += str(y) if y >= 10 else str(0) + str(y)
        re += str(x) if x >= 10 else str(0) + str(x)
        return re
    except Exception as e:
        #echosentence_color(('error in common tranlocInto4str():{}'.format(str(e))))
        raise