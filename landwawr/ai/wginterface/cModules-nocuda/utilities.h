/*
 *  2017年5月5日/gsliu/PAL_Wargame
 *  基本功能：
 *    封装所有与python进行交互的函数
 *  更新：
 *    2017年5月5日：  建立文档/判断任意两个六角格上的通视算法 tsIsOk()函数
 *    2017年5月6日：  封装map.h 中的initMapAttr() / freeMapAttr()到对应的warpInitMapAttr/ warpFreeMapAttr中
 *		      测试函数 warpTestMapAttr()
 *		      封装map.h 中的initMapEdgePower / freeMapEdgePower()函数
 *		      测试函数 warTestMapEdgePower()
 *    2017年5月7日：  定义基本张量结构体 struct BasicTensor（与python中的数据对应，用来和python交换特征数据）
 *		      增加读取python中的struct BasicWeapen的warpTestReadBasicWeapon()
 *		      增加读取python中的struct BasicOperator的warpTestReadBasicOperator()
 *		      增加从python中读取struct BasicOperator对象指针，并生成该对象的icuMap地图 warpGetMyIcuMap()
 *    2017年5月8日：  封装map.h中的机动范围函数 whereICanGoMap函数为warpGetMyWhereICanGoMap()
 *    2017年5月10日： 更正warpGetMyIcuMap 根据张量维度进行自适应扩展py_p_bt.shape， 张量数据扩展到三维，对人对车两种地图
 *    2017年5月10日:  函数 计算算子的攻击等级地图函数 warpGetMyAttackLevelMap()
 *		      基本思路： 算子车班数目 + 算子武器列表 ==> 计算生成多少张地图 
 *		      ==> 依次从武器列表中选择武器，并根据车班数目填充到对应的地图中
 *			按照武器类型计算计算算子可生成的攻击等级地图数量方法：
 *			cur_wz_tartype = getSpecifiedWeaponTartype(py_p_bop,i) 算子第i件武器的攻击类型 0不限 2对车
 *			武器攻击类型==0的武器数量n0 
 *			武器攻击类型==2的武器数量n2
 *			总地图数量n = n0 * 2 + n2;
 *    2017年5月16日： 根据算子的攻击等级maps计算对应的损伤等级
 *		    函数 warpGetMyDamageLevelMap(), 内部封装judge.c/h中的damagelevelMap()函数
 *    2017年5月17日： 函数 warpInitDamageTable() 初始化judge.c/h中的三个全局变量战损表格
 *    2017年5月25日： 函数 warpFFBTOptMap() 封装judge.c/h中的ffbtOptMap函数
 *    2017年5月31日： 底层数据类型dictionary GA 变化导致进行的修改
 *    2017年6月1日：  封装 trendpathP2P()函数，绘制A->B的路径 warptrendpathP2P()
 *    2017年6月6日：  RUSHAI点对点估计射击效果的函数 warpRushDamageLevelP2P(), 内部封装rushAiDamageLevelP2P()
 *	            RUSHAI寻找到达指定目标路径中的单步移动位置 warpRushOptNextRoute() , 内部封装rushAiOptNextRoute()
 *    2017年7月27日： 将与AI动作有关的策略函数从feature.h/c中分离出来，放到strategy.h/c中
 *    2017年7月27日： 将FFBT和DA模块中挑选出来的最优路径转化成为有效动作，和python部分定义相同的动作字段
 *		    合并warpFFBTOptMap和warpRushDamageLevelP2P两个函数，按照下面的流程增补函数
 *		    c ==> DA/FFBT（模型选择）
 *			  ==>最优路径选择(getBest*Route系列函数)
 *			  ==>python可识别的动作字段转化(分析每个模块的输出，结合python 的需求)
 *			  ==>python 
 *
 *   2017年7月30日： 合并FFBT，DA模型，静态射击为一个函数，warpMSAction()==> 输出AI可识别的动作字段
 *   2017年8月8日：  封装iouIsOk()，在python中判断算子A能否观察到算子B，
 *		     以便提前剔除掉我方所有算子都不能看到的敌方算子（基于共享视野考虑问题）==> warpIouIsOk()函数
 *		     另外，去掉warpMSAction()中需要提前判断是否可观察的模型调用的先决条件;
 *   2017年8月15日： 更新warpMSAction()函数，在调用DA模型前先检查是否能原地（静态）射击的函数checkStaticShooting()
 *		     如果无行射能力算子原地射击占据优势，不在调用DA模型。本时节（我方机动）直接输出无动作；
 *   2017年8月16日： 更新warpInitMapAttr()，适应initMapAttr()的接口变化
 *   2017年8月16日： 增加函数warpWhereICanPassRangeGA()，计算行军状态下的机动范围
 *   2017年8月17日： 更新warpRushDamageLevelP2P()纯机动函数，在内部加入行军，躲避对方算子，观察对方算子的算法实现,需要考虑行军命令
 *   2017年8月23日： 封装feature.h/c中的iouRange() 为 warpGetMyIouMap()函数
 *   2017年9月7日 ： 封装feature.h中的damageMapP2P() 为 warpGetMyDamageMap()函数
 *   2017年12月6日： 封装getOccupyingRoutes等夺控系列函数warpOccupyAction()
 *   2017年12月11日： 封装getDARoutes**反击模型为两个模块 warpDA00SMAction()/ warpDA01SMAction()
 *   2017年12月12日： 封装守城模型DC00系列 warpDC00Action()
 *   2018年3月5日：   封装cuda-c的并行特征计算程序
 *   2018年3月24日: 特征图的封装函数加入 flag_mode标记使用的计算模式:0 C-COM/ 1:C-CACHE/ 2:GPU-CACHE
 *   2018年6月21日： 增加GPU生成动作和特征的函数模块(宋国瑞)
 *
 *
 */

#include <time.h>     /* time */
#include <stdlib.h>   /* rand() */
#include <locale.h>  /*setlocale(LC_ALL, "");*/
#include "feature.h"  /* 特征计算函数 */
//#include "feature_cu.h" /*基于cuda-c的并行特征函数*/
#include "strategy.h" /*动作输出函数 */
//#include "strategy_cu.h" /*sgr GPU ==》feaure / action */

extern bool g_flag_graphicmem_ok;
/*------------------------------------------初始化/资源释放/数据测试相关的函数------------------------------------------*/
/*------------------------------------------初始化/资源释放/数据测试相关的函数------------------------------------------*/

/*
 *  封装：map.h中的initMapAttr()函数，与warpFreeMapAttr()对应
 *  输入参数  const void * py_p_geodata (int* 类型) 从python传来的地图属性数据（以一维指针的形式)
 *	      const void *py_p_epdata 单边机动力消耗数据
 *	      const void *py_p_roadnet 道路网（图）的邻接矩阵
 *	      const void *py_p_wptable 武器属性表
 *	      const int py_georows
 *	      const int py_geocols
 *	      const int py_eprows
 *	      const int py_epcols
 *	      const int py_rdnetrows
 *	      const int py_rdnetcols
 *	      const int py_wprows
 *	      const int py_wpcols
 *
 *  注意  
 *    要保证py_p_geodata py_p_epdata, py_p_roadnet的数据连续性质
 *    2018-03-06： 初始化模块中加入cudaInit()
 */

void warpInitMapAttr(const void *py_p_geodata, const void * py_p_epdata, const void* py_p_roadnet, const void *py_p_wptable, const int py_georows, const int py_geocols, const int py_eprows, const int py_epcols, const int py_rdnetrows, const int py_rdnetcols, const int py_wprows, const int py_wpcols);


/* 初始化judge.c/h中的三个战损表格
 * 输入参数：从python中传过来的三个三维numpy对象 维度分别为 125*11*10 / 25*11*10 / 5*11*10
 * 将三维数组直接作为成为一维数组使用，数据直接覆盖
*/

void warpInitDamageTable(const void * py_p_damagetable_zm2car, const void * py_p_damagetable_ltf2car, const void * py_p_damagetable_allw2people);

/*
 *  函数说明：初始化与地图相关的缓存数据
 *  输入参数：const void * py_p_1d_icutable, const int len_icu通视表的元素与长度
 *	      const void * py_p_1d_wicgtable, const int len_wicg机动范围的元素与长度
 *	      const void * py_p_1d_distable , const int len_dis 距离表的元素数据与长度
 *  输入参数：void 
 *  返回参数：void 
 *  注意事项：扩展其他的缓存表格，如机动范围表格
 *
 * */

void warpInitCacheData(const void * py_p_1d_icutable, const int len_icu,  const void * py_p_1d_wicgtable, const int len_wicg,  const void * py_p_1d_distable , const int len_dis );


/*
 * 释放struct Map_Attr占据的内存
 * 输入参数： struct Map_Attr * p_map_attr
 * 主要释放： 位置-行索引字典，地图属性数据
 */

void warpFreeMapAttr();

/*
 *  测试模块，测试全局变量g_map_attr是否被正确初始化
 *    打印全局变量g_map_attr的各项信息
 *  注意
 *    需要在warpInitMapAttr()函数之后调用
 */

void warpTestMapAttr();


//  *  函数说明: 初始化显存中的全局变量
//  *  输入参数:
//  *  输出参数:
//  *  返回参数: bool 显存数据是否初始化成功
//  *  注意事项: 0 返回数值用来更新g_flag_graphicmem_ok标志
//  *	      1 如果python想要使用显存-缓存模式,必须保证g_flag_graphicmem_ok == true;
//  *
//  *
//  * 

// bool warpCudaInit(const int num_rbops, const int num_bbops, const int num_city);

/*  测试函数：测试武器
 *  python中传入算子的p_obj_wpids的方法：
 *    数组类型 --> 数组变量 --> 变量赋值
 *    数组作为参数传入，参数类型为ctypes.POINTER(c_int)
 *
 *
 */
void warpTestWeaponData(const struct BasicOperator *py_p_bopa);



/*-------------------------特征图相关的计算函数：观察范围/机动方位/行军范围/攻击等级/战损范围图等：C缓存/显存-缓存模式下--------------------*/
/*-------------------------特征图相关的计算函数：观察范围/机动方位/行军范围/攻击等级/战损范围图等：C缓存/显存-缓存模式下--------------------*/

/*
 * 生成一个BasicOperator的icuMap, 不通视位置标注-1，通视位置标注该位置到中心点的距离
 * 输入参数 const struct BasicOperator *py_p_bop
 * 输出参数 const struct BasicTensor *py_p_bt(将icuMap填充到py_p_bt->data中)
 */

void warpGetMyIcuMap(const struct BasicOperator *py_p_bop, struct BasicTensor *py_p_bt);

/*
 * 计算算子B位于哪些位置上能够被算子A看到
 * 输入参数：
 *  const int flag_mode 0 C计算模式 1 C缓存模式 2 显存-缓存模式
 *  const struct BasicOperator *py_p_bopa, py_p_bopb
 * 输出参数：
 *  const struct BasicTensor *py_p_bt
 * 注意：0 内部封装iouRange()函数
 *	 1 C计算模式/C缓存模式自动选择
 *	 
 */

void warpGetMyIouMap(const int flag_mode, const struct BasicOperator *py_p_bopa, const struct BasicOperator *py_p_bopb, struct BasicTensor *py_p_bt);

/*
 *  计算算子B对于坦克A的暴露程度：动态的warpGetMyIouMap()函数； 内部封装的是iouDynamicRange()
  * 输入参数：
 *    const int flag_mode 0 C计算模式 1 C缓存模式 2 显存-缓存模式
 *    const struct BasicOperator *py_p_bopa, py_p_bopb
 *  输出参数：
 *    const struct BasicTensor *py_p_bt
 *  注意：
 *	0 内部封装iouDynamicRange()函数
 *	1 C计算模式/C缓存模式自动选择
 * */

void warpGetMyIouDynamicMap(const int flag_mode, const struct BasicOperator *py_p_bopa, const struct BasicOperator *py_p_bopb, struct BasicTensor *py_p_bt);

/*
 *  封装cudaIouMap()
 *  输入参数：const struct BasicOperator * py_p_bopa, py_p_bopb目标算子
 *  输出参数： struct BasicTensor * py_p_bt 地图张量数据
 */

// void warpCudaIouMap(const struct BasicOperator * py_p_bopa, const struct BasicOperator * py_p_bopb,  struct BasicTensor * py_p_bt);

/*
 *  函数说明：计算攻击算子对目标算子的攻击等级图张量（遍历攻击算所有的武器）
 *  输入参数：
 *	      const int flag_mode 0 C计算模式 1 C缓存模式 2 显存-缓存模式
 *	      const struct BasicOperator * py_bop_att
 *	      const struct BasicOperator * py_bop_obj
 *  输出参数：struct BasicTensor * py_p_bt(返回的是N维张量,N==攻击算子的武器数)
 *  返回数值：void
 *  注意事项：1 攻击算子的武器数量==特征图数量
 *	      2 针对目标算子的无效武器，特征图的数值为0，但是特征图存在
 *	      3 加快计算，提前检查武器类型与目标类型匹配问题
 *	      
 * */
void warpGetMyAttacklevelMap(const int flag_mode, const struct BasicOperator * py_bop_att, const struct BasicOperator * py_bop_obj, struct BasicTensor * py_p_bt);


/* 计算点对点的战损（区分warpGetDirectDamageP2P()函数）
 * 输入参数：
 *  攻击算子 py_p_bopa
 *  目标算子 py_p_bopb
 * 输出参数：
 *  战损（0 / damage * bop_value ）
 * 注意：
 *  区分算子有无可行射能力的问题： 如果攻击算子由行射能力，需要检查攻击算子在其机动范围内所有位置上对目标算子的射击情况，如果只进行单点计算，使用warpGetDirectDamageP2P()函数
 *  只要调用该函数，默认攻击算子在外部态势中的状态符合兵棋中的射击规则
 *  只要调用该函数，默认攻击算子A已经能够确定出目标算子B的具体位置（直接看到，队友看到，预测等方法！）
 */

void warpGetDamageP2P(const struct BasicOperator *py_p_bopa, const struct BasicOperator *py_p_bopb, void *p_damage);


/*
 *  计算点对点算子的战损（区分warpGetDamageP2P()函数）
 *  输入参数：攻击算子和目标算子
 *  输出参数：damage > 0 存在战损，否则=0
 *  注意事项：计算的是直接攻击战损!
 *
 * */

void warpGetDirectDamageP2P(const struct BasicOperator *py_p_bopa, const struct BasicOperator *py_p_bopb, void *p_damage);


/*
 * 封装damageMapP2P函数
 * 输入参数：
 *  const struct *py_p_bopa, py_p_bopb 攻击算子与目标算子
 * 输出参数：
 *  void * p_damagemap (float*类型) python 传过来的张量数据
 * 注意:该函数返回1张综合战损图,warpGetAllDamageMap()返回夺张战损图(张量数据类型)
 * 修正：只计算目标算子机动范围可达的位置，其余位置设置为100，节省时间;
 */

void warpGetMyDamageMap(const struct BasicOperator *py_p_bopa, const struct BasicOperator* py_p_bopb, void * p_damagemap);

/*
 *  函数说明:计算攻击算子对目标算子的多张战损特征图,区别warpGetMyDamageMap()函数
 *  输入参数: 攻击算子/目标算子: py_p_bopa / py_p_bopb
 *
 *	      const int flag_mode 0 C计算模式 1 C缓存模式 2 显存-缓存模式
 *  输出参数: py_p_bt
 *  返回参数: void
 *  注意事项: 1 内部参数化c/cuda-c的计算模块
 *	      2 区分warpGetMyDamageMap() 函数
 *
 * */
void warGetAllDamageMap(const int flag_mode, const struct BasicOperator *py_p_bopa, const struct BasicOperator *py_p_bopb, struct BasicTensor * py_p_bt);

/*
 * 生成python传入的算子BasicOperator的机动范围地图 whereICanGoMap
 * 输入参数： const struct BasicOperator &py_p_bop 获取位置信息以及初始机动力
 * 输出参数： struct BasicTensor *py_p_bt， 将whereICanGoMap填充到py_p_bt的data中
 * KEY0: 算子从A到B的机动力消耗：只针对车辆算子，人员算子无效!
 */

void warpGetMyWhereICanGoMap(const struct BasicOperator *py_p_bop, struct BasicTensor *py_p_bt);

/*
 * 封装行军状态的机动范围whereICanPassRangeGA()函数
 * 输入参数：const struct BasicTensor *py_p_bop
 * 输出参数：const struct BasicTensor *py_p_bt
 *
 */
void warpGetMyICanPassMap(const struct BasicOperator *py_p_bop, struct BasicTensor *py_p_bt);

/*
 *  测试函数：按照方位和距离区间划分地图和机动范围
 *  输入参数： 
 *    const struct BasicOperator *py_p_bop
 *    const int dir, mindis, maxdis 
 *  输出参数：
 *    struct BasicTensor *py_p_bt; 
 *  注意事项：
 *    1 中间调用了map.h/c中的getCandidateScoutlocs()函数
 *    2 mindis >=1 && maxdis <= p_bop.obj_step, 在外部调用时候需要进行检查
 *  
 *    
 * */

void warpGetDirRegionMap(const struct BasicOperator *py_p_bop, const int dir, const int mindis, const int maxdis, struct BasicTensor *py_p_bt);



/*--------------------------与AI动作引擎相关的函数------------------------------------*/
/*--------------------------与AI动作引擎相关的函数------------------------------------*/

/*
 * 函数说明： 判断位置A/B之间是否可视（0不可/1可以）
 * */
void warpGetMyIcuFlag(const int cen_row, const int cen_col, const int cur_row, const int cur_col, const int maxdis, void * py_p_int_flag);

/*
 *  函数说明：计算从A点到B点需要消耗的机动力
 *  输入参数： 初始位置和目标位置, 算子类型
 *  输出擦树： 中间消耗的机动力（和地形相关，和算子类型无关，是地图的一部分）
 *  返回参数： 无
 *  注意事项：
 *      KEY0: 人员算子：最小机动力为距离
              车辆算子：如果存在机动力消耗缓存表并且缓存表可用，使用缓存表；否则需要预先计算整张图的机动力消耗（计算量过大）
 * */

// void warpGetMinPowConsume(const int int6loc_a, const int int6loc_b, void *py_p_int_powcon);

/*
 * 封装iouIsOk()，直接在python中判断算子之间是否通视（这样可以绕过可视范围的问题，避免做多余计算）
 * 输入参数：
 *  const struct BasicOperator *py_p_bopa, py_p_bopb
 * 输出参数：
 *  void * py_p_int_flag 如果算子bopa能够观察到bopb,返回1 否则返回0
 */

void warpIouIsOk(const struct BasicOperator *py_p_bopa, const struct BasicOperator * py_p_bopb, void *py_p_int_flag);


/*
 * 为当前算子找到合适的隐藏位置
 * 输入： 当前算子py_p_obj
 *	  np_viewblinddata; 对方所有算子针对当前算子的视野盲区，当前算子在0位置标识不会被对方发现，非0位置会被对方看到
 * 输入： void * 返回最近的隐藏位置（不会被对方所有位置看到）
 *
 */

void warpGetNHideLoc(const struct BasicOperator* py_bop_obj, void * np_viewblinddata, void *py_int_hideloc);

/*
 *  给定对方所有算子对我方算子的联合战损图,为我方算子找出最优的躲避位置
 *  输入参数：
 *    const struct BasicOperator *py_p_bop
 *    void * py_p_damagemap 对方算子对我方的联合战损(float类型)
 *    const int len 找出最优和次优的两个位置
 *  输出参数：
 *    void * 位置数组 py_p_locs , 长度为len
 *  注意; 
 *    len > 1(目前取值2，为了保证算子不发生堆叠现象)
 *    如果两个位置的战损相同，选择机动消耗最小的位置
 */
void warpGetMinDamgageLoc(const struct BasicOperator *py_p_bop, void *py_p_damagemap, const int len, void * py_p_locs);

/*
 * 封装trendpathP2P()函数， 算子py_p_bopa到py_p_bopb的全局路径以及基于机动力的局部路径(最优路径特征)
 * 输入参数： py_p_bopa, py_p_bopb
 * 输出参数： py_p_bt
 * 注意： py_p_bt->data为单通道图像，路径上的数据标识剩余机动力量>=0,注意全局路径中不满足剩余机动力的格子仍然设置=0，保证可视化
 */
void warptrendpathP2P(const struct BasicOperator *py_p_bopa, const struct BasicOperator *py_p_bopb, struct  BasicTensor *py_p_bt);


/*
 * 封装合并FFBT/静态射击2个函数，关键在于调用struct.c/h中的哪个函数 => 输出AI可识别的动作（各个字段定义在struct.h中）
 * 输入参数：
 *  const struct BasicOperator *py_p_attacker
 *  const struct BasicOperator *py_p_obj
 *  const int flag_ss 调用静态射击标志位 1(内部调用struct.h中cvtStaticShooting2AIAction函数) 
 *				      0 ==> 算子属性 选择getDA 或 getFFBT系列函数 ==> getBest* ==> cvt**Route2Action() => 动作字段
 *  void * p_uniondamage_map 对方剩余算子对我方算子的最大战损图
 *  void * p_blindareadata 敌方算子的累积盲区（记录我方算子在指定位置能够对方多少个算子看到）
 * 输出参数：
 *  void * p_aiaction (字段的定义存放在struct.h中)
 */

void warpMSAction(const struct BasicOperator *py_p_attacker,  const struct BasicOperator *py_p_obj, const int flag_ss, const int flag_task, void * p_uniondamage_map, void *p_totalblind_map, void *p_aiaction);

/*
 *  2018-10-21
 *  从warpMSAction()函数中单独抽离坦克算子的机动-射击-机动的功能动作，结合新的规则（倪老师的反坦克斜面/有效躲避点等）
 *  输入参数：
 *    const struct BasicOperator *py_p_att， py_p_obj 攻击算子和目标算子(float类型)
 *    void * p_uniondamage_map 对方剩余算子对我方算子的最大战损图（int类型）
 *    void * p_blindareadata 敌方算子的累积盲区（记录我方算子在指定位置能够对方多少个算子看到）
 *  输出参数：
 *    void * p_aiaction(生成的动作)
 * */

// void warpTankMsAction(const struct BasicOperator *py_p_att, const struct BasicOperator *py_p_obj, void * p_uniondamage_map, void * p_totalblind_map, void *p_aiaction);

/*  
 *  2018-10-21
 *  封装getALLFFBTRoutes()函数，获取坦克对目标算子的所有攻击路线，返回给python中（攻击路径的选择，放在python中调整）
 *  输入参数：
 *    py_p_att, py_p_obj 攻击算子和目标算子（攻击算子必须是坦克）
 *    const int max_routes_num 返回的最长攻击路线的条数目（默认是10000）
 *  输出参数：
 *    void * p_2d_routesdata 大小是max_routes_num * FFBTMODE_ELELEN(整数类型)
 *  注意事项：
 *    1 所返回的攻击路线中的元素不是都是有效元素，具体参考getALLFFBTRoutes()
 *    2 本函数返回有效的攻击路径：能够攻击对方算子的路径 【getALLFFBTRoutes()返回的是所有的路径】
 *
 * */
void warpGetALLFFBTRoutes(const struct BasicOperator * py_p_att, const struct BasicOperator* py_p_obj, const int max_routes_num, void * p_2d_routesdata);

/*
 *  函数说明：直接定义原地射击动作，内部调用cvtStaticShooting2AIAction()函数
 *  输入参数： py_p_attacker, py_p_obj, 攻击算子/目标算子
 *  输出参数： (void* p_aiaction)  使用时需要转换为float*类型 
 *  注意事项：
 *    0 能够射击：返回原地射击(action_type = 2)的动作标记， 不能射击返回无效动作
 *    1 不需要像warpMSAction()一样输入更多的规则参数！
 * */

void warpDirectShootAction(const struct BasicOperator *py_p_attacker, const struct BasicOperator *py_p_obj, void * p_aiaction);

/* 封装struct.h中的纯机动动作 cvtRushMoving2AIAction()便于直接调用（外部直接判断无有效的MS动作，进一步确定是否可执行RUSHMOVE动作时候使用）
 * 输入参数：
 *  const struct BasicOperator *py_p_attacker
 *  void *p_keyloc 长度为2的整形数组，0： global_key6loc 算子移动的全局目标位置；1： stage_key6loc  算子移动的阶段目标位置
 *  void *p_sawcount_map 更新全局被发现变量
 * 输出参数：
 *  float * p_aiaction
 * 注意：模块需要选择目标（全局还是阶段），以何种方式达到（机动还是行军）并将动作转化成为AI可识别的字段指令p_aiaction
 */
 

void warpRushMovingAction(const struct BasicOperator *py_p_attacker, void * p_keyloc,  void * p_sawcount_map, void* p_aiaction);


/*
 * 封装DA模型，DA模块以射击动作为驱动，输出机动动作，因此没有封装在warpMSAction()中
 * 输入参数：
 *  const struct BasicOperator * py_p_attacker (不载人战车/人员等无法机动射击的算子)
 *  const struct BasicOperator * py_p_obj 目标算子
 *  const int flag_task （0 进攻/1 防守）
 *  void * p_uniondamage_map  敌方算子对我方的统一战损图(区别战损/reward: 后者考虑了算子的分数)
 *  void * p_totalblind_map
 *  const int aiaction_len  编码数组的长度
 * 输出参数：
 *  void * p_aiaction
 * 注意事项：
 *  该模块以射击动作为驱动，输出无行射能力算子（无人战车/人员算子）的反击动作，输出的是纯机动模型
 */

void warpDA00SMAction(const struct BasicOperator *py_p_attacker, const struct BasicOperator *py_p_obj, const int flag_task , void * p_uniondamage_map, void * p_totalblind_map, void * p_aiaction);



/*
 * 封装DA01模型
 * 输入参数：
 *    const struct BasicOperator * py_p_attacker(载人战车)
 *    const struct BasicOperator * py_p_peo (战车上的人员算子)
 *    const struct BasicOperator * py_p_obj (目标算子)
 *    const int flag_task (0/1/2) 进攻/防御/撤退
 *    void * p_uniondamage_map 对方算子对我方当前算子py_p_attacker的综合战损图
 *    void * p_totalblind_map 对方算子的视野盲区
 *    const int aiaction_len 编码长度
 * 输出参数：
 *    void * p_aiaction
 * 注意事项：
 *    动作编码为下车3/下车机动8/机动下车7/机动下车机动9:四种类型
 *    reward包含obj_value
 *    类比： warpDA00SMAction()
 * */


void warpDA01SMAction(const struct BasicOperator *py_p_attacker, const struct BasicOperator * py_p_peo, const struct BasicOperator *py_p_obj, const int flag_task , void * p_uniondamage_map, void * p_totalblind_map, void * p_aiaction);

/*
 *  封装守城模型： getDC00Routes -》 getBestDCRoute --> cvtDCRoute2Aiaction
 *  输入参数：
 *    const struct BasicOperator * py_p_bop
 *    const int city_loc6
 *    const float city_value
 *    void * p_totaldamage_map
 *  输出参数:
 *    void p_aiaction
 *  注意事项：
 *    检查算子
 * */
void warpDC00Action(const struct BasicOperator * py_p_bop, const int city_loc6 , const float city_value, void * p_totaldamage_map, void * p_aiaction);

/*
 *  测试函数：夺控
 *  输入参数:
 *    const struct BasicOperator *p_bop
 *    const int loc_city_int6 要夺控的城市的6位坐标
 *    const float value_city 要夺控的城市的分数
 *    const float * p_totaldamage_map 敌方所有算子对p_bop的综合战损图
 *    const int aiaction_len
 *  输出参数：
 *    float *p_aiaction 
 *  
 *  注意事项：
 *    如果能够进入该函数（该函数被调用），默认算子如果能到达城市，可以进行夺控， reward的起点是value_city
 *    内部封装getOccupyingRoutes ==> getBestOccupyingRoute ==> cvtOccupyRoute2AIAction()
 */
void warpOccupyAction(const struct BasicOperator * py_p_bop, const int loc_city_int6, const float value_city, void * p_totaldamage_map, const int aiaction_len, void * p_aiaction);

/*  
 * 在指定参数下计算算子的侦察动作
 * 输入参数：
 *  py_p_bop 当前算子
 *  dir , mindis , maxdis : 指定方向和距离区间
 *  methodflag : 选点方法
 *  aiaction_len 动作长度
 * 输出参数：
 *  p_aiaction 动作
 * 注意事项：
 *  1 当前没有实现methodflag方法，直接选择最远的点
 *  2 mindis >= 1 && mindis <= maxdis
 *  3 如果找不到侦察点，返回无效动作
 * */

void warpScoutAction(const struct BasicOperator *py_p_bop, const int dir, const int mindis, const int maxdis, const int methodflag, const int aiaction_len, void * p_aiaction);

//算子起始点达目标点的路径
void warpGetPath(const struct BasicOperator *p_attacker, const int obj_int6loc,const int len,void *p_path);

//计算单个武器的攻击等级
void warpOneWeaponDirectDamageP2P(const struct BasicOperator *p_attacker,const struct BasicOperator *p_obj,const int weaponID,void *p_damage);

// /*--------------------宋国瑞添加--------------------*/
// //  申请全局显存存储特征图 
// //  * 输入参数：
// //  *		const int redOpeNum
// //  *		const int blueOpeNum
// //  *		const int cityNum
// //  * 返回参数：
// //  *		bool 初始化是否成功
 
// // bool warpCuFeatureInit(const int redOpeNum, const int blueOpeNum, const int cityNum);

// /*---------------------封装动作生成函数---------------*/

// /* 射击动作cuda生成
//  * 封装合并FFBT/静态射击2个函数
//  * 输入参数：
//  *  const struct BasicOperator *py_p_attacker
//  *  const struct BasicOperator *py_p_obj
//  *  const int flag_ss 调用静态射击标志位 1(内部调用struct.h中cvtStaticShooting2AIAction函数) 
//  *				      0 ==> 算子属性 选择getDA 或 getFFBT系列函数 ==> getBest* ==> cvt**Route2Action() => 动作字段
//  *  void * p_uniondamage_map 对方剩余算子对我方算子的最大战损图
//  *  void * p_blindareadata 敌方算子的累积盲区（记录我方算子在指定位置能够对方多少个算子看到）
//  * 输出参数：
//  *  void * p_aiaction (字段的定义存放在struct.h中)
//  */
// // void warpMSAction_cuda(const struct BasicOperator *py_p_attacker, const struct BasicOperator *py_p_obj, const int flag_ss, const int flag_task, void *p_uniondamage_map,  void *p_totalblind_map, void *p_aiaction);

// /* DC00 cuda计算
//  *  封装守城模型： getDC00Routes -》 getBestDCRoute --> cvtDCRoute2Aiaction
//  *  输入参数：
//  *    const struct BasicOperator * py_p_bop
//  *    const int city_loc6
//  *    const float city_value
//  *    void * p_totaldamage_map
//  *  输出参数:
//  *    void p_aiaction
//  *  注意事项：
//  *    检查算子
//  * */
// // void warpDC00Action_cuda(const struct BasicOperator * py_p_bop, const int city_loc6 , const float city_value, void * p_totaldamage_map, void * p_aiaction);

// /* DA01 cuda计算
//  * 封装DA01模型
//  * 输入参数：
//  *    const struct BasicOperator * py_p_attacker(载人战车)
//  *    const struct BasicOperator * py_p_peo (战车上的人员算子)
//  *    const struct BasicOperator * py_p_obj (目标算子)
//  *    const int flag_task (0/1/2) 进攻/防御/撤退
//  *    void * p_uniondamage_map 对方算子对我方当前算子py_p_attacker的综合战损图
//  *    void * p_totalblind_map 对方算子的视野盲区
//  *    const int aiaction_len 编码长度
//  * 输出参数：
//  *    void * p_aiaction
//  * 注意事项：
//  *    动作编码为下车3/下车机动8/机动下车7/机动下车机动9:四种类型
//  *    reward包含obj_value
//  *    类比： warpDA00SMAction()
//  * */
// // void warpDA01SMAction_cuda(const struct BasicOperator *py_p_attacker, const struct BasicOperator * py_p_peo, const struct BasicOperator *py_p_obj, const int flag_task , void * p_uniondamage_map, void * p_totalblind_map, void * p_aiaction);

// /* DA00 cuda计算
//  * 封装DA模型，DA模块以射击动作为驱动，输出机动动作，因此没有封装在warpMSAction()中
//  * 输入参数：
//  *  const struct BasicOperator * py_p_attacker (不载人战车/人员等无法机动射击的算子)
//  *  const struct BasicOperator * py_p_obj 目标算子
//  *  const int flag_task （0 进攻/1 防守）
//  *  void * p_uniondamage_map  敌方算子对我方的统一战损图(区别战损/reward: 后者考虑了算子的分数)
//  *  void * p_totalblind_map
//  *  const int aiaction_len  编码数组的长度
//  * 输出参数：
//  *  void * p_aiaction
//  * 注意事项：
//  *  该模块以射击动作为驱动，输出无行射能力算子（无人战车/人员算子）的反击动作，输出的是纯机动模型
//  */
// // void warpDA00SMAction_cuda(const struct BasicOperator *py_p_attacker, const struct BasicOperator *py_p_obj, const int flag_task , void * p_uniondamage_map, void * p_totalblind_map, void * p_aiaction);

//  夺控cuda 计算
//  *  测试函数：夺控
//  *  输入参数:
//  *    const struct BasicOperator *p_bop
//  *    const int loc_city_int6 要夺控的城市的6位坐标
//  *    const float value_city 要夺控的城市的分数
//  *    const float * p_totaldamage_map 敌方所有算子对p_bop的综合战损图
//  *    const int aiaction_len
//  *  输出参数：
//  *    float *p_aiaction 
//  *  
//  *  注意事项：
//  *    如果能够进入该函数（该函数被调用），默认算子如果能到达城市，可以进行夺控， reward的起点是value_city
//  *    内部封装getOccupyingRoutes ==> getBestOccupyingRoute ==> cvtOccupyRoute2AIAction()
 
// // void warpOccupyAction_cuda(const struct BasicOperator * py_p_bop, const int loc_city_int6, const float value_city,  void * p_totaldamage_map, const int aiaction_len,  void * p_aiaction);

// /* 承受战损图(不能机动的位置战损为-1) 维数：算子最大血量×MAP_YNUM*MAP_XNUM(可变的为B算子的血量)
//  * 输入参数：
//  *		const struct BasicOperator *p_bopA ： 算子A
//  *		const struct BasicOperator *p_bopB ： 算子B
//  *		const int *dev_p_wcgAMap ： A机动范围图
//  *		const int *dev_p_wcgBMap ： B机动范围图
//  * 输出参数	
//  *		float *dev_p_takeDamageMap ： 战损图 维数： 算子最大血量×地图高×地图宽
//  * 返回参数：
//  *		bool 是否计算成功
//  * 注意：后缀为C表示计算C内存中的特征图,后缀为CUDA表示计算CUDA显存中的特征图
//  */
// //void warpCalTakeDamageMap(const struct BasicOperator *p_bopA,const struct BasicOperator *p_bopB,void *p_takeDamageMap);

// /*---------------------封装特征图计算函数-------------*/

// /*是否为隐蔽点图特征图 0不是隐蔽点/1隐蔽点，维数：MAP_YNUM*MAP_XNUM*/
// void warpCalIsInCoverMap(void *p_isInCoverMap);
// /* 机动范围图: 可以机动值为剩余机动力，不能机动值为-1 维数：MAP_YNUM*MAP_XNUM
//  * 输入参数：
//  *		int cur_intloc 算子当前位置
//  *		int cur_step 算子当前机动力
//  *      int obj_type,
//  * 输出参数:
//  *		int *dev_p_wcgMap： 机动范围图 维数：地图高×地图宽
//  * 返回参数：
//  *		bool 是否计算成功
//  * 注意：后缀为C表示计算C内存中的特征图,后缀为CUDA表示计算CUDA显存中的特征图
//  */
// void warpCalWcgMap(int cur_int4loc,int cur_step,int obj_type,void *p_wcgMap);
// /* c计算机动范围图，不能机动-1 维数:MAP_YNUM*MAP_XNUM
//  * 输入参数：
//  ×		const struct BasicOperator *py_p_bop ： 算子
//  * 输出参数：
//  *		void *p_wcgMap :机动范围图		
//  */
// void warpCalWcgMapC(const struct BasicOperator *py_p_bop,void *p_wcgMap);
// /* 造成战损图(不能机动的位置战损为-1) 维数：最大血量*MAP_YNUM*MAP_XNUM(可变的为攻击算子的血量)
//  * 输入参数：
//  *		const struct BasicOperator *p_attacker ： 攻击算子
//  *		const struct BasicOperator *p_obj ： 目标算子
//  *		const int *dev_p_wcgAttMap ： 攻击算子机动范围图
//  * 输出参数	
//  *		float *dev_p_damageMap ： 战损图 维数： 算子最大血量×地图高×地图宽
//  * 返回参数：
//  *		bool 是否计算成功
//  * 注意：后缀为C表示计算C内存中的特征图,后缀为CUDA表示计算CUDA显存中的特征图
//  */
// void warpCalDamageMap(const struct BasicOperator *p_attacker,const struct BasicOperator *p_obj,void *p_damageMap);
// //不考虑a的机动范围，在全图范围内计算战损图
// void warpCalWholeTakeDamageMap(const struct BasicOperator *p_bopA,const struct BasicOperator *p_bopB,void *p_takeDamageMap);
// /* 计算A算子机动到各个位置之后在剩余机动范围内承受的最小战损图 维数： 算子最大血量 * MAP_YNUM*MAP_XNUM(可变的为B算子的血量)
//  * 输入参数：
//  *		const struct BasicOperator *p_bopA ： 算子A
//  *		const struct BasicOperator *p_bopB ： 算子B
//  *		const int *dev_p_wcgAMap ： A机动范围图
//  *		const float *dev_p_takeDamageMap : A算子承受B算子的战损图
//  * 输出参数	
//  *		float *dev_p_moveTakeDamageMap ：A机动范围内承受最小战损图 维数： 算子最大血量×地图高×地图宽
//  * 返回参数：
//  *		bool 是否计算成功
//  * 注意：后缀为C表示计算C内存中的特征图,后缀为CUDA表示计算CUDA显存中的特征图
//  */
// void warpCalMoveTakeMinDamageMap(const struct BasicOperator *p_bopA,const struct BasicOperator *p_bopB,void *p_moveTakeDamageMap);
// /* 计算是否在夺控点一格范围内图  维数：MAP_YNUM*MAP_XNUM
//  * 输入参数：
//  *		const int city_int4loc : 夺控点位置
//  * 输出参数
//  *		int *p_isCityDefMap : 是否是防守夺控点图
//  * 返回参数：
//  *		bool 是否计算成功
//  * 注意：后缀为C表示计算C内存中的特征图,后缀为CUDA表示计算CUDA显存中的特征图
//  */
// void warpCalCityDefMap(const int city_int4loc,void *p_isCityDefMap);


/*---------------------宋国瑞2018年08月10日重新封装特征计算函数---------------------*/
/* 计算攻击等级图
 * 输入参数：
 *	const struct BasicOperator *p_attacker 攻击算子
 * 	const struct BasicOperator *p_obj 目标算子
 * 输出参数：	
 *	void *p_attLevelMap 攻击等级图
 *	注意：
 * 		内部根据cuda是否初始化标志位自动选择计算方式(c/cuda)
 *
*/
void warpAttackLevelMap(const struct BasicOperator *p_attacker,const struct BasicOperator *p_obj,void *p_attLevelMap);

/* 计算视野盲区图
 * 输入参数：
 *	const struct BasicOperator *p_bop 
 * 输出参数：	
 *	void *p_blindMap 视野盲区图 盲区1/非盲区0
 *	注意：
 * 		内部根据cuda是否初始化标志位自动选择计算方式(c/cuda)
 *
*/
void warpIsBlindMap(const struct BasicOperator *p_bop,void *p_blindMap);
