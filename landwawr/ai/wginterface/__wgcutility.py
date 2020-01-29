# coding:utf-8

"""
2017年8月27日/gsliu/PAL_Wargame
文件说明：封装C模块提供的组件
    2017年8月27日：建立文档
"""

import numpy, pandas, ctypes, os, time
from numpy.ctypeslib import ndpointer
from copy import deepcopy
import __wgobject as wgobject
import __common as common
import __hex as hex
from __wgjudge import getEnterHexPower
from __common import echosentence_color
import __wgcache as wgcache


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
# metaclass=Singleton
# class CUtility(metaclass=Singleton):

class CUtility(object):

    if "WG_CACHE_XD" in os.environ:
        cache_root = "./xd_" + os.environ["WG_CACHE_XD"]
    else:
        cache_root = "./xd_0"
    if "WG_CACHE_FROZEN" in os.environ:
        frozen = bool(int(os.environ["WG_CACHE_FROZEN"]))
    else:
        frozen = True
    static_blindmap_decorator = wgcache.CacheDecorator(
        cache_file=os.path.join(cache_root, "cache_static_blindmap.pkl"),
        save_every_nmiss=10000,
        cal_key_fn=wgcache.cal_key_for_blindmap_p2p,
        log_level="error",
        log_prefix="STATIC_BLINDMAP:",
        log_every_ncall=1000,
        frozen=frozen,
    )

    dynamic_blindmap_decorator = wgcache.CacheDecorator(
        cache_file=os.path.join(cache_root, "cache_dynamic_blindmap.pkl"),
        save_every_nmiss=1000,
        cal_key_fn=wgcache.cal_key_for_blindmap_p2p,
        log_level="error",
        log_prefix="DYNAMIC_BLINDMAP:",
        log_every_ncall=100,
        frozen=frozen,
    )

    # @profile
    def __init__(self, dic_paras):
        self.max_y_hexnum = dic_paras["max_y_hexnum"]
        self.max_x_hexnum = dic_paras["max_x_hexnum"]
        self.utilitiesSo = None
        self.flag_gpu = dic_paras["flag_gpu"]
        self.flag_dllnum = dic_paras["flag_dllnum"]
        assert self.flag_dllnum >= 0
        self.np_ep_table = None

        try:
            # 网络时间验证
            try:
                # todo 大部分时候都要进行网络校验
                # if (not soft_highpro()) and (not dbus_gsliu_time_my_hashUYBC()):
                #     flag_casia_connection_check = False
                #     assert flag_casia_connection_check
                pass
            except Exception as e:
                echosentence_color(
                    "CUtility > __init[jbeitm]__():{}".format(str(e)), "red"
                )
                raise e

            self.utilitiesSo = self.getUtilitiesSo(dic_paras)

            # # 更新所有的函数的argtypes/ restype
            # warpMSAction
            self.utilitiesSo.warpMSAction.argtypes = [
                ctypes.POINTER(wgobject.BasicOperator),  # bop_attacker
                ctypes.POINTER(wgobject.BasicOperator),  # bop_obj
                ctypes.c_int,
                ctypes.c_int,  # flag_ss, flag_task
                ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),  # np_damagemaskmap
                ndpointer(ctypes.c_int, flags="C_CONTIGUOUS"),  # blindarea_data
                ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
            ]  # np_aiaciton
            self.utilitiesSo.warpMSAction.restype = None
            # warpDA00SMAction
            # warpDirectShootAction
            self.utilitiesSo.warpDirectShootAction.argtypes = [
                ctypes.POINTER(wgobject.BasicOperator),  # bop_attacker
                ctypes.POINTER(wgobject.BasicOperator),  # bop_obj
                ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
            ]  # np_aiaciton
            self.utilitiesSo.warpDirectShootAction.restype = None
            #
            # warpRushMovingAction
            self.utilitiesSo.warpRushMovingAction.argtypes = [
                ctypes.POINTER(wgobject.BasicOperator),
                ndpointer(ctypes.c_int, flags="C_CONTIGUOUS"),  # np_keyloc
                ndpointer(ctypes.c_int, flags="C_CONTIGUOUS"),  # np_totalblindmap
                ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
            ]  # np_aiaction
            self.utilitiesSo.warpRushMovingAction.restype = None

            # warpIcuIsOk
            self.utilitiesSo.warpGetMyIcuFlag.argtypes = [
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.POINTER(ctypes.c_int),
            ]
            self.utilitiesSo.warpGetMyIcuFlag.restype = None

            self.utilitiesSo.warpGetPath.argtypes = [
                ctypes.POINTER(wgobject.BasicOperator),
                ctypes.c_int,
                ctypes.c_int,
                ndpointer(ctypes.c_int, flags="C_CONTIGUOUS"),
            ]

            self.utilitiesSo.warpOneWeaponDirectDamageP2P.argtypes = [
                ctypes.POINTER(wgobject.BasicOperator),
                ctypes.POINTER(wgobject.BasicOperator),
                ctypes.c_int,
                ctypes.POINTER(ctypes.c_float),
            ]

            # # warpGetMyIouMap
            self.utilitiesSo.warpGetMyIouMap.argtypes = [
                ctypes.c_int,
                ctypes.POINTER(wgobject.BasicOperator),
                ctypes.POINTER(wgobject.BasicOperator),
                ctypes.POINTER(wgobject.BasicTensor),
            ]
            self.utilitiesSo.warpGetMyIouMap.restypes = None

            # warpGetMyIouDynamicMap
            self.utilitiesSo.warpGetMyIouDynamicMap.argtypes = [
                ctypes.c_int,
                ctypes.POINTER(wgobject.BasicOperator),
                ctypes.POINTER(wgobject.BasicOperator),
                ctypes.POINTER(wgobject.BasicTensor),
            ]
            self.utilitiesSo.warpGetMyIouDynamicMap.restypes = None

            # warpGetMyDamageMap
            # todo 计算算子A对算子B的攻击等级：B在自己的机动范围内移动，确定A对每一点上B的攻击等级
            self.utilitiesSo.warpGetMyDamageMap.argtypes = [
                ctypes.POINTER(wgobject.BasicOperator),
                ctypes.POINTER(wgobject.BasicOperator),
                ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
            ]
            self.utilitiesSo.warpGetMyDamageMap.restypes = None
            print("wgcutility load complete")

            # warpSpecHideMSAction  计算给定躲避位置的坦克行进间射击的动作 sgr添加 2018年10月15日
            # self.utilitiesSo.warpSpecHideMSAction.argtypes = [ctypes.POINTER(wgobject.BasicOperator),  # bop_attacker
            #                                           ctypes.POINTER(wgobject.BasicOperator),  # bop_obj
            #                                           ctypes.c_int,  # int_hideloc4 躲避位置
            #                                           ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"), #p_uniondamage_map
            #                                           ndpointer(ctypes.c_float, flags="C_CONTIGUOUS")]  # np_aiaciton
            #
            # todo 加入获取坦克所有攻击路径的函数 warpGetALLFFBTRoutes
            # self.utilitiesSo.warpGetALLFFBTRoutes.argtypes = [
            #     ctypes.POINTER(wgobject.BasicOperator),
            #     ctypes.POINTER(wgobject.BasicOperator),
            #     ctypes.c_int,
            #     ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
            # ]
            # self.utilitiesSo.warpGetALLFFBTRoutes.restypes = None

        except Exception as e:
            common.echosentence_color("error in CUtility __init__():{}".format(str(e)))
            raise

    """申请动态链接库的接口句柄"""
    # @profile
    def getUtilitiesSo(self, dic_paras):
        try:
            #  初始化地图属性特征 &  初始化单边机动力消耗
            str_soloc = "{}{}{}.so".format(
                dic_paras["str_cModuleDir"],
                dic_paras["mapname"],
                "" if self.flag_dllnum == 0 else str(self.flag_dllnum),
            )
            assert os.path.exists(str_soloc)
            utilitiesSo = ctypes.CDLL(str_soloc)
            df_reduced_map = self.getReducedMapData(dic_paras["str_rdmap_file"])
            # df_reduced_map = df_reduced_map.sort_values(by='MapID')
            assert len(df_reduced_map) >= 0 and len(df_reduced_map.T) >= 0

            # 地图(需要将每个六角格的像素坐标补充进来（多加入两列数据 row col）)
            np_reduced_map = numpy.ascontiguousarray(
                df_reduced_map.values.astype(ctypes.c_int)
            )

            # 机动力消耗表
            np_ep_table = numpy.loadtxt(dic_paras["str_eptfile"])
            self.np_ep_table = np_ep_table
            np_ep_table = numpy.ascontiguousarray(np_ep_table.astype(ctypes.c_int))

            # 道路网的邻接表
            np_rdnet_adjmat = numpy.loadtxt(dic_paras["str_roadnetadjmat_file"])
            np_rdnet_adjmat = numpy.ascontiguousarray(
                np_rdnet_adjmat.astype(ctypes.c_int)
            )  # 转换numpy到连续内存

            # 武器属性表
            np_wptable = numpy.loadtxt(dic_paras["str_wptable_file"])
            np_wptable = numpy.ascontiguousarray(
                np_wptable.astype(ctypes.c_int)
            )  # 转换numpy到连续内存
            # 初始化 utilitiesSo中的全局变量
            utilitiesSo.warpInitMapAttr.argtypes = [
                ndpointer(ctypes.c_int, flags="C_CONTIGUOUS"),
                ndpointer(ctypes.c_int, flags="C_CONTIGUOUS"),
                ndpointer(ctypes.c_int, flags="C_CONTIGUOUS"),
                ndpointer(ctypes.c_int, flags="C_CONTIGUOUS"),
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
            ]
            utilitiesSo.warpInitMapAttr.restype = None
            utilitiesSo.warpInitMapAttr(
                np_reduced_map,
                np_ep_table,
                np_rdnet_adjmat,
                np_wptable,
                ctypes.c_int(np_reduced_map.shape[0]),
                ctypes.c_int(np_reduced_map.shape[1]),
                ctypes.c_int(np_ep_table.shape[0]),
                ctypes.c_int(np_ep_table.shape[1]),
                ctypes.c_int(np_rdnet_adjmat.shape[0]),
                ctypes.c_int(np_rdnet_adjmat.shape[1]),
                ctypes.c_int(np_wptable.shape[0]),
                ctypes.c_int(np_wptable.shape[1]),
            )

            #   初始化基于概率的攻击等级
            np_damagetable_zm2car = (
                numpy.loadtxt(
                    dic_paras["str_file_zm2cartable"], dtype=float, comments="_"
                )
                .reshape((125, 11, 10))
                .astype(ctypes.c_float)
            )
            np_damagetable_zm2car = numpy.ascontiguousarray(np_damagetable_zm2car)
            np_damagetable_ltf2car = (
                numpy.loadtxt(
                    dic_paras["str_file_ltf2cartable"], dtype=float, comments="_"
                )
                .reshape((25, 11, 10))
                .astype(ctypes.c_float)
            )
            np_damagetable_ltf2car = numpy.ascontiguousarray(np_damagetable_ltf2car)
            np_damagetable_allw2people = (
                numpy.loadtxt(
                    dic_paras["str_file_allw2peopletable"], dtype=float, comments="_"
                )
                .reshape((5, 11, 10))
                .astype(ctypes.c_float)
            )
            np_damagetable_allw2people = numpy.ascontiguousarray(
                np_damagetable_allw2people
            )
            utilitiesSo.warpInitDamageTable.argtypes = [
                ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
                ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
                ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
            ]
            utilitiesSo.warpInitDamageTable.restype = None
            utilitiesSo.warpInitDamageTable(
                np_damagetable_zm2car,
                np_damagetable_ltf2car,
                np_damagetable_allw2people,
            )

            if dic_paras["flag_cache"]:  # 加载缓存数据
                # print '-' * 30
                # print u'初始化缓存数据'
                common.echosentence_color("init cache data", "blue")
                utilitiesSo.warpInitCacheData.argtypes = [
                    ndpointer(ctypes.c_int, flags="C_CONTIGUOUS"),
                    ctypes.c_int,
                    ndpointer(ctypes.c_longlong, flags="C_CONTIGUOUS"),
                    ctypes.c_int,
                    ndpointer(ctypes.c_longlong, flags="C_CONTIGUOUS"),
                    ctypes.c_int,
                ]
                utilitiesSo.warpInitCacheData.restype = None
                np_icutable = numpy.loadtxt(
                    fname=dic_paras["str_icutable_file"], dtype=int
                ).astype(dtype=ctypes.c_int)
                np_icutable = numpy.ascontiguousarray(np_icutable)  # 转换numpy到连续内存
                np_wicgtable = numpy.loadtxt(
                    fname=dic_paras["str_wicgtable_file"], dtype=float
                ).astype(dtype=ctypes.c_longlong)
                np_wicgtable = numpy.ascontiguousarray(np_wicgtable)  # 转换numpy到连续内存
                np_distable = numpy.loadtxt(
                    fname=dic_paras["str_distable_file"], dtype=float
                ).astype(dtype=ctypes.c_longlong)
                np_distable = numpy.ascontiguousarray(np_distable)  # 转换numpy到连续内存
                utilitiesSo.warpInitCacheData(
                    np_icutable,
                    ctypes.c_int(np_icutable.shape[0]),
                    np_wicgtable,
                    ctypes.c_int(np_wicgtable.shape[0]),
                    np_distable,
                    ctypes.c_int(np_distable.shape[0]),
                )

            if dic_paras["flag_gpu"]:
                assert dic_paras["flag_cache"]
                # print '-' * 30
                # print u'初始化显存数据'
                common.echosentence_color("init gpu memory")
                utilitiesSo.warpCudaInit.argtypes = [
                    ctypes.c_int,
                    ctypes.c_int,
                    ctypes.c_int,
                ]
                utilitiesSo.warpCudaInit.restypes = [ctypes.c_bool]
                utilitiesSo.warpCudaInit(
                    ctypes.c_int(len(dic_paras["l_r_ids"])),
                    ctypes.c_int(len(dic_paras["l_b_ids"])),
                    ctypes.c_int(len(dic_paras["l_cityinfos"]) // 3),
                )

            return utilitiesSo
        except Exception as e:
            common.echosentence_color(
                "wargamecutility > getUtilitiesSo():{}".format(str(e))
            )
            raise

    """获取我方算子的机动范围地图，地图上的数值表示算子机动到该位置剩余的机动力
    """
    # @profile
    def getWhereICanGoMap(self, cur_bop):
        """
            KEY0: 算子的机动范围地图，>=0为有效位置，-1为无效位置（不可达到位置）
            BUG1: 限制算子的机动范围，上下左右边界周围3格的区域都强制无法达到
        :param cur_bop:
        :return:
        """
        try:
            # print '\tgetWhereICanGoMap()'
            basic_bt_wicgMap = wgobject.BasicTensor()
            basic_bt_wicgMap.ndim = ctypes.c_int(2)
            tmp_p_ints = (ctypes.c_int * basic_bt_wicgMap.ndim)(
                self.max_y_hexnum, self.max_x_hexnum
            )
            basic_bt_wicgMap.shape = ctypes.cast(
                tmp_p_ints, ctypes.POINTER(ctypes.c_int)
            )
            np_wicpmap = numpy.zeros(
                (self.max_y_hexnum, self.max_x_hexnum), ctypes.c_float, order="C"
            )
            p_np_wicpmap = np_wicpmap.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
            basic_bt_wicgMap.data = p_np_wicpmap
            self.utilitiesSo.warpGetMyWhereICanGoMap(
                ctypes.byref(cur_bop), ctypes.byref(basic_bt_wicgMap)
            )
            np_wicpmap = np_wicpmap.astype(dtype=int)
            # fill border zone
            border_width = 3
            np_wicpmap[:border_width].fill(-1)
            np_wicpmap[np_wicpmap.shape[0] - border_width :].fill(-1)
            np_wicpmap[:, :border_width].fill(-1)
            np_wicpmap[:, np_wicpmap.shape[1] - border_width :].fill(-1)
            return np_wicpmap
        except Exception as e:
            common.echosentence_color("error in getWhereICanGoMap():{}".format(str(e)))
            raise

    """检查算子A是否能够观察到算子B
        返回0 不能观察/ 1 可观察 """
    # @profile
    def checkIoUIsOk(self, bopa, bopb):
        try:
            # print '\tcheckIoUIsOk()'
            flag_icu = ctypes.c_int(0)
            self.utilitiesSo.warpIouIsOk(
                ctypes.byref(bopa), ctypes.byref(bopb), ctypes.byref(flag_icu)
            )
            return flag_icu.value
        except Exception as e:
            common.echosentence_color("error in checkIoUIsOk():{}".format(str(e)))
            raise

    """检查两个位置间是否通视
            返回0 不通视/ 1 通视 """
    # @profile
    def checkIcUIsOk(self, rowa, cola, rowb, colb):
        try:
            # print '\tcheckIoUIsOk()'
            flag_icu = ctypes.c_int(0)
            maxDis = 500
            self.utilitiesSo.warpGetMyIcuFlag(
                rowa, cola, rowb, colb, maxDis, ctypes.byref(flag_icu)
            )
            return flag_icu.value
        except Exception as e:
            common.echosentence_color("error in checkIoUIsOk():{}".format(str(e)))
            raise

    """计算不超过给定距离的通视范围"""
    # @profile
    def getLOSArea(self, coordinate, distance):
        try:
            int4loc = common.cvtInt6loc2Int4loc(coordinate)
            np_LOSArea = numpy.zeros(
                (self.max_y_hexnum, self.max_x_hexnum), ctypes.c_int, order="C"
            )
            self.utilitiesSo.warpGetLOSArea(int4loc, distance, np_LOSArea)
            return np_LOSArea
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    """ 计算我方算子obop的视野盲区
        即目标算子躲在哪些位置（0）不会被我方算子（所有）看到，在哪些位置可以被我方算子看到(1)"""
    # @profile
    def getViewBlindRange(self, obop, ubop):
        try:
            t = time.time()
            np_ioumap = numpy.zeros(
                (self.max_y_hexnum, self.max_x_hexnum), ctypes.c_int, order="C"
            )
            # print '\tgetViewBlindRange()'
            basic_bt_ioumap = wgobject.BasicTensor()
            basic_bt_ioumap.ndim = ctypes.c_int(2)
            tmp_p_ints = (ctypes.c_int * basic_bt_ioumap.ndim)(
                self.max_y_hexnum, self.max_x_hexnum
            )
            basic_bt_ioumap.shape = ctypes.cast(
                tmp_p_ints, ctypes.POINTER(ctypes.c_int)
            )
            # np_ioumap = numpy.zeros((self.max_y_hexnum, self.max_x_hexnum), ctypes.c_int, order= 'C')
            # np_ioumap = numpy.ascontiguousarray(np_ioumap)
            p_np_ioumap = np_ioumap.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
            basic_bt_ioumap.data = p_np_ioumap
            # flag_mode = 0 if not self.flag_gpu else 2
            flag_mode = 0
            # bop_obj不会被看到的位置标记为0，否则标记为1
            self.utilitiesSo.warpGetMyIouMap(
                ctypes.c_int(flag_mode),
                ctypes.byref(obop),
                ctypes.byref(ubop),
                ctypes.byref(basic_bt_ioumap),
            )
            return np_ioumap

        except Exception as e:
            common.echosentence_color("error in getViewBlindRange():{}".format(str(e)))
            raise

    # todo getViewBlindRange（）函数的动态版本（我方算子是坦克,对方算子的暴露程度）
    # @profile
    def getDynamicViewBlindRange(self, obop, ubop):
        try:
            assert obop.A1 == 1
            # print '\tgetViewBlindRange()'
            basic_bt_ioumap = wgobject.BasicTensor()
            basic_bt_ioumap.ndim = ctypes.c_int(2)
            tmp_p_ints = (ctypes.c_int * basic_bt_ioumap.ndim)(
                self.max_y_hexnum, self.max_x_hexnum
            )
            basic_bt_ioumap.shape = ctypes.cast(
                tmp_p_ints, ctypes.POINTER(ctypes.c_int)
            )
            np_ioumap = numpy.zeros(
                (self.max_y_hexnum, self.max_x_hexnum), ctypes.c_int, order="C"
            )
            # np_ioumap = numpy.ascontiguousarray(np_ioumap)
            p_np_ioumap = np_ioumap.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
            basic_bt_ioumap.data = p_np_ioumap
            # flag_mode = 0 if not self.flag_gpu else 2
            flag_mode = 0
            self.utilitiesSo.warpGetMyIouDynamicMap(
                ctypes.c_int(flag_mode),
                ctypes.byref(obop),
                ctypes.byref(ubop),
                ctypes.byref(basic_bt_ioumap),
            )  # bop_obj不会被看到的位置标记为0，否则数值>0
            return np_ioumap

        except Exception as e:
            common.echosentence_color(
                "__wgutility > getDynamicViewBlindRange():{}".format(str(e))
            )
            raise

    """为算子ubop找出最进的躲避位置 pre_int6loc 
        给定参数：对方所有算子的盲区 np_totalblind， 数值为0标识该位置不会被对方算子看到，位置非零标识对方算子能够看到bop_obj
        预估对方位置的时候: 可以不考虑危险点； 自己做决策的时候，在撤退环节需要用战损最小 + 危险点共同计算撤退点
        """
    # @profile
    def getNearestHideLoc(self, list_o_bops, ubop, list_danger_locs=[]):
        try:
            # print '\tgetNearestHideLoc()'
            flag_danger = True if len(list_danger_locs) > 0 else False
            np_totalblindmap = self.getTotalBlindMap(
                list_o_bops,
                ubop,
                flag_danger=flag_danger,
                list_danger_locs=list_danger_locs,
            )

            self.utilitiesSo.warpGetNHideLoc.argtypes = [
                ctypes.POINTER(wgobject.BasicOperator),
                ndpointer(ctypes.c_int, flags="C_CONTIGUOUS"),
                ctypes.POINTER(ctypes.c_int),
            ]
            self.utilitiesSo.warpGetNHideLoc.restypes = None
            np_totalblind = numpy.ascontiguousarray(
                np_totalblindmap.astype(ctypes.c_int)
            )
            hide_int6loc = ctypes.c_int(0)
            self.utilitiesSo.warpGetNHideLoc(
                ctypes.byref(ubop), np_totalblind, ctypes.byref(hide_int6loc)
            )

            return hide_int6loc.value
        except Exception as e:
            common.echosentence_color(
                str("error in getNearestHideLoc():{}".format(str(e)))
            )
            raise

    """ 给定对方算子list_ubops， 我方算子obop, 为我方算子找出最优的躲避位置"""
    # @profile
    def getOptTwoMinDamageLocs(self, list_g_stage, list_ubops, obop):
        try:
            # print '\tgetOptTwoMinDamageLocs()'
            np_damagemaskmap = self.getUnionDamageMaskMap(
                list_g_stage, list_ubops, obop, "sum"
            )
            np_damagemaskmap = numpy.ascontiguousarray(
                np_damagemaskmap.astype(ctypes.c_float)
            )
            len = ctypes.c_int(2)
            np_hidelocs = numpy.zeros((1, 2), ctypes.c_int, "C")
            self.utilitiesSo.warpGetMinDamgageLoc(
                ctypes.byref(obop), np_damagemaskmap, len, np_hidelocs
            )
            np_hidelocs = np_hidelocs.astype(int)

            return np_hidelocs
        except Exception as e:
            common.echosentence_color(
                "error  in getOptTwoMinDamageLocs():{}".format(str(e))
            )
            raise

    """计算攻击算子列表内list_attbops内的所有算子对目标算子 objbop 的战损图列表"""
    # @profile
    def getUnionDamageMaskMap(
        self, list_g_stage, list_attbops, objbop, flag_method="max"
    ):
        """
            BUG0: C 模块中只计算目标算子在其机动范围内的被攻击战损，其余位置为0
            BUG1: 计算之前先判断攻击算子是否能够进行射击，减少不必要的计算量
            BUG2: remove deep copy # np_3d_damagemaps[index,:,:] = np_2d_damagemap.copy()
        """
        try:
            t = time.time()
            # print '\tgetUnionDamageMaskMap'
            assert flag_method == "max" or flag_method == "sum"
            num_attbops = len(list_attbops)
            np_damagemaskmap = numpy.zeros(
                (self.max_y_hexnum, self.max_x_hexnum), ctypes.c_float, "C"
            )
            if num_attbops > 0:
                np_3d_damagemaps = numpy.zeros(
                    (num_attbops, self.max_y_hexnum, self.max_x_hexnum),
                    ctypes.c_float,
                    order="C",
                )
                for index in range(num_attbops):
                    cur_att = list_attbops[index]
                    # 当前算子不能射击的情况
                    if (
                        cur_att.ObjAttack == 1
                        or cur_att.ObjStep != cur_att.ObjStepMax
                        or (cur_att.ObjTypeX == 2 and cur_att.ObjKeep == 1)
                        or (cur_att.ObjTypeX != 2 and cur_att.ObjPass != 0)
                        or (cur_att.ObjTongge == 1)
                    ):
                        continue
                    self.utilitiesSo.warpGetMyDamageMap(
                        ctypes.byref(list_attbops[index]),
                        ctypes.byref(objbop),
                        np_3d_damagemaps[index, :, :],
                    )
                if flag_method == "max":
                    np_damagemaskmap = np_3d_damagemaps.max(axis=0)
                else:
                    np_damagemaskmap = numpy.sum(np_3d_damagemaps, axis=0)

            return np_damagemaskmap
        except Exception as e:
            common.echosentence_color(
                "error in getUnionDamageMaskMap():{}".format(str(e))
            )
            raise

    """计算视野盲区"""
    # @profile
    def getTotalBlindMap(
        self, list_u_bops, bop_attacker, flag_danger=False, list_danger_locs=[]
    ):

        try:
            # print '\tgetTotalBlindMap'
            np_totalblindmap = numpy.zeros(
                (self.max_y_hexnum, self.max_x_hexnum), ctypes.c_int, "C"
            )
            for ubop in list_u_bops:
                if ubop.A1 == 0:
                    numpy.add(
                        np_totalblindmap,
                        self.getViewBlindRange(ubop, bop_attacker),
                        np_totalblindmap,
                    )
                else:  # 观察算子是坦克
                    numpy.add(
                        np_totalblindmap,
                        self.getDynamicViewBlindRange(ubop, bop_attacker),
                        np_totalblindmap,
                    )
            if flag_danger:
                assert len(list_danger_locs) > 0
            for cur_dloc in list_danger_locs:
                cur_y, cur_x = common.cvtInt6loc2HexOffset(cur_dloc)
                np_totalblindmap[cur_y, cur_x] = 50

            np_totalblindmap = numpy.ascontiguousarray(np_totalblindmap)

            return np_totalblindmap
        except Exception as e:
            common.echosentence_color("error in getTotalBlindMap():{}".format(str(e)))
            raise

    # todo 计算方向区域
    # @profile
    def getDirZoneMaskMap(self, att_int4loc, obj_int4loc, attack_dir=None):
        # 计算给定攻击点和目标点的方向区域:[方向从攻击点到目标点,区域是方向以及方向+/-:1]: 处于该区域为1,否则为0'''
        try:
            int_hexdir = (
                common.com_attackdir(att_int4loc=att_int4loc, obj_int4loc=obj_int4loc)
                if attack_dir is None
                else attack_dir
            )
            list_candidate_hexdirs = common.getNeighborHexdir(int_hexdir)
            assert len(list_candidate_hexdirs) == 3
            # common.echosentence_color(
            #     u"\t攻击算子位置[{}], 目标算子位置[{}], 攻击算子的威胁方向:{}".format(
            #         att_int4loc, obj_int4loc, list_candidate_hexdirs
            #     ),
            #     "white",
            # )
            np_dirzone_map = numpy.zeros(
                (self.max_y_hexnum, self.max_x_hexnum), dtype=int
            )
            for y in range(self.max_y_hexnum):
                for x in range(self.max_x_hexnum):
                    np_dirzone_map[y][x] = (
                        1
                        if common.com_attackdir(y * 100 + x, obj_int4loc)
                        in list_candidate_hexdirs
                        else 0
                    )
            return np_dirzone_map
        except Exception as e:
            common.echosentence_color(
                "__wgcutility.py > getDirZoneMaskMap():{}".format(str(e))
            )
            return e

    # todo 获取我方算子对对方威胁算子的暴露程度
    # @profile
    def getExposedMap(self, obop, ubop, list_tuple_candidate_locs=[], attack_dir=None):
        # 计算方法: 我方机动范围内,计算每个点的可视范围,并和威胁算子的攻击方向区域取交集,取出个数作为该六角格的暴露程度
        # 只计算指定位置的暴露程度
        try:
            obop = wgobject.op_deepcopy(obop)
            ubop = wgobject.op_deepcopy(ubop)
            # 初始设定所有位置都会暴露
            np_exposed_map = numpy.ones(
                (self.max_y_hexnum, self.max_x_hexnum), dtype=int
            )
            np_exposed_map = np_exposed_map * 3000
            # 计算方向区域mask
            np_2d_dirzone_mask = self.getDirZoneMaskMap(
                att_int4loc=common.cvtInt6loc2Int4loc(ubop.ObjPos),
                obj_int4loc=common.cvtInt6loc2Int4loc(obop.ObjPos),
                attack_dir=attack_dir,
            )
            for (y, x) in list_tuple_candidate_locs:
                obop.ObjPos = common.cvtHexOffset2Int6loc(row=y, col=x)
                np_2d_ioumap_mask = self.get_staticobserve_blindmap_p2p(obop, ubop)
                np_final_mask = numpy.logical_and(np_2d_ioumap_mask, np_2d_dirzone_mask)
                np_exposed_map[y][x] = numpy.sum(np_final_mask == True)
            # common.echosentence_color(
            #     u"\t暴露程度的最小数值[{}], 最小数值所在位置[{}]".format(
            #         numpy.min(np_exposed_map), numpy.where(numpy.min(np_exposed_map))
            #     ),
            #     "white",
            # )
            return np_exposed_map
        except Exception as e:
            common.echosentence_color(
                "__wgcutility.py > getDirZoneMaskMap():{}".format(str(e))
            )
            return e

    """获取简化版地图，避免从数据库中读取"""
    # @profile
    def getReducedMapData(self, str_reducedmap_filepath):
        try:
            # print '\tgetReducedMapData()'
            assert os.path.isfile(str_reducedmap_filepath)
            df_reduced_map = pandas.read_excel(str_reducedmap_filepath, "df")
            df_reduced_map.index = df_reduced_map.MapID
            # del df_reduced_map['MapID']
            return df_reduced_map
        except Exception as e:
            common.echosentence_color(
                "error in class getReducedMapData():{}".format(str(e))
            )
            raise e

    """计算静态战损（点对点）"""
    # @profile
    def getDamageP2P(self, o_bop, u_bop, flag_pso=True):
        """
            BUG0:   flag_pso
                    true: 考虑算子的行射能力，返回的damage不能反映算子A和算子B在当前态势下的观察情况，
                          需要预先确定攻击算子能够看到目标算子
                    false: 只进行算子之间的单点damage, 返回的damage能够反映两者的观察情况，如果>0,
                          则一定能够观察，反之，不确定
        """
        try:
            # print '\tgetDamageP2P()'
            damage = ctypes.c_float(0)
            if flag_pso:
                self.utilitiesSo.warpGetDamageP2P(
                    ctypes.byref(o_bop), ctypes.byref(u_bop), ctypes.byref(damage)
                )
            else:
                self.utilitiesSo.warpGetDirectDamageP2P(
                    ctypes.byref(o_bop), ctypes.byref(u_bop), ctypes.byref(damage)
                )
            return damage.value

        except Exception as e:
            common.echosentence_color("error in getDamageP2P():{}".format(str(e)))
            raise

    """计算指定武器的静态战损(点对点)"""
    # @profile
    def getOneWeaponDamageP2P(self, o_bop, u_bop, weaponID):
        try:
            damage = ctypes.c_float(0)
            self.utilitiesSo.warpOneWeaponDirectDamageP2P(
                o_bop, u_bop, weaponID, ctypes.byref(damage)
            )
            return damage.value
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    """算子A到目标位置的机动路线列表"""
    # @profile
    def getRouteList(self, cur_bop, obj_int6loc, flag_routetype=0):
        """
            KEY0:机动路线是完整路线，包括算子当前位置到目标位置[cur_loc, obj_loc], 不能达到返回None
            KEY1:flag_routetype  = 0. 表示按照最优路线（机动力消耗最少进行机动）
        """
        try:
            assert flag_routetype == 0
            np_wicgMap = self.getWhereICanGoMap(cur_bop=cur_bop)
            obj_row, obj_col = common.cvtInt6loc2HexOffset(obj_int6loc)
            list_routes = None
            if np_wicgMap[obj_row][obj_col] >= 0:
                np_aiaction = numpy.zeros((1, 20), ctypes.c_float, order="C")
                np_keyloc = numpy.zeros((1, 2), ctypes.c_int, order="C")
                np_keyloc[0, 0:2] = [obj_int6loc] * 2
                np_totalblindmap = numpy.zeros(
                    (self.max_y_hexnum, self.max_x_hexnum), ctypes.c_int, "C"
                )
                self.utilitiesSo.warpRushMovingAction(
                    ctypes.byref(cur_bop), np_keyloc, np_totalblindmap, np_aiaction
                )
                np_aiaction = np_aiaction.astype(dtype=int)
                list_routes = list(np_aiaction[0, 3 : 3 + np_aiaction[0, 2]])
                assert len(list_routes) > 0
                if list_routes[-1] != obj_int6loc:
                    print("error in x")
                    pass
            return list_routes
        except Exception as e:
            common.echosentence_color("error in getRouteList:{}".format(str(e)))
            raise e

    """检查算子能否到达指定位置"""
    # @profile
    def canArrivePos(self, cur_bop, obj_int6loc):
        np_wicgMap = self.getWhereICanGoMap(cur_bop=cur_bop)
        obj_row, obj_col = common.cvtInt6loc2HexOffset(obj_int6loc)
        return np_wicgMap[obj_row, obj_col] >= 0

    """位置A到位置B的最短路径"""
    # @profile
    def getPath(self, int6loc1, int6loc2, maxDis):
        try:
            l_path = []
            bop = wgobject.BasicOperator()
            bop.ObjPos = int6loc1
            bop.ObjTypeX = 1
            bop.ObjType = 2

            np_path = numpy.zeros((1, maxDis), ctypes.c_int)
            self.utilitiesSo.warpGetPath(bop, int6loc2, maxDis, np_path)

            for i in range(maxDis):
                if np_path[0, i] > 0:
                    l_path.append(np_path[0, i])
            return l_path
        except Exception as e:
            common.echosentence_color(" " + str(e))
            self.__del__()
            raise
        except KeyboardInterrupt as k:
            common.echosentence_color(" " + str(k))
            self.__del__()
            raise

    # todo '''获取坦克算子对目标算子的所有攻击路径'''
    # @profile
    def getAttackRoutes4Tank(self, cur_att, cur_obj, max_routes=1000):
        """具体列的含义：参考cModules中的strategy.h 或者 __common.py文件
        modify：2018年12月04日 修复Bug：攻击路径过滤条件应同时不等于同格算子的行和列才过滤
        """
        try:
            assert cur_att.A1 == 1
            max_cols = 17
            np_2d_routesdata = numpy.zeros(
                (max_routes, max_cols), ctypes.c_float, order="C"
            )
            self.utilitiesSo.warpGetALLFFBTRoutes(
                ctypes.byref(cur_att),
                ctypes.byref(cur_obj),
                ctypes.c_int(max_routes),
                np_2d_routesdata,
            )
            # 获取无效数据（删除所有行都是0的元素）
            np_2d_routesdata = np_2d_routesdata[
                numpy.sum(np_2d_routesdata, axis=1) > 0.0
            ].astype(int)
            # 删除攻击位置满格机动力的攻击路线
            mask_0 = (
                np_2d_routesdata[:, common.FFBTMODE_SHOOTING_LEFTPOWER_A]
                < cur_att.ObjStepMax
            )
            # 删除让坦克陷入同格状态的攻击路径
            obj_row, obj_col = common.cvtInt6loc2HexOffset(cur_obj.ObjPos)
            mask_1 = (
                np_2d_routesdata[:, common.FFBTMODE_SHOOTING_ROW_A] != obj_row
            ) | (np_2d_routesdata[:, common.FFBTMODE_SHOOTING_COL_A] != obj_col)
            mask = numpy.logical_and(mask_0, mask_1)
            np_2d_routesdata = np_2d_routesdata[mask]
            return np_2d_routesdata

        except Exception as e:
            common.echosentence_color(
                "error in getAttackRoutes4Tank():{}".format(str(e))
            )
            raise e

    # @profile
    def checkBopGetArriveBecauseofTongge(self, cur_bop, int6loc, list_ubops):
        try:
            list_o2u_routes = self.getRouteList(cur_bop=cur_bop, obj_int6loc=int6loc)
            if list_o2u_routes is None:
                flag_ok = False
            else:
                list_ulocs = [bop.ObjPos for bop in list_ubops]
                list_o2u_routes = list_o2u_routes[0:-1]
                if (
                    len((set(list_ulocs) & set(list_o2u_routes))) == 0
                ):  # 中间路线上不与任何其他算子的位置重合
                    flag_ok = True
                else:
                    flag_ok = False
            return flag_ok
        except Exception as e:
            common.echosentence_color(
                "error in checkBopGetArriveBecauseofTongge():{}".format(str(e))
            )
            raise

        # todo get all possible (acyclic and cyclic) and  paths given startpoint S and endpoint E
        # 18-11-17 by gsliu
        # ref https://blog.csdn.net/dazhushenxu/article/details/77833023

    # @profile
    def get_all_movepaths(self, cur_bop, obj_int6loc):
        try:
            row_e, col_e = common.cvtInt6loc2HexOffset(obj_int6loc)
            # power checking
            assert cur_bop.ObjStep <= 8  # more power, more time-consuming
            np_wicg = self.getWhereICanGoMap(cur_bop)
            if np_wicg[row_e][col_e] < 0:
                np_dis_np = numpy.ones(np_wicg.shape, dtype=int) * 1000
                np_dis_cal_mask = np_wicg >= 0
                # ugly
                for row_tmp in range(np_dis_np.shape[0]):
                    for col_tmp in range(np_dis_np.shape[1]):
                        if np_dis_cal_mask[row_tmp][col_tmp]:
                            np_dis_np[row_tmp][col_tmp] = hex.getDisBy2tupleloc(
                                (row_tmp, col_tmp), (row_e, col_e)
                            )
                row_e, col_e = numpy.unravel_index(np_dis_np.argmin(), np_dis_np.shape)
            # find path
            list2_paths = []
            try:
                list2_paths = self.__find_dfs_paths(
                    int6loc_s=cur_bop.ObjPos,
                    int6loc_e=common.cvtHexOffset2Int6loc(row_e, col_e),
                    int_leftpower_s=cur_bop.ObjStep,
                    bop_type=cur_bop.ObjType,
                )
            except Exception as e:
                common.echosentence_color(
                    "\t something wrong when path searching", "white"
                )
                pass

            return list2_paths
        except Exception as e:
            common.echosentence_color("__wgcutility > get_acyclicpaths")
            raise e

        # 18-11-17 by gsliu
        # ref https://www.cnblogs.com/maydow/p/4839376.html
        # basicly just a DFS algorithm + hard-code tree pruning

    # @profile
    def __find_dfs_paths(self, int6loc_s, int6loc_e, int_leftpower_s, bop_type):
        try:
            # 3-tuple: level, leftpower, int6loc
            index_level, index_power, index_loc = range(3)
            first_node = (0, int_leftpower_s, int6loc_s)
            stack_t3_tree = [first_node]
            stack_t3_onepath = []
            list2_paths = []
            while stack_t3_tree:
                # update stack_t3_onepath
                t3_treenode = stack_t3_tree.pop()
                while stack_t3_onepath:
                    if stack_t3_onepath[-1][index_level] >= t3_treenode[index_level]:
                        stack_t3_onepath.pop()
                    else:
                        break
                stack_t3_onepath.append(deepcopy(t3_treenode))
                # update list2_paths
                if stack_t3_onepath[-1][index_loc] == int6loc_e:
                    list2_paths.append(deepcopy(stack_t3_onepath))
                # update stack_t3_tree
                row_cur, col_cur = common.cvtInt6loc2HexOffset(t3_treenode[index_loc])
                hex_curnode = hex.HEX_OFF(y=row_cur, x=col_cur)
                list_nextnodes = hex_curnode.getSpecifiedNeighFromDirList(range(6))
                for t2 in list_nextnodes:
                    int6loc_subnode = common.cvtHexOffset2Int6loc(t2[0], t2[1])
                    needpow = getEnterHexPower(
                        np_eptable=self.np_ep_table,
                        bop_type=bop_type,
                        src_int6loc=t3_treenode[index_loc],
                        des_int6loc=int6loc_subnode,
                    )
                    if t3_treenode[index_power] >= needpow:
                        # hard coding for pruning
                        dis = hex.getDisBy2int6loc(int6loc_e, int6loc_subnode)
                        willleftpower = t3_treenode[index_power] - needpow
                        if dis <= willleftpower:
                            stack_t3_tree.append(
                                (
                                    t3_treenode[index_level] + 1,
                                    willleftpower,
                                    int6loc_subnode,
                                )
                            )

            return list2_paths
        except Exception as e:
            common.echosentence_color("__wgcutility > __findpath")
            raise

    # todo 计算我方算子obop的视野盲区 即目标算子躲在哪些位置（0）不会被我方算子（所有）看到，在哪些位置可以被我方算子看到(1)
    # @profile
    @static_blindmap_decorator
    def get_staticobserve_blindmap_p2p(self, obop, ubop):
        try:
            obop = wgobject.op_deepcopy(obop)
            ubop = wgobject.op_deepcopy(ubop)
            basic_bt_ioumap = wgobject.BasicTensor()
            basic_bt_ioumap.ndim = ctypes.c_int(2)
            tmp_p_ints = (ctypes.c_int * basic_bt_ioumap.ndim)(
                self.max_y_hexnum, self.max_x_hexnum
            )
            basic_bt_ioumap.shape = ctypes.cast(
                tmp_p_ints, ctypes.POINTER(ctypes.c_int)
            )
            np_ioumap = numpy.zeros(
                (self.max_y_hexnum, self.max_x_hexnum), ctypes.c_int, order="C"
            )
            # np_ioumap = numpy.ascontiguousarray(np_ioumap)
            p_np_ioumap = np_ioumap.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
            basic_bt_ioumap.data = p_np_ioumap
            # flag_mode = 0 if not self.flag_gpu else 2
            flag_mode = 0
            self.utilitiesSo.warpGetMyIouMap(
                ctypes.c_int(flag_mode),
                ctypes.byref(obop),
                ctypes.byref(ubop),
                ctypes.byref(basic_bt_ioumap),
            )  # bop_obj不会被看到的位置标记为0，否则标记为1
            return np_ioumap

        except Exception as e:
            common.echosentence_color(
                "error in get_staticobserve_blindmap_p2p():{}".format(str(e))
            )
            raise

    # todo get_staticobserve_blindmap_p2p（）函数的动态版本（我方算子是坦克）
    # @profile
    @dynamic_blindmap_decorator
    def get_dynamicobserve_blindmap_p2p(self, obop, ubop):
        try:
            obop = wgobject.op_deepcopy(obop)
            ubop = wgobject.op_deepcopy(ubop)
            # assert obop.A1 == 1
            # print '\tget_staticobserve_blindmap_p2p()'
            basic_bt_ioumap = wgobject.BasicTensor()
            basic_bt_ioumap.ndim = ctypes.c_int(2)
            tmp_p_ints = (ctypes.c_int * basic_bt_ioumap.ndim)(
                self.max_y_hexnum, self.max_x_hexnum
            )
            basic_bt_ioumap.shape = ctypes.cast(
                tmp_p_ints, ctypes.POINTER(ctypes.c_int)
            )
            np_ioumap = numpy.zeros(
                (self.max_y_hexnum, self.max_x_hexnum), ctypes.c_int, order="C"
            )
            # np_ioumap = numpy.ascontiguousarray(np_ioumap)
            p_np_ioumap = np_ioumap.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
            basic_bt_ioumap.data = p_np_ioumap
            # flag_mode = 0 if not self.flag_gpu else 2
            flag_mode = 0
            # bop_obj不会被看到的位置标记为0，否则数值>0
            self.utilitiesSo.warpGetMyIouDynamicMap(
                ctypes.c_int(flag_mode),
                ctypes.byref(obop),
                ctypes.byref(ubop),
                ctypes.byref(basic_bt_ioumap),
            )
            return np_ioumap

        except Exception as e:
            common.echosentence_color(
                "__wgutility > get_dynamicobserve_blindmap_p2p():{}".format(str(e))
            )
            raise

    # todo 获取观察算子[l_observer_bops]对给定被观察目标[move_bop]的观察视野盲区: [是盲区 1 不是盲区 0]
    # @profile
    def _get_observeblind_map(
        self,
        l_observer_bops,
        move_bop,
        flag_static=False,
        np_alltrue_mask=None,
        np_allfalse_mask=None,
    ):
        # where i can hide based on np_wicg_map, np_true_mask, np_allfalse_mask  : 1 yes 0 no
        try:
            # calculate
            np_totalblindmap = numpy.zeros(
                (self.max_y_hexnum, self.max_x_hexnum), ctypes.c_int, "C"
            )
            for observer_bop in l_observer_bops:
                if (not flag_static) and observer_bop.A1 == 1:  # observer bop is tank
                    numpy.add(
                        np_totalblindmap,
                        self.get_dynamicobserve_blindmap_p2p(observer_bop, move_bop),
                        np_totalblindmap,
                    )
                else:
                    numpy.add(
                        np_totalblindmap,
                        self.get_staticobserve_blindmap_p2p(observer_bop, move_bop),
                        np_totalblindmap,
                    )
            # type convert
            np_totalblindmap = np_totalblindmap.astype(dtype=int)
            # mask filter
            if np_alltrue_mask is not None:
                np_totalblindmap[np_alltrue_mask] = 0
            if np_allfalse_mask is not None:
                np_totalblindmap[np_allfalse_mask] = 1
            np_totalblindmap[np_totalblindmap != 0] = 1
            np_totalblindmap = 1 - np_totalblindmap
            return np_totalblindmap
        except Exception as e:
            common.echosentence_color(
                "CUtility > _get_observeblind_map():{}".format(str(e))
            )
            raise e

    # todo 给定观察算子列表和待机动算子，计算待机动算子在指定位置上的暴露程度[0-3000]
    # @profile
    def _get_exposed_map(self, l_observer_bops, move_bop, np_candidate_mask):
        # 只计算指定位置的暴露程度: np_candidate_mask 1 yes, 0 no
        # np_candidate_mask: very important
        try:
            # init bops
            move_bop = wgobject.op_deepcopy(move_bop)
            l_observer_bops = [wgobject.op_deepcopy(bop) for bop in l_observer_bops]
            pso_ubop = wgobject.op_deepcopy(move_bop)
            pso_ubop.GameColor = 1 - move_bop.GameColor
            # calc attack direction
            tuple_u_center = common.getBopCenterLocs(l_observer_bops)
            if tuple_u_center != (-1, -1):
                pso_ubop.ObjPos = common.cvtHexOffset2Int6loc(
                    tuple_u_center[0], tuple_u_center[1]
                )
                attack_dir = common.com_attackdir(
                    att_int4loc=common.cvtInt6loc2Int4loc(pso_ubop.ObjPos),
                    obj_int4loc=common.cvtInt6loc2Int4loc(move_bop.ObjPos),
                )
            else:
                # default attack direction based my color: red 0 blue 3
                attack_dir = 3 if move_bop.GameColor == 1 else 0

            # calclulate attack zone
            np_2d_dirzone_mask = self.getDirZoneMaskMap(
                att_int4loc=common.cvtInt6loc2Int4loc(pso_ubop.ObjPos),
                obj_int4loc=common.cvtInt6loc2Int4loc(move_bop.ObjPos),
                attack_dir=attack_dir,
            )
            # calculate exposed map
            np_exposed_map = (
                numpy.ones((self.max_y_hexnum, self.max_x_hexnum), dtype=int) * 3000
            )
            candidate_locs_y, candidate_locs_x = numpy.where(np_candidate_mask > 0)
            for (y, x) in zip(candidate_locs_y, candidate_locs_x):
                move_bop.ObjPos = common.cvtHexOffset2Int6loc(row=y, col=x)
                np_2d_ioumap_mask = self.get_staticobserve_blindmap_p2p(
                    move_bop, pso_ubop
                )
                np_final_mask = numpy.logical_and(np_2d_ioumap_mask, np_2d_dirzone_mask)
                np_exposed_map[y][x] = numpy.sum(np_final_mask == True)

            # common.echosentence_color(
            #     u"\t暴露程度的最小数值[{}], 最小数值所在位置[{}]".format(
            #         numpy.min(np_exposed_map), numpy.where(numpy.min(np_exposed_map))
            #     ),
            #     "white",
            # )
            return np_exposed_map
        except Exception as e:
            raise e

    # todo 给定观察算子列表和待机动算子，取出对方视野盲区和待机动算子的机动范围的交集，作为待机动算子的候选落脚点集合
    # @profile
    def _gen_hidemap_4_bop(
        self,
        l_observer_bops,
        move_bop,
        flag_static,
        flag_danger=False,
        list_danger_locs=[],
    ):
        # where i can hide based on my wicg map : 1 yes 0 no
        try:
            # calculate where i can go map
            np_wicg_map_mask = self.getWhereICanGoMap(move_bop)
            np_wicg_map_mask[np_wicg_map_mask >= 0] = 1
            np_wicg_map_mask[np_wicg_map_mask < 0] = 0
            # calculate np_allfalse_map
            np_allfalse_mask = numpy.zeros(
                (self.max_y_hexnum, self.max_x_hexnum), dtype=int
            )
            if flag_danger and list_danger_locs:
                for cur_int6loc in list_danger_locs:
                    row, col = common.cvtInt6loc2HexOffset(cur_int6loc)
                    np_allfalse_mask[row][col] = 1
            np_allfalse_mask = np_allfalse_mask == 1
            # calculate your blind map mask
            np_blind_map_mask = self._get_observeblind_map(
                l_observer_bops=l_observer_bops,
                move_bop=move_bop,
                flag_static=flag_static,
                np_allfalse_mask=np_allfalse_mask,
            )

            np_hide_map = numpy.zeros((self.max_y_hexnum, self.max_x_hexnum), dtype=int)
            np_hide_map[numpy.logical_and(np_wicg_map_mask, np_blind_map_mask)] = 1
            return np_hide_map

        except Exception as e:
            common.echosentence_color(
                "CUtility > _gen_hidemap_4_bop():{}".format(str(e))
            )
            raise e

    # @profile
    def _gen_dismap_4_bop(self, cur_bop, obj_pos):
        try:
            np_wicg_map_mask = self.getWhereICanGoMap(cur_bop)
            np_wicg_map_mask[np_wicg_map_mask >= 0] = 1
            np_dis_map = (
                numpy.ones((self.max_y_hexnum, self.max_x_hexnum), dtype=int) * 3000
            )

            candidate_locs_y, candidate_locs_x = numpy.where(np_wicg_map_mask == 1)
            for (y, x) in zip(candidate_locs_y, candidate_locs_x):
                np_dis_map[y][x] = hex.getDisBy2int6loc(
                    obj_pos, common.cvtHexOffset2Int6loc(y, x)
                )

            return np_dis_map
        except Exception as e:
            common.echosentence_color(
                "CUtility > _gen_dismap_4_bop():{}".format(str(e))
            )
            raise e

    """出现异常或者程序退出时需要释放资源"""
    # @profile
    def releaseUtilitiesSo(self):
        try:
            if self.utilitiesSo is not None:
                # 'AI 释放动态特征链接库'
                common.echosentence_color("AI release so memory", "white")
                self.utilitiesSo.warpFreeMapAttr()
                self.utilitiesSo = None
            else:
                print("AI so memory have been released")
        except Exception as e:
            print("error in releaseUtilitiesSo(): {}".format(str(e)))
            raise ValueError(e)

    def __del__(self):
        if not CUtility.static_blindmap_decorator.frozen:
            CUtility.static_blindmap_decorator.save_cache()
        if not CUtility.dynamic_blindmap_decorator.frozen:
            CUtility.dynamic_blindmap_decorator.save_cache()
        CUtility.static_blindmap_decorator.log()
        CUtility.dynamic_blindmap_decorator.log()
        self.releaseUtilitiesSo()
        

    def printTime(self):
        pass


if __name__ == "__main__":
    pass
