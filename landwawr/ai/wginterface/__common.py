# coding:utf-8

import json
import datetime
import http.client
import __wgobject as wgobject
from sqlalchemy import create_engine
import pandas
from time import sleep
import warnings
warnings.filterwarnings("ignore")


# 全局变量
ji_neigh_offset = [(0, 1), (-1, 1), (-1, 0), (0, -1), (1, 0), (1, 1)]
ou_neigh_offset = [(0, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0)]
list_trans_neigh_edgeloc = [3, 4, 5, 0, 1, 2]
list_neighdir_offset_ji = ji_neigh_offset
list_neighdir_offset_ou = ou_neigh_offset

#todo 加入与FFBT模型相关的宏定义
FFBTMODE_ELELEN = 17 # 表示一种策略需要的元素个数
FFBTMODE_SHOOTING_ROW_A = 0 # 攻击算子的射击位置行索引
FFBTMODE_SHOOTING_COL_A = 1 # 攻击算子的设计位置列索引
FFBTMODE_SHOOTING_LEFTPOWER_A =  2   # 攻击算子移动到射击位置上的剩余机动力量
FFBTMODE_SHOOTING_DAMAGELEVEL_A = 3    # 攻击算子主动攻击造成的战损
FFBTMODE_DEFENSELOC_ROW_A = 4 #攻击算子防御位置的行索引
FFBTMODE_DEFENSELOC_COL_A = 5 #攻击算子防御位置的列索引
FFBTMODE_DEFENSELOC_LEFTPOWER_A = 6 #攻击算子移动到防御位置剩余机动力
FFBTMODE_SHOOTING_ROW_O  = 7 # 目标算子射击（反击）位置的行索引
FFBTMODE_SHOOTING_COL_O  = 8 # 目标算子射击（反击）位置的列索引
FFBTMODE_SHOOTING_LEFTPOWER_O = 9 # 目标算子在射击（反击）位置上的剩余机动力
FFBTMODE_SHOOTING_DAMAGELEVEL_O = 10 # 目标算子在射击（反击）造成的战损索引
FFBTMODE_REWARD = 11 # 本策略攻击算子最终取得的综合战损
FFBTMODE_WEAPENINDEX_A = 12 # 攻击算子射击使用的武器
FFBTMODE_WEAPENINDEX_O = 13 # 目标算子反击使用的武器
FFBTMODE_STRATEGYTYPE = 14 # 记录当前策略类型索引
FFBTMODE_INITLOC_ROW_A = 15 # 攻击算子的初始位置行索引
FFBTMODE_INITLOC_COL_A = 16 # 攻击算子的初始位置列索引

# 常用的坐标转换函数
def cvtInt4loc2Int6loc(int4loc):
    '''转换四位整形坐标int4loc到六位整形坐标int6loc'''
    try:
        assert isinstance(int4loc, int)
        tmp_row, tmp_col = int4loc // 100, int4loc % 100
        return cvtHexOffset2Int6loc(tmp_row, tmp_col)
    except Exception as e:
        echosentence_color('common > cvtInt4loc2Int6loc():{}'.format(str(e)))
        raise

def cvtInt6loc2Int4loc(int6loc):
    '''转换6位坐标int6loc到四位坐标int4loc'''
    try:
        assert isinstance(int6loc, int)
        y , x = cvtInt6loc2HexOffset ( int6loc )
        return y * 100 + x
    except Exception as e:
        echosentence_color('common cvtInt6loc2Int4loc():{}'.format(str(e)))
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
        echosentence_color('common > cvtHexOffset2Int6():{}'.format(str(e)))
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
        echosentence_color('comnon > cvtInt6loc2HexOffset():{}'.format(str(e)))
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
        echosentence_color(('error in common tranlocInto4str():{}'.format(str(e))))
        raise

# 算子列表的筛选，查找，缩减工作: filter(function, list_bops)
def getSpecifiedBopById(list_bops, bop_id):
    '''给定算子ID，从当前敌我算子列表中找出对应的算子, 没有找到返回None；
        filter函数返回的是对象和原始列表中的对象的id相同'''
    try:
        # list_filtered_bops = filter(lambda cur_bop : cur_bop.ObjID == bop_id, list_bops)
        list_filtered_bops = [bop for bop in list_bops if bop_id == bop.ObjID]
        return list_filtered_bops[0] if len(list_filtered_bops) == 1 else None
    except Exception as e:
        echosentence_color('common > getSpecifiedBopById():{}'.format(str(e)))
        raise

def getSpecifiedBopByPos(list_bops, bop_pos, obj_type = -1):
    '''从指定的bop列表list_bops中找出位于指定位置bop_pos与类型obj_type的算子,没有返回None'''
    try:
        # list_filtered_bops = filter ( lambda cur_bop: cur_bop.ObjPos == bop_pos and cur_bop.ObjTypeX == obj_type , list_bops )
        if obj_type == -1: # all types
            list_filtered_bops = [bop for bop in list_bops if bop.ObjPos == bop_pos]
            return None if len(list_filtered_bops) == 0 else list_filtered_bops
        else:
            list_filtered_bops = [bop for bop in list_bops if bop.ObjPos == bop_pos and bop.ObjTypeX == obj_type]
            return list_filtered_bops[0] if len(list_filtered_bops) >= 1 else None
    except Exception as e:
        echosentence_color('common > getCorrespondingBopByPos():{}'.format(str(e)))
        raise

def getSpecifiedBopByIndex(list_bops, index):
    try:
        list_filtered = [bop for bop in list_bops if bop.ObjIndex == index]
        return list_filtered[0] if len(list_filtered) == 1 else None
    except Exception as e:
        echosentence_color('error in __common.py > getSpecifiedBopByIndex():{}'.format(str(e)))
        raise

def getSpecifiedBopByIdentity(list_bops, identity):
    '''从输入列表中找出给定算子唯一标志的算子 GameColor + Army + ObjType, 没有找到返回None'''
    try:
        # list_filtered_bops = filter ( lambda cur_bop: '{}_{}_{}'.format ( cur_bop.GameColor , cur_bop.ObjArmy , cur_bop.ObjType ) == identity , list_bops )
        list_filtered_bops = [bop for bop in list_bops if '{}_{}_{}'.format ( bop.GameColor , bop.ObjArmy , bop.ObjType ) == identity]
        return list_filtered_bops [0] if len ( list_filtered_bops ) == 1 else None
    except Exception as e:
        echosentence_color('common > getSpecifiedBopByIdentity():{}'.format(str(e)))
        raise

# pandas格式的态势数据的算子筛选，查找，缩减工作
def getSerByID(df_objects, objid):
    df_tmponeobject = df_objects.loc[df_objects.ID == objid]
    assert len(df_tmponeobject) == 1
    return df_tmponeobject.iloc[0]

def getBopIdentity(bop):
    return '{}_{}_{}'.format ( bop.GameColor , bop.ObjArmy , bop.ObjType )

def getValidTonggeBops(list_bops):
    '''处于同格状态并且能够还能继续射击的算子'''
    list_filtered_bops = [bop for bop in list_bops if bop.ObjTongge == 1 and bop.ObjTonggeShootCountLeft > 0 and bop.ObjBlood > 0]
    return list_filtered_bops

def getDiffSetForListBops(list_all_bops, list_bops):
    '''计算算子列表的补集'''
    try:
        list_diff_bops = []
        for cur_bop in list_all_bops:
            if not checkBopIsInList(list_bops, cur_bop):
                list_diff_bops.append(cur_bop)
        return list_diff_bops
    except Exception as e:
        echosentence_color('common > getDiffSetForListBops():{}'.format(str(e)))
        raise

def checkBopIsInList(list_bops, bop):
    '''利用算子ID检查算子bop 是否在给定的列表中list_bops中'''
    try:
        found_bop = getSpecifiedBopById(list_bops, bop.ObjID)
        return found_bop is not None
    except Exception as e:
        echosentence_color('common > checkBopIsInList():{}'.format(str(e)))
        raise

def getIndexInSpecifiedList(list_identities, bop):
    '''利用算子的identity找出算子在固定列表中的对应位置, 不存在返回-1'''
    try:
        identity =  '%d_%d_%d' % (bop.GameColor, bop.ObjArmy, bop.ObjType)
        return -1 if identity not in list_identities else list_identities.index(identity)
    except Exception as e:
        echosentence_color('common > getIndexInSpecifiedList():{}'.format(str(e)))
        raise

def removeZeorBloodBops (list_bops ):
    '''去掉算子列表中血量<=0的算子, 返回筛选后的算子列表'''
    try:
        # return filter(lambda bop: bop.ObjBlood > 0 , list_bops)
        return [bop for bop in list_bops if bop.ObjBlood > 0]
    except Exception as e:
        echosentence_color('common > removeZeorBloodBops():{}'.format(str(e)))
        raise

def removeZeorBloodBopsPlus(list_bops ):
    '''去掉算子列表中血量<=0的算子, 返回筛选后的算子列表和被移除的算子列表'''
    try:
        list_alive = []
        list_die = []
        for bop in list_bops:
            if bop.ObjBlood > 0:
                list_alive.append(bop)
            else:
                list_die.append(bop)
        return list_alive, list_die
    except Exception as e:
        echosentence_color('common > removeZeorBloodBopsPlus():{}'.format(str(e)))
        raise
    
def removeZeroShootCountBops(list_bops):
    return [bop for bop in list_bops if bop.ObjTonggeShootCountLeft > 0]
    
def getSpecifiedTaskFlag(cur_bop, dic_identity2flagmovings):
    '''算子identity ==> 算子的flag_moving'''
    try:
        str_identykey = '%d_%d_%d' % (cur_bop.GameColor, cur_bop.ObjArmy, cur_bop.ObjType)
        assert (str_identykey in dic_identity2flagmovings.keys())
        return dic_identity2flagmovings[str_identykey]
    except Exception as e:
        echosentence_color('common > getSpecifiedTaskFlag():{}'.format( str( e ) ))
        raise

# 态势分析的公共函数
# 获取算子的中心位置
def getBopCenterLocs(l_bops):
    tuple_centers = (-1,-1)
    sum_rows, sum_cols = 0, 0
    if l_bops:
        for bop in l_bops:
            cur_row, cur_col = cvtInt6loc2HexOffset(bop.ObjPos)
            sum_rows += cur_row
            sum_cols += cur_col
        tuple_centers = (sum_rows//len(l_bops), sum_cols//len(l_bops))
    return  tuple_centers

# def getUniformTaskFlag(dic_identity2flagtasks):
#     '''检查并确认当前的任务'''
#     try:
#         list_taskflags = []
#         for key, value  in dic_identity2flagtasks.items():
#             list_taskflags.append(value)
#         assert  len(list_taskflags) > 0
#         if float(sum(list_taskflags)) / len(list_taskflags) == float(list_taskflags[0]):
#             return list_taskflags[0]
#         return -1
#     except Exception as e:
#         echosentence_color('PreKnow > getUniformTaskFlag():{}'.format(str(e)))
#         raise

# 取相对偏移量，输入参数为方向，距离 ==> 输出立方坐标系统下所有符合要求的偏移向量列表

list_dir2cubeoff = [[1,0,-1], [1,-1,0],[0,-1,1],[-1,0,1],[-1,1,0],[0,1,-1]]

def getDirOffVectorList(dir, dis):
    try:
        assert  dir in range(6) and dis > 0
        list_result = []
        sameloc = dir % 3
        varyloc = (sameloc + 1) % 3
        hastovaryloc = (sameloc + 2) % 3
        varyIncre = -1 if dir % 2 == 0  else 1
        for dis_index in range(1, dis+1):
            base_cur  = [x * dis_index for x in list_dir2cubeoff[dir]]
            # base_next = [x * dis_index for x in list_dir2cubeoff[(dir + 1) % 6]]
            list_result.append(base_cur)
            for i in range(1, dis_index):
                list_tmp_vec = [0] * 3
                list_tmp_vec[sameloc] = base_cur[sameloc]
                list_tmp_vec[varyloc] = base_cur[varyloc] + varyIncre * i
                list_tmp_vec[hastovaryloc] = 0 - list_tmp_vec[sameloc] - list_tmp_vec[varyloc]
                list_result.append(list_tmp_vec)
        return list_result
    except Exception as e:
        echosentence_color('common > getDirOffVectorList():{}'.format(str(e)))
        raise e

def writelist2(list2_eles, filename):
    with open(filename, 'w') as file:
        for list_eles in list2_eles:
            file.writelines(["{}\t".format(item)  for item in list_eles])
            # file.writelines(["{}\t".format(item)  for item in list_eles])
            file.write('\n')

def readlist( filename):
    list2_eles =  []
    with open(filename, 'r') as file:
        list2_streles = file.readlines()
        for str_list in list2_streles:
            list_ele = [float(ele) for ele in str_list.strip('\n').strip('\t').split('\t')]
            list2_eles.append(list_ele)
    return list2_eles

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

# 支持快速推演的公共函数
def getSDDataInfosList(dic_metadata):
    '''打印所有的数据信息'''
    list_str_sdinfos = []
    try:
        # 算子数据
        list_o_bops = dic_metadata['l_rbops'] + dic_metadata['l_bbops']
        list_p_bops = [bop for bop in dic_metadata['l_pbops']]
        list_str_sdinfos.append(u'自由算子')
        for bop in list_o_bops:
            # common.echosentence_color(wgobject.getKeyBopInfo(bop))
            list_str_sdinfos.append('\t' + wgobject.getKeyBopInfo(bop))
        if len(list_p_bops) > 0:
            # common.echosentence_color('Bops[in car] ')
            list_str_sdinfos.append(u'乘车步兵')
            for bop in list_p_bops:
                # common.echosentence_color(wgobject.getKeyBopInfo(bop))
                list_str_sdinfos.append('\t' + wgobject.getKeyBopInfo(bop))
        # 城市信息
        list_str_sdinfos.append(u'城市信息')
        list_citycolor = [u'绿色',u'红色',u'蓝色']
        for index in range(len(dic_metadata['l_cities'])//3):
            str_city = u'城市{}: 位置:{}; 颜色:{}'.format(index,
                                                    str(cvtInt6loc2HexOffset(dic_metadata['l_cities'][index * 3])),
                                                    list_citycolor[dic_metadata['l_cities'][index * 3 + 1]+1]
                                                    )
            list_str_sdinfos.append('\t' + str_city)
    
        return list_str_sdinfos
    except Exception as e:
        echosentence_color('error in __common.py > getSDDataInfosList():{}'.format(str(e)))
        return []

def to_json_string(json_object):
    return json.dumps(json_object, default=lambda obj:obj.__dict__, ensure_ascii=False, indent=4)

# 态势分析的公共函数
# 获取算子的中心位置
def getCenterLocs(l_bops):
    tuple_centers = (-1,-1)
    sum_rows, sum_cols = 0, 0
    if l_bops:
        for bop in l_bops:
            cur_row, cur_col = cvtInt6loc2HexOffset(bop.ObjPos)
            sum_rows += cur_row
            sum_cols += cur_col
        tuple_centers = (sum_rows//len(l_bops), sum_cols//len(l_bops))
    return  tuple_centers

def getCenterInt6Locs(l_bops):
    try:
        t_centerlocs = getBopCenterLocs(l_bops)
        if t_centerlocs == (-1, -1):
            return -1
        else:
            return cvtHexOffset2Int6loc(t_centerlocs[0], t_centerlocs[1])
    except Exception as e:
        echosentence_color('__common.py > getCenterInt6Locs()'.format(str(e)))
        raise e

import math
# todo 计算视线方向(按照六角格的方向标准)
def com_attackdir(att_int4loc, obj_int4loc):
    # 从攻击位置att_int4loc到目标位置obj_int4loc的视线最先打到目标六角格的那个方向
    try:
        att_y, att_x = att_int4loc//100, att_int4loc % 100
        obj_y, obj_x = obj_int4loc // 100, obj_int4loc %100
        # assert att_y >= 0 and att_y < 66
        # assert obj_y >= 0 and obj_y < 66
        # assert att_x >= 0 and att_x < 51
        # assert obj_x >= 0 and obj_x < 51
        # 计算目标算子到攻击算子的方向
        angle = math.atan2(-1 * (att_y-obj_y), att_x-obj_x)
        angle = 180*angle/math.pi
        if angle >= -150 and angle < -90:
            hex_dir = 4
        elif angle >= -90 and angle < -30:
            hex_dir = 5
        elif angle >= -30 and angle < 30:
            hex_dir = 0
        elif angle >= 30 and angle < 90:
            hex_dir = 1
        elif angle >= 90 and angle < 150:
            hex_dir = 2
        else:hex_dir = 3
        return hex_dir
    except Exception as e:
        echosentence_color('__common.py > com_attackdir():{}'.format(str(e)))
        return 0

def getNeighborHexdir(hex_dir):
    '''获取当前方向的相临方向. 返回列表'''
    try:
        assert hex_dir in range(6)
        list_nei_hexdirs = [hex_dir, hex_dir-1, hex_dir+1]
        for index, t_hex_dir in enumerate(list_nei_hexdirs):
            list_nei_hexdirs[index] = 0 if list_nei_hexdirs[index] == 6 else list_nei_hexdirs[index]
            list_nei_hexdirs[index] = 5 if list_nei_hexdirs[index] == -1 else list_nei_hexdirs[index]
            assert list_nei_hexdirs[index] in range(6)
        return list_nei_hexdirs
    except Exception as e:
        echosentence_color('__common.py > getNeighborHexdir():{}'.format(str(e)))
        return 0

class ymdTime:
    def __init__(self,year = 0,month = 0,day = 0):
        self.year = year
        self.month = month
        self.day = day

def str2time(strtime):
    try:
        # 一月 Jan，二月 Feb，三月 Mar，四月 Apr，五月May，六月June，七月July，八月Aug，九月Sept，十月Oct，十一月Nov，十二月Dec
        dict_mon2num = {'Jan':1,'Feb':2,'Mar':3,'Apr':4, 'May':5, 'June':6,'July':7,'Aug':8,'Sept':9,'Oct':10,'Nov':11,'Dec':12}
        l_time = strtime.split(' ')
        obj_ymdtime = ymdTime()
        obj_ymdtime.year = int(l_time[3])
        obj_ymdtime.month = dict_mon2num[l_time[2]]
        obj_ymdtime.day = int(l_time[1])
        return obj_ymdtime
    except Exception as e:
        print('error in str2time -> {}'.format(str(e)))
        raise e

# todo 时间校验功能
def get_jb_time():
    flag_ok, obj_dt_bjtime = False, None
    try:
        conn = http.client.HTTPConnection("www.beijing-time.org")
        conn.request("GET", "/time.asp")
        response = conn.getresponse()
        assert response.status == 200
        str_bjtime = dict(response.getheaders())['Date']
        obj_ymdtime = str2time(str_bjtime)
        obj_dt_bjtime = datetime.datetime(obj_ymdtime.year,obj_ymdtime.month,obj_ymdtime.day,1,1,1)
        flag_ok=True
        conn.close()
    except Exception as e:
        # print('wrong in __common.py get_jb_time')
        pass
    return flag_ok, obj_dt_bjtime

def get_db_emti():
    try:
        str_wg_u = 'wargamesa'
        str_wg_p = 'TZdKB8iBz6Hlu'
        str_ip = '140.143.47.211'
        str_port = '1433'
        str_driver = '?driver=FreeTDS'
        engine = create_engine('mssql+pyodbc://' + str_wg_u + ":" + str_wg_p + '@' + str_ip + ':{}/'.format(str_port) + 'SCORE' + str_driver)
        database_cnn = engine.connect()
        data = pandas.read_sql("select top 1 GETDATE() from [WARGAME].[dbo].[ROOM]", database_cnn)
        str_curtime = str(data.ix[[0]].values[0][0])
        str_curtime = str_curtime[0: str_curtime.find('.')]
        str_curtime = str(str_curtime)
        list_es = str_curtime.split('T')
        list_es = list_es[0]
        list_es = list_es.split('-')
        list_es = [int(x) for x in list_es]
        assert(len(list_es) == 3)
        obj_cur_datetime = datetime.datetime(list_es[0], list_es[1], list_es[2])
        return True, obj_cur_datetime
    except Exception as e:
        return False, None

def dbus_gsliu_time_my_hashUYBC():
    try:
        obj_dt_baseline = datetime.datetime(2018, 12, 1, 1, 1, 1)
        flag_count = 3
        flag_valid, obj_dt_bjtime = get_jb_time()
        while (not flag_valid) and flag_count > 0 :
            flag_valid, obj_dt_bjtime = get_db_emti()
            flag_count -= 1
            sleep(1)
        return flag_valid if not flag_valid else (abs((obj_dt_bjtime - obj_dt_baseline).days) < 20 )
    except Exception as  e:
        return False
    except KeyboardInterrupt as k:
        return False
    
def soft_lowpro():
    import random
    return random.random() > 1

def soft_highpro():
    import random
    return random.random() > 0.1

global version_
version_='72c5c69701a295444311926a01494345dbae23d8'
if __name__ == "__main__":
    # print getDirOffVectorList(dir= 3, dis= 3)
    while(1):
        print(dbus_gsliu_time_my_hashUYBC())
        sleep(1)
