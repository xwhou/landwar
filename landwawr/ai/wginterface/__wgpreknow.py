# coding:utf-8

'''
2017年8月27日/gsliu/PAL_Wargame
文件说明：封装先验数据
    2017年8月27日：建立文档, 确定各种预定义的参数!
    2018年1月27日: 各个想定的编号
        0:全国赛区AI表演赛（城镇居民地）
        1 / 2:南通赛军队组预选赛想定1，2（城镇居民地）
        3:南通赛军队组预选赛想定3（城镇居民地）
        4:全国赛北京赛区（岛上台地）
        5:南通赛AI表演赛（人机对抗想定：水网稻田）
        6:南通赛AI表演赛（机机对抗想定：水网稻田 , 暂时没有用到）
'''

import random,copy
import __common as common
import math
import pandas

''' 全局变量：想定编号 ==> ../../interface/DataForAi/子文件夹名称的映射关系 '''
dic_xd2name = {83:'czjmd',
               19:'gytd',
               86:'sycl',
               43:'swdt',
               84:'zdqfd',
               82:'dstd'
               }
'''全局变量：想定编号==>算子identities'''
dic_xd2tuple_rbids = {83:(['_111_2' , '_112_2' , '_121_1' , '_121_2' , '_122_1' , '_122_2'],
                         ['_111_2' , '_112_2' , '_121_1' , '_121_2' , '_122_1' , '_122_2']),
                      19:(['_111_2' , '_112_2' , '_121_2' , '_121_1' , '_122_1' , '_122_2'], # 红方第一辆人车的顺序是先车后人
                         ['_111_2' , '_112_2' , '_121_1' , '_121_2' , '_122_1' , '_122_2']),
                      86:(['_111_2' , '_112_2' , '_121_1' , '_121_2' , '_122_1' , '_122_2'],
                         ['_111_2' , '_112_2' , '_121_1' , '_121_2' , '_122_1' , '_122_2']),
                      43:(['_111_2' , '_112_2' , '_121_1' , '_121_2' , '_122_1' , '_122_2'],
                         ['_111_2' , '_112_2' , '_121_1' , '_121_2' , '_122_1' , '_122_2']),
                      84: (['_111_2', '_112_2', '_121_2', '_123_1', '_124_1', '_122_2'],
                          ['_111_2', '_112_2', '_122_1', '_122_2', '_123_1', '_123_2']),
                      82: (['_111_2', '_112_2', '_121_1', '_121_2', '_122_1', '_122_2'],
                          ['_111_2', '_112_2', '_121_1', '_121_2', '_122_1', '_122_2']),
                      }
'''全局变量：想定编号==>每个想定的算子总数量(区分红方和蓝方)'''
dic_r_xd2opnum = {83: 6, 19:6, 86: 6, 43: 6, 84: 6, 82:6}
dic_b_xd2opnum = {83: 6, 19:6, 86: 6, 43: 6, 84: 6, 82:6}
'''全局变量：想定编号==>每个想定的预定义路线的数量(区分红方和蓝方)'''
dic_r_xd2strategynum = {0: 4, 1: 3, 2: 5, 3: 4, 4: 3, 5:3}
dic_b_xd2strategynum = {0: 4, 1: 2, 2: 4, 3: 4, 4: 3, 5:4}
'''全局变量：想定编号 ==> 危险点列表(不区分红方和蓝方)'''
dic_xd2listdangerlocs= {0:[90041 + x * 2  for x in [0,1,2,3,4,5,8]] + [100042 + x * 2 for x in range(8)], # 保留90053, 90055两个点
                        1:[10002],
                        2:[10002],
                        3:[10002],
                        4:[10002],
                        5:[10002],
                        }
'''确定每个想定的主要战场区域'''
dic_xd2warzoneloc = {0:[80048, 100049],
                     1:[80062, 100060],
                     2:[150049, 130046],
                     3:[220048, 230052],
                     4:[210056, 180055],
                     5:[120057, 120051],
                     }

'''全局变量：前多少个阶段完全按照预定义路线机动，区分红方和蓝方: 只针对坦克'''
dic_r_xd2fixedRouteStage = {0: 8, 1: 8, 2: 8, 3: 8, 4:8, 5:8}
dic_b_xd2fixedRouteStage = {0: 8, 1: 8, 2: 8, 3: 8, 4:8, 5:8}
'''全局变量：红方算子和蓝方算子的固定下车位置（规则，载人战车在这些位置上一定会下人，区分红方和蓝方）'''
# dic_r_xd2listgetofflocs = {0: [80042 , 110044, 70037, 80048], # 1621, 2222, 1518, 1624
#                        1: [80062, 100060],
#                        2: [150049, 130046],
#                        3: [220048, 230052],
#                        4: [210056, 180055],
#                        5: [120057, 120051],
#
#                        }
# dic_b_xd2listgetofflocs = {0: [80053, 80054 , 80055, 100055, 100057, 100059], # 1726, 1627, 1727, 2127, 2128, 2129
#                        1: [80062, 100060],
#                        2: [150049, 130046],
#                        3: [220048, 230052],
#                        4: [210056, 180055],
#                        5: [120057, 120051],
#                        }
dic_r_xd2listgetofflocs = {0: [80042, 110044, 70037, 80048],  # 1621, 2222, 1518, 1624
                           1: [80062, 100060, 100057, 80057],  # [2128, 1728]
                           2: [150049, 130046, 130038, 150043, 150040],  # [2619, 3121, 3020]
                           3: [220048, 230052, 220046, 210049, 210048, 220042],  # 4423, 4324, 4224, 4421
                           4: [210056, 180055, 200053, 210052, 230037, 190043, 210047],
                           # 夺控点+[4126, 4226, 4718, 3921, 4323]
                           5: [120057, 120051, 130046, 130072, 150052],  # [2623, 2636, 3026]
                           }
dic_b_xd2listgetofflocs = {0: [80053, 80054, 80055, 100055, 100057, 100059],  # 1726, 1627, 1727, 2127, 2128, 2129
                           1: [80062, 100060, 110062, 90062, 120057, 120059],  # 2231, 1831, 2528, 2529
                           2: [150049, 130046, 150055, 160061],  # [3127, 3330]
                           3: [220048, 230052, 220055, 220057, 220060],  # 4527, 4528, 4430
                           4: [210056, 180055, 200060, 210064],  # 夺控点+[4030 4232]
                           5: [120057, 120051, 140058, 120047, 120062],  # 2829, 2523, 2431
                           }
'''全局变量：粘滞点列表（规则，算子死守这些点，区分红蓝方）'''
dic_r_xd2listviscouslocs = {0:[80048, 100049],
                            1:[80062, 100060],
                            2:[150049, 130046],
                            3:[220048, 230052],
                            4:[210056, 180055],
                            5:[120057, 120051],
                            }
dic_b_xd2listviscouslocs = {0:[80048, 100049],
                            1:[80062, 100060],
                            2:[150049, 130046],
                            3:[220048, 230052],
                            4:[210056, 180055],
                            5:[120057, 120051],
                            }
'''全局变量：QD模式下加载算子 想定编号==> 房间号码'''
dic_xd2roomid = {0: 1001, 1: 1002, 2: 1003, 3: 1004, 4: 1001,5:1006 }
'''全局变量，夺控点的信息: （位置，颜色，分数，需要从数据库中获取） '''
dic_xd2cityinfos = {
    83:[80048, -1, 80, 100049, -1, 50],
    19:[100060, -1, 80, 80062, -1, 50],
    86:[150049, -1, 80, 130046, -1, 50],
    43:[220048, -1, 80, 230052, -1, 50],
    84:[210056, -1, 80, 180055, -1, 50],
    82:[120057, -1, 80, 120051, -1, 50],

}
'''全局变量，定义红方和蓝方的进攻方向【方向编码按照六角格的方向定义， 范围[0-5]】'''
dic_r_xd2attackdir={0:3, 1:3, 2:3, 3:3, 4:3, 5:3}
dic_b_xd2attackdir={0:0, 1:0, 2:0, 3:0, 4:0, 5:0}

#sgr添加
''' 全局变量，夺控点的信息: （位置，颜色，分数，需要从数据库中获取） '''
dic_xd2cityname = {
    0:['主要', '次要'],
    1:['主要', '次要'],
    2:['主要', '次要'],
    3:['主要', '次要'],
    4:['主要', '次要'],
    5:['主要', '次要'],
}

dic_cityflag2str = {'-1':'GREEN','0':'RED','1':'BLUE'}
'''全局变量：不同想定的地图大小num_xd ==> (rows , cols): 修改地图大小和量化等级，需要重新编译.so文件。'''
dic_xd2mapsize = {
    82: (64, 51),
    83: (66, 51),
    19: (70, 66),
    43: (60, 58),
    86: (64, 51),
    84: (64, 51)
}

'''全局变量：不同想定的高程量化等级'''
dic_xd2elequa = {
    83: 10,
    19: 20,
    86: 10,
    43: 10,
    84: 10,
    82: 20
}
'''全局变量：不同想定所使用的地图编号'''
dic_xd2mapid = {
    0:83, # 城镇
    1:19, # 山地
    2:86, # 山岳
    3:43, # 水网
    4:84, # 中等
    5:82, # 岛上台地
}
dic_sen2mapid = {
    1531:83,
    3531:83,
    1631:82,
    3631:82,
    1231:19,
    3231:19
}
'''全局变量：不同想定使用的地图中心坐标'''
dic_xd2scoreId = {0:80048,1:100060,2:150049,3:220048,4:210056,5:120057}
'''全局变量,不同想定地图染色方案'''
dic_xd2cssFile = {0:u'09',1:u'02',2:u'10',3:u'10',4:u'09',5:u'02'}
'''全局变量,不同想定地图最低高程'''
dic_xd2eleLow = {0:90,1:4000,2:0,3:80,4:1040,5:0}
def genCityNames(num_xd):
    assert num_xd in list(dic_xd2cityname.keys())
    return dic_xd2cityname[num_xd]

def genListIdentities(num_xd):
    '''生成红蓝双方的identities list'''
    assert  num_xd in list(dic_xd2tuple_rbids)
    list_identities_r,list_identities_b = dic_xd2tuple_rbids[num_xd]
    assert len(list_identities_r) == dic_r_xd2opnum[num_xd] and len(list_identities_b) == dic_b_xd2opnum[num_xd]
    return (['0{}'.format(x) for x in list_identities_r] , ['1{}'.format(x) for x in list_identities_b])

def genOperatorNum(num_xd, flag_color):
    '''返回指定想定编号下的算子数目'''
    dic_xd2opnum = dic_r_xd2opnum if flag_color == 0 else dic_b_xd2opnum
    assert  num_xd in list(dic_xd2opnum)
    return dic_xd2opnum[num_xd]

def genCityInfos(num_xd):
    '''modify : 2018年10月26日 宋国瑞 返回拷贝的字典，以免值被改变'''
    assert num_xd in list(dic_xd2cityinfos.keys())
    return copy.deepcopy(dic_xd2cityinfos[num_xd])

def genRandomStatagyId(num_xd, flag_color):
    '''随机选择开局路线 dic_xd2strategynum: 想定编号==>人工策略数目 '''
    dic_xd2strategynum = dic_r_xd2strategynum if flag_color == 0 else dic_b_xd2strategynum
    assert num_xd in list(dic_xd2strategynum)
    return random.randint( 0 , dic_xd2strategynum[num_xd] - 1 )

def genDangerLocs(num_xd):
    '''生成不同想定的危险点序列(6位数坐标)
    modify: 2018年10月26日 宋国瑞 返回拷贝
    '''
    assert num_xd in list(dic_xd2listdangerlocs)
    return copy.deepcopy(dic_xd2listdangerlocs[num_xd])

def genDicXD2RouteStage():
    '''红方与蓝方在前多少个阶段(人车)完全按照关键点行走'''
    return (dic_r_xd2fixedRouteStage, dic_b_xd2fixedRouteStage)

def genGetOffLocs(num_xd, flag_color):
    '''预定义的下车位置
    modify: 2018年10月26日 宋国瑞 返回拷贝
    '''
    dic_xd2listgetofflocs = dic_r_xd2listgetofflocs if flag_color == 0 else dic_b_xd2listgetofflocs
    assert num_xd in list(dic_xd2listgetofflocs)
    return copy.deepcopy(dic_xd2listgetofflocs[num_xd])

def genViscousLocs(num_xd, flag_color):
    '''粘滞点（人员算子死守在这些位置点进行机会射击）
    modify: 2018年10月26日 宋国瑞 返回拷贝
    '''
    dic_xd2listviscouslocs = dic_r_xd2listviscouslocs if flag_color == 0 else dic_b_xd2listviscouslocs
    assert num_xd in list(dic_xd2listviscouslocs)
    return copy.deepcopy(dic_xd2listviscouslocs[num_xd])

def genDefaultRoomid(num_xd):
    '''根据想定编号num_xd,获取默认房间号roomid, 用于QD模式下加载算子'''
    try:
        assert  num_xd in list(dic_xd2roomid)
        return dic_xd2roomid[num_xd]
    except Exception as e:
        common.echosentence_color('wargamesituationdata > genDefaultRoomid:{}'.format ( str ( e ) ))
        raise

def genObjectsIndexDict(num_xd):
    l_r_ids, l_b_ids = genListIdentities(num_xd)
    dic_r_iden2index, dic_b_iden2index = dict(zip(l_r_ids, range(len(l_r_ids)))), dict(
        zip(l_b_ids, range(len(l_b_ids))))
    return dic_r_iden2index, dic_b_iden2index

def genDicParas(ip = None, roomid = None , num_xd = None , mapname = None, str_global_flag = None, flag_qd_rm = True, flag_action_cache= False, flag_cache = False, flag_gpu=False ,flag_dllnum= 0, flag_savestate = False, str_wgrootdir = None):
    '''生成参数字典：
        BUG0： 想定num_xd与参数mapname需要配对【1/2/3:南通赛预选赛 czjmd_nt】【4:全国赛 dstd】【5/6：南通赛表演赛 swdt】
    '''
    try:
        # assert (None not in [num_xd, strategy_ids, mapname])
        assert str_global_flag in ['AC', 'QD']
        # assert mapname.__contains__( 'czjmd' ) or mapname.__contains__( 'swdt' )
        max_y_hexnum, max_x_hexnum = dic_xd2mapsize[num_xd]
        str_public_dir = '{}ai/wginterface/DataForAi/public/'.format(str_wgrootdir)
        str_data4ai_dir = '{}ai/wginterface/DataForAi/'.format(str_wgrootdir)
        # str_stagekeyloc_file = str_data4ai_dir + mapname + '/clusters_keylocs_{}.xls'.format('none')
        str_logs_dir = '{}/logs/'.format(str_wgrootdir)
        l_r_ids , l_b_ids = genListIdentities( num_xd )
        dic_r_iden2index, dic_b_iden2index = genObjectsIndexDict(num_xd)
        return { 'ip': ip ,
                 'roomid': roomid ,
                 'num_xd': num_xd ,
                 # 'strategy_id_r': strategy_ids[0] if strategy_ids[0] in range(dic_r_xd2strategynum[num_xd]) else random.choice(range(dic_r_xd2strategynum[num_xd])),
                 # 'strategy_id_b': strategy_ids[1] if strategy_ids[1] in range(dic_b_xd2strategynum[num_xd]) else random.choice(range(dic_b_xd2strategynum[num_xd])),
                 'mapname': mapname ,
                 'username':'Noneusername', 'passwd': 'Nonepasswd',
                 'str_global_flag' : str_global_flag,
                 'list_g_fullstage': [5 , 4 , 5],
                 'ele_qua':dic_xd2elequa[num_xd],
                 'flag_qd_rm': flag_qd_rm,
                 'max_y_hexnum': max_y_hexnum,'max_x_hexnum':max_x_hexnum,
                 'str_hexlabelxls': str_public_dir +'labelled_hexs.xls' ,
                 'str_wgrootdir':str_wgrootdir,
                 'str_logfiles':'{}/logfile_{}.txt'.format(str_logs_dir, roomid),
                 'str_cModuleDir':str_data4ai_dir+mapname+'/',
                 'str_file_zm2cartable': str_public_dir +'damageleveltable_zm2car' ,
                 'str_file_ltf2cartable': str_public_dir +'damageleveltable_ltf2car' ,
                 'str_file_allw2peopletable': str_public_dir +'damageleveltable_allw2people' ,
                 'str_wptable_file': str_public_dir +'wp_table_{}.txt'.format ( 0 ) ,
                 'str_elerect_file': str_public_dir +'elerecttable.txt' ,
                 'str_zm2car_0': str_public_dir +'zm2car_0_forPythonJuder' ,
                 'str_zm2car_1': str_public_dir +'zm2car_1_forPythonJuder' ,
                 'str_zm2car_2': str_public_dir +'zm2car_2_forPythonJuder' ,
                 'str_anywp2peo_0': str_public_dir +'anyweapen2people_0_forPythonJuder' ,
                 'str_anywp2peo_1': str_public_dir +'anyweapen2people_1_forPythonJuder' ,
                 'str_wargame_file': str_data4ai_dir + mapname +'/wargame_' + mapname +'.xlsx' ,
                 'str_rdmap_file': str_data4ai_dir + mapname +'/reduced_map.xls' ,
                 'str_eptfile': str_data4ai_dir + mapname +'/edgepower_table' ,
                 'str_roadnetadjmat_file': str_data4ai_dir + mapname +'/adjmat_roadnet' ,
                 'str_warzone_file': str_data4ai_dir + mapname +'/warzone.txt' ,
                 'str_stagekeyloc_r_file': str_data4ai_dir + mapname + '/clusters_keylocs_{}.xls'.format('r'),
                 'str_stagekeyloc_b_file': str_data4ai_dir + mapname + '/clusters_keylocs_{}.xls'.format('b'),
                 'str_icutable_file':  str_data4ai_dir + mapname + '/icu_table',
                 'str_wicgtable_file': str_data4ai_dir + mapname + '/wicg_table',
                 'str_distable_file': str_data4ai_dir + mapname + '/dis_table',
                 # 'str_action_cache': str_data4ai_dir + mapname + '/cache_action_{}.npy'.format(strategy_ids[0]),
                 'flag_action_cache': flag_action_cache,
                 'flag_cache': flag_cache,
                 'flag_gpu':flag_gpu,
                 'l_r_ids': l_r_ids,
                 'l_b_ids': l_b_ids,
                 'l_cityinfos': genCityInfos(num_xd),
                 'dic_r_iden2index': dic_r_iden2index,
                 'dic_b_iden2index': dic_b_iden2index,
                 'flag_dllnum':flag_dllnum,
                 'flag_savestate':flag_savestate,
                 'str_tsmin_path': str_data4ai_dir + mapname +'/stra_minfea.t7' ,
                 'str_tsmax_path': str_data4ai_dir + mapname +'/stra_maxfea.t7' ,
                 'str_mctssddata_dirpath': str_data4ai_dir + mapname + '/sddata',
                 'str_mctsfea_filepath': str_data4ai_dir + mapname + '/fealabeldata/fea',
                 'str_mctslabel_filepath': str_data4ai_dir + mapname + '/fealabeldata/label',
                 'str_stramodel_dirpath': str_data4ai_dir + mapname + '/model',
                 'stra_feadim': 0# wgfeature.get_featuredim(),
                 }
    except Exception as e:
        common.echosentence_color('wargamepreknowledge > genDicParas():{}'.format ( str ( e ) ))
        raise

class PreKnow:

    def __init__(self, dic_mainparas):
        '''BUG0: 设置平台预定义的AI的参数 self.dic_paras['dic_aiparas'] '''
        try:
            self.dic_paras = genDicParas(ip=dic_mainparas['ip'], roomid=dic_mainparas['roomid'],
                                         num_xd=dic_sen2mapid[dic_mainparas['num_xd']],
                                         # strategy_ids=dic_mainparas['strategy_ids'],
                                         mapname=dic_xd2name[dic_sen2mapid[dic_mainparas['num_xd']]],
                                         str_global_flag=dic_mainparas['str_global_flag'],
                                         flag_qd_rm=dic_mainparas['flag_qd_rm'],
                                         flag_action_cache=dic_mainparas['flag_action_cache'],
                                         flag_cache=dic_mainparas['flag_cache'],
                                         flag_gpu=dic_mainparas['flag_gpu'],
                                         flag_dllnum=dic_mainparas['flag_dllnum'],
                                         flag_savestate=False,
                                         str_wgrootdir=dic_mainparas['str_wgrootdir'])
            self.dic_paras['dic2_aiparas'] = dic_mainparas['dic2_aiparas']
            # self.dic_paras['flag_show'] = dic_mainparas['flag_show']
            self.dic_paras['flag_color4acai'] = dic_mainparas['dic2_aiparas']['flag_color4acai']
            self.dic_paras['flag_afm'] = dic_mainparas['flag_afm']
            # self.dic_paras['useRandom'] = dic_mainparas['useRandom']
            # self.dic_paras['obj_afmparas'] = G4AFM(num_xd=dic_mainparas['num_xd'])
            # todo 加载预定义路线相关的成员变量
            # self.np_stagekeylocs_r, self.np_stagekeylocs_b, self.dic_bop2rowindex_stageloc = self.__loadStageKeyLoc()

        except Exception as e:
            common.echosentence_color('PreKnow > __init__():{}'.format(str(e)))
            raise

    def InitFlagMovingDics(self ):
        ''' 为两方生成一份完整的算子标志串->flag_moving'''
        return { x: 1 for x in self.dic_paras['l_r_ids'] + self.dic_paras['l_b_ids'] }
    
    # todo 增加基于算子ID/时间节点获取预定义路线的函数

    def __loadStageKeyLoc(self):
        ''' 算子的唯一标识为'%d_%d_%d' %(GameColor , ObjArmy , ObjType) ==>   对应在阶段关键位置点中的具体行
            [# 算子排列:先蓝后红]
            KEY0: 注意：红蓝方的预定义路线分离，算子数量operator_num只针对单一颜色方
        '''
        try:
            # update self.np_stagekeylocs_r/self.np_stagekeylocs_b
            self.np_stagekeylocs_r = pandas.read_excel(self.dic_paras['str_stagekeyloc_r_file']).iloc[:, 1:22].fillna(
                'missing').values
            self.np_stagekeylocs_b = pandas.read_excel(self.dic_paras['str_stagekeyloc_b_file']).iloc[:, 1:22].fillna(
                'missing').values
            strategy_id_r, strategy_id_b = self.dic_paras['strategy_id_r'], self.dic_paras['strategy_id_b']
            operator_num_r, operator_num_b = genOperatorNum(self.dic_paras['num_xd'], flag_color=0), genOperatorNum(
                self.dic_paras['num_xd'], flag_color=1)
            assert (strategy_id_r >= 0 and strategy_id_r < self.np_stagekeylocs_r.shape[0] // operator_num_r)
            assert (strategy_id_b >= 0 and strategy_id_b < self.np_stagekeylocs_b.shape[0] // operator_num_b)
            # update self.dic_bop2rowindex_stageloc
            self.dic_bop2rowindex_stageloc = {}
            list_stras = [strategy_id_r, strategy_id_b]
            list_oper_nums = [operator_num_r, operator_num_b]
            list_str_ids = ['l_r_ids', 'l_b_ids']
            list_colors = [0, 1]
            for color in list_colors:
                list_key = self.dic_paras[list_str_ids[color]]
                list_value = [x + list_stras[color] * list_oper_nums[color] for x in range(0, len(list_key))]
                self.dic_bop2rowindex_stageloc.update(dict(zip(list_key, list_value)))
            return (self.np_stagekeylocs_r, self.np_stagekeylocs_b, self.dic_bop2rowindex_stageloc)
        except Exception as e:
            common.echosentence_color('PreKnow > __loadStageKeyLoc():{}'.format(str(e)))
            raise

    def __getCurStageKeyLocByIdentity(self, str_identykey, cur_stageid, flag_color=None):
        '''根据算子的indetity获取算子位置
            # 需要进行扰动，使用目标位置或者目标位置周围1邻域的六角格代替目标位置
            # 进行扰动的条件: 推演模式/ 60%的概率选择/ 在第一个回合之后 cur_stageid > 4 / 检查扰动后的六角格在地图范围内部
            # print 'ori hex = %d' %(tmp_int4loc)
        '''
        try:
            assert (str_identykey in list(self.dic_bop2rowindex_stageloc))
            tmprow, tmpcol = self.dic_bop2rowindex_stageloc[str_identykey], cur_stageid
            tmp_int4loc = self.np_stagekeylocs_r[tmprow][tmpcol] if flag_color == 0 else self.np_stagekeylocs_b[tmprow][tmpcol]
            if math.isinf(tmp_int4loc) or math.isnan(tmp_int4loc):
                assert tmpcol >= 1
                tmp_int4loc = self.np_stagekeylocs_r[tmprow][tmpcol - 1] if flag_color == 0 else \
                self.np_stagekeylocs_b[tmprow][tmpcol - 1]
                
            # if flag_turbulence and random.randint(0, 100) % 3 >= 1 and cur_stageid > 4:
                # obj_hexoff = hex.HEX_OFF(int(tmp_int4loc) // 100, int(tmp_int4loc) % 100)
                # list_dir = []
                # list_dir.append(random.randint(0, 5))
                # list_neighhex = obj_hexoff.getSpecifiedNeighFromDirList(list_dir_index=list_dir)
                # tuple_neighhex = list_neighhex[0]
                # if int(tuple_neighhex[0]) >= 0 and int(tuple_neighhex[1]) >= 0:
                #     tmp_int4loc = 100 * int(tuple_neighhex[0]) + int(tuple_neighhex[1])
            return common.cvtInt4loc2Int6loc(int(tmp_int4loc))
        except Exception as e:
            common.echosentence_color('PreKnow > __getCurStageKeyLocByIdentity():{}'.format(str(e)))
            raise

    def getPreLoc(self, cur_bop, stageid):
        '''
            坦克：根据stageid判断是选择预定义路线还是自由发挥
            战车/人：全部阶段选择预定义路线
        :param cur_bop:
        :param stageid:
        :return:
        '''
        try:
            stageid_thres = dic_r_xd2fixedRouteStage[self.dic_paras['num_xd']] if cur_bop.GameColor == 0 else dic_b_xd2fixedRouteStage[self.dic_paras['num_xd']]
            flag_preroute = stageid <= stageid_thres if cur_bop.ObjTypeX == 0 else True
            if flag_preroute:
                str_bop_id = common.getBopIdentity(cur_bop)
                int6loc = self.__getCurStageKeyLocByIdentity(str_bop_id, stageid, cur_bop.GameColor)
                return (True, int6loc)
            else:
                return (False, None)
            
        except Exception as e:
            common.echosentence_color('PreKnow > getPreLoc()')
            return (False, None)

    def __getCurStageKeyTaskByIdentity(self, str_identykey, cur_stageid, flag_color):
        '''根据算子的indetity获取算子位置
            # 需要进行扰动，使用目标位置或者目标位置周围1邻域的六角格代替目标位置
            # 进行扰动的条件: 推演模式/ 60%的概率选择/ 在第一个回合之后 cur_stageid > 4 / 检查扰动后的六角格在地图范围内部
            # print 'ori hex = %d' %(tmp_int4loc)
        '''
        try:
            assert (str_identykey in list(self.dic_bop2rowindex_stageloc))
            tmprow, tmpcol = self.dic_bop2rowindex_stageloc[str_identykey], cur_stageid
            str_tasknode = self.np_stagekeylocs_r[tmprow][tmpcol] if flag_color == 0 else \
                self.np_stagekeylocs_b[tmprow][tmpcol]
            return str_tasknode
        except Exception as e:
            common.echosentence_color('PreKnow > __getCurStageKeyTaskByIdentity():{}'.format(str(e)))
            raise

    def getPreTask(self, str_id, stageid):
        '''
            坦克：根据stageid判断是选择预定义路线还是自由发挥
            战车/人：全部阶段选择预定义路线
        :param str_id:
        :param stageid:
        :return:
        '''
        try:
            str_pre_tasknode = self.__getCurStageKeyTaskByIdentity(str_id, stageid, int(str_id[0]))
            return str_pre_tasknode
        except Exception as e:
            common.echosentence_color('PreKnow > getPreLoc()')
            raise e
        
    def checkGetoff(self, cur_bop):
        num_xd = self.dic_paras['num_xd']
        flag_getoff = cur_bop.ObjTypeX == 1 and cur_bop.ObjSonNum == 1 and cur_bop.ObjStep >= 3
        flag_getoff = flag_getoff and (cur_bop.ObjPos in (dic_r_xd2listgetofflocs[num_xd] if cur_bop.GameColor == 0 else dic_b_xd2listgetofflocs[num_xd]))
        return flag_getoff
    
    def getDangerLocs(self):
        return genDangerLocs(num_xd= self.dic_paras['num_xd'])
    
    def getDefaultAttackDir(self, flag_color):
        try:
            dic_xd2attackdir = dic_b_xd2attackdir if flag_color == 1 else dic_r_xd2attackdir
            return dic_xd2attackdir[self.dic_paras['num_xd']]
        except Exception as e:
            common.echosentence_color('PreKnow > getDefaultAttackDir():{}'.format(str(e)))
            raise e
    
    def __getWarZoneLocs(self):
        assert self.dic_paras['num_xd'] in dic_xd2warzoneloc.keys()
        return dic_xd2warzoneloc[self.dic_paras['num_xd']]
    
    def getWarZoneCenterint6loc(self):
        try:
            list_int6locs = self.__getWarZoneLocs()
            assert list_int6locs
            c_y, c_x = 0, 0
            for tmp_int6loc in list_int6locs:
                tmp_y, tmp_x = common.cvtInt6loc2HexOffset(tmp_int6loc)
                c_y += tmp_y
                c_x += tmp_x
            c_y = c_y // len(list_int6locs)
            c_x = c_x // len(list_int6locs)
            return common.cvtHexOffset2Int6loc(c_y, c_x)
        except Exception as e:
            common.echosentence_color('PreKnow > getWarZoneCenterint6loc():{}'.format(str(e)))
            raise e

    def _getFixStageID(self, flag_color):
        try:
            dic_xd2fixedRouteStage = genDicXD2RouteStage()[flag_color]
            return dic_xd2fixedRouteStage[self.dic_paras['num_xd']]
        except Exception as e:
            raise e

    # def getCurStageKeyLoc(self, cur_bop, cur_stageid, flag_turbulence = False):
    #     '''返回指定算子在指定阶段的关键位置点'''
    #     try:
    #         cur_stageid = 20 if cur_stageid > 20 else cur_stageid
    #         assert(cur_stageid >= 1 and cur_stageid <= 20)
    #         str_identykey = '%d_%d_%d' % (cur_bop.GameColor, cur_bop.ObjArmy, cur_bop.ObjType )
    #         return self.__getCurStageKeyLocByIdentity(str_identykey, cur_stageid, flag_color= cur_bop.GameColor, flag_turbulence = flag_turbulence)
    #     except Exception as e:
    #         common.echosentence_color('PreKnow > getCurStageKeyLoc():{}'.format( str( e ) ))
    #         raise
            

if __name__ == '__main__':
    ip = '10.0.14.150'
    roomid = 3 + 11
    flag_ai_color = 0
    num_xd, strategy_id_r, strategy_id_b = 9, 0, 0
    num_plays, num_objcutility = 1, 1
    dic2_rolloutaiparas = None
    dic_mainparas = {'str_wgrootdir': '../',
                     'str_global_flag': 'AC',
                     'num_plays': num_plays,
                     'num_objcutility': num_objcutility,
                     'ip': ip,
                     'roomid': roomid,
                     'num_xd': num_xd,
                     'strategy_ids': (strategy_id_r, strategy_id_b),
                     'flag_show': True,
                     'flag_action_cache': False,
                     'flag_qd_rm': False,
                     'flag_cache': False,
                     'flag_gpu': False,
                     'flag_dllnum': 0,
                     'flag_afm': True,
                     'cuda_id': 0,
                     'flag_savestate': False,
                     'dic2_aiparas': {
                         'flag_color4acai': flag_ai_color,
                         'red': {'type_ai': None,
                                 'type_stra': 'rule-base',
                                 # type of stratree of nodes, how to select next path, [rule-base, random, net]
                                 'type_stranet': None,
                                 'dic2_rolloutaiparas': dic2_rolloutaiparas,
                                 'flag_candidateactions': 'rule-base'
                                 # [rule-base, stra] how to get candidate actions
                                 },
                         'blue': {'type_ai': None,
                                  'type_stra': 'net',
                                  'type_stranet': None,
                                  'dic2_rolloutaiparas': dic2_rolloutaiparas,
                                  'flag_candidateactions': 'stra'
                                  },
                     },
                     }
    
    obj_pk = PreKnow(dic_mainparas)
    print(obj_pk.dic_paras)
    pass