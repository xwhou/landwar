/*  2017年5月31日/gsliu/PAL_Wargame
 *  基本功能：
 *    计算特征图，map.h/c operator.c/h => feature.h/c ==> utilities.c/h  ==> python 
 *  更新：
 *    2017年5月31日： 建立文档，将原来map.c/h中的特征图计算模块抽离出来放到本文件中
 *		      基于给定位置计算通视范围 icuRange()
 *		      根据单边机动表格计算机动范围 whereICanGoRange()
 *		      给定攻击算子计算攻击等级范围 attacklevelRange()
 *    2017年6月1日：  点对点的战损等级 damagelevelP2P() 需要以点对点的攻击等级为基础
 *    2017年6月2日：  最优攻击与躲避路径getOptFFBTRoutesP2P() & getFFBTRoutes1010()函数
 *		      RUSHAI中基于指定射击类型的模拟战损计算 rushAiDamageLevelP2P()
 *		      RUSHAI中找出移动路径rushAiOptNextRoute()函数
 *    2017年6月4日：  修正damagelevelP2P()函数的辅助可视范围参数接口 
 *    2017年6月5日：  基于当前算子的机动力，从A->B为算子找到一条趋势路径trendpathP2P()
 *    2017年7月19日： 针对无法进行进间射击的算子设计延迟攻击模型 getDelayAttackRouteP2P()
 *    2017年7月26日： 增加FFBT系列函数：具有行进间射击能力（1）的无人（0）算子攻击无行射能力（0）的不载人（0）算子
 *    2017年7月27日： 移除将动作决策模型有关的函数模块放在strategy.h/c文件中
 *    2017年8月16日： 增加采用行军方式的机动范围whereICanPassRangeGA()函数
 *    2017年8月17日： 针对算子在道路网上行军的路径回溯，增加函数trendpathP2P4Pass()函数与trendpathP2P()相对应
 *    2017年8月23日： 补充基于两个算子的特征iouRange()， 以icuRange()的输入为输出进行估计
 *    2017年8月29日： 完善whereICanGoRangeGA()函数，车辆与人员算子的机动力消耗方式不同，在此函数中区分车辆与人员；
 *		      主要区别在于进入指定六角格消耗的机动力/对应路径回溯trendpathP2P()函数也要更正
 *    2017年8月29日： 行军中考虑道路类型的限制因素，目前仅修正行军结果，即在trendpathP2P4Pass()模块中进行操作
 *		      实际上需要对从行军机动范围whereICanPassRangeGA()下手处理
 *    2017年9月7日：  计算被打击程度地图 damageMapP2P()， 算子A对指定位置的算子B的战损图，区分算子A是否有行射能力
 *    2018年3月14日： 更改icuRange(),查表方式代替计算方式，完成六角格AB的通视判断，实际上仅仅修改judge.h/c中的icuIsOk()函数
 *
 */

#ifndef FEATURE_
#define FEATURE_

#include "judge.h" 

/*宏定义*/
#define DEFALUT_ZERO (0.0)


/*
 * 给定当前六角格位置坐标，最大通视距离，计算通视范围
 * 输入参数： const struct HexOfOffset *p_hex
 *	      const int maxdistance
 * 输出参数： struct dictionary *p_dicloc2dis
 *	      key为可通视的六角格的坐标 ==> value为该六角格距离中心六角格的距离
 */

void icuRange(const struct HexOfOffset *p_hex, const int maxdistance, struct dictionary *p_dicloc2dis);

/*
 * 标记算子B在哪些位置上能够被算子A看到（1），在哪些位置上不会被算子A看到（0）
 * 输入参数：
 *  const struct BasicOperator *p_bopa, p_bopb
 * 输出参数：
 *  float * p_ioumap
 */
void iouRange(const struct BasicOperator *p_bopa, const struct BasicOperator *p_bopb, float *p_ioumap);

/*
 * 坦克对其他算子的动态可视范围：标记的是B在哪些位置上被A看到的程度
 * 输入参数：
 *  const struct BasicOperator * p_bopa, p_bopb
 * 输出参数：
 *  float* p_ioumap
 * 注意事项：
 *  坦克在机动范围，逐格计算B的被观察标记(iouRange)，最后叠加所有的ioumap作为B的暴露程度
 * */
void iouDynamicRange(const struct BasicOperator* p_bopa, const struct BasicOperator* p_bopb, float *p_ioumap);

/*  计算给定算子的机动范围
 *  输入参数： const struct BasicOperator *p_bop
 *  输出参数： struct dictionary *p_dicwicg
 *  方法：
 *    key(六角格四位坐标)->value(达到该六角格所剩余的机动力), 六角格序列经过检验
 *  注意：内部调用 whereICanPassRangeGA()函数
 */

void whereICanGoRange(const struct BasicOperator *p_bop, struct dictionary *p_dicwicg);

/*  计算给定算子的机动范围：输出是GA类型的数据
 *  输入参数： const struct BasicOperator *p_bop
 *  输出参数： struct GA *p_gawicg
 *  元素格式：row col power sizeof(int)
 *  注意：该方法可计算人、车两种类型的算子；人进入每一个格子的基本机动力（区别于被发现程度）为1
 *	  该函数通过判断g_mapattr.dic_pairlocs2pow == NULL 选择 whereICanGoRangeGA_com 或者 whereICanGoRangeGA_cache;
 *	  0 BUG0: C缓存模式的使用条件，需要加上机动力 leftpower <= 8, 否则使用C计算模式
 *	  1 BUG2: 测试表明C缓存对于计算机动范围没有加速效果，直接屏蔽掉/同时屏蔽掉距离计算的C缓存函数
 *    2 BUG3: whereICanGoRangeGA_cache 函数需要考虑算子是人的情况，机动力消耗等于距离,
 *    3 BUG4: 人员算子不使用g_mapattr.dic_pairlocs2pow变量
 */

void whereICanGoRangeGA(const struct BasicOperator *p_bop, struct GA *p_gawicg);
void whereICanGoRangeGA_com(const struct BasicOperator *p_bop, struct GA *p_gawicg);
void whereICanGoRangeGA_cache(const struct BasicOperator *p_bop, struct GA *p_gawicg);

/*
 *  计算给定算子的行军范围，返回struct dictionary *p_dicwicp 结构，与whereICanGoRange()对应
 *  输入参数： const struct BasicOperator *p_bop
 *  输出参数： struct dictionary *p_dicwicp
 *  注意：返回dictionary的元素格式为int, str_4loc(key) -> leftpower (value)
 *	  内部调用了whereICanPassRangeGA()模块
 *  注意2： 只针对车辆算子 (obj_type == 2)
 */ 
void whereICanPassRange(const struct BasicOperator *p_bop, struct dictionary *p_dicwicp);

/*
 * 对应whereICanGoRangeGA，给出算子以行军方式的机动范围
 * 输入参数： const struct BasicOperator *p_bop 算子
 * 输出参数： struct GA * p_gawicp
 * 注意：元素格式 int4loc, hexnum_passed (从起始位置开始，到此位置中间走过的六角格数目) sizeof(int)
 * 注意2： 只针对车辆算子 (obj_type == 2)
 */

void whereICanPassRangeGA(const struct BasicOperator *p_bop, struct GA *p_gawicp);



/* 计算算子当前机动力计算从A到B的一条“趋势”路径
 * 输入参数： struct BasicOperator *p_bop 当前算子 
 *	      struct HexOfOffset *p_objhex 想要达到的位置
 * 输出参数： struct GA *p_gafullpath, p_gapartpath;
 * 返回数值： bool 找到路径 p_gapartpath->count >= 2 返回true
 *	      其他情况： p_gapartpath->count == 1 (当前位置为目标点）
 *			 p_gapartpath->count == 0 (外部规则约束无法进行路径规划) 
 *	      均返回false
 *	      
 * 方法：
 *	首先赋予算子充足的机动力，从初始位置计算wicgmap,保证wicgmap能够覆盖到p_hexb
 *	然后从p_hexb为起点，不断寻找机动力最大的数值,直到返回p_hexa,形成全局路径
 *	基于算子当前的机动力，从全局路径中截取一段，填充到p_gapath,作为返回结果
 */
bool trendpathP2P(const struct BasicOperator *p_bop, const struct HexOfOffset *p_objhex, struct GA *p_gafullpath, struct GA *p_gapartpath);

//算子起始点达目标点的路径
bool getPath(const struct BasicOperator *p_attacker, const int obj_int6loc,int len,int *p_path);

/*
 *  以目标为导向为当前算子找到一个合适的躲避点（机动+躲避同时进行）
 *  输入参数：
 *    const struct BasicOperator * p_bop
 *    const struct HexOfOffset *p_objhex
 *  输出参数：
 *    struct HexOfOffset *p_findhex
 *  返回数值：
 *    bool true(找到合适的躲避点+落脚点) / false（未找到）
 */

bool findOptStopHex(const struct BasicOperator *p_bop, const struct HexOfOffset *p_objhex, struct HexOfOffset *p_findhex);

/*
 * 行军状态下的路径回溯算法，与trendpathP2P()相对应
 * 输入参数：
 *  const struct BasicOperator *p_bop 当前算子
 *  const struct HexOfOffset *p_objhex 需要达到的位置，该参数与算子当前所在六角格都应该在道路网上
 * 输出参数：
 *  struct GA *p_gafullpath, p_gapartpath;
 * 返回数值：
 *  同trendpathP2P()函数的返回数值
 * 注意：该模块与trendpathP2P()模块算法思想一致，需要优化，保持统一
 *	 p_objhex不一定在道路上，如果目标位置不再道路上，将与p_objhex距离最近i(给定阈值)的道路节点定义为本次的目标位置
 *	 因此本函数不一定能够返回有效的路径，如果目标不再道路上，同时最近临道路六角格超过范围，则返回空路径（无法行军）
 * 注意2： 只针对车辆算子 (obj_type == 2)
 */

bool trendpathP2P4Pass(const struct BasicOperator *p_bop, const struct HexOfOffset *p_objhex, struct GA *p_gafullpath, struct GA *p_gapartpath);


/*
 *  给定攻击算子与目标算子，攻击算子所用武器编号，计算并返回经过高差矫正后的攻击等级
 *  输入参数：	
 *		const struct BasicOperator *p_attacker
 *		const struct BasicOperator *p_obj
 *		const int weapen_index
 *  返回参数：  int <0 标识攻击无效(不再射程内部) /  =0 标识实际攻击等级确实为0(经过矫正) / > 0 有效攻击等级
 *  注意：内部不进行武器有效性数值范围检查
 *
 */

int  attacklevelP2P(const struct BasicOperator *p_attacker, const struct BasicOperator *p_obj, const int weapen_index);

/*
 *  函数说明：给定攻击/目标算子，所用武器，计算目标算子遍历地图不同位置上的攻击等级图
 *  输入参数：const struct BasicOperator * p_bop_att
 *	      const struct BasicOperator * p_bop_obj
 *	      const int wp_index
 *  输出参数：float *p_atmap_data 计算后的特征图数据
 *  返回参数：bool 特征图中含有有效数值，true, 否则为false
 *  注意事项：1 p_atmap_data 需要初始化为DEFALUT_ZERO ,后续回据此判断目标位置的有效性质
 *	      2 CUDA—C也提供同样的特征计算模块
 *	      3 内部不使用attacklevelP2P,而是在此基础上简化冗余计算
 *  
 * */

bool attacklevelMap(const struct BasicOperator *p_bop_att, const struct BasicOperator *p_bop_obj, const int wp_index, float * p_atmap_data);

/*
 *  函数说明：给定攻击/目标算子，所用武器，计算攻击算子遍历地图不同位置上的攻击等级图
 *  输入参数：const struct BasicOperator * p_bop_att
 *	      const struct BasicOperator * p_bop_obj
 *	      const int wp_index
 *		  const int* p_attWcgMap 攻击算子机动范围图
 *  输出参数：float *p_atmap_data 计算后的特征图数据
 *  返回参数：bool 特征图中含有有效数值，true, 否则为false
 *  注意事项：1 p_atmap_data 需要初始化为DEFALUT_ZERO ,后续回据此判断目标位置的有效性质
 *	      2 CUDA—C也提供同样的特征计算模块
 *	      3 内部不使用attacklevelP2P,而是在此基础上简化冗余计算
 *  
 * */
bool attacklevelMap_attMove(const struct BasicOperator *p_bop_att, const struct BasicOperator *p_bop_obj, const int wp_index, const int* p_attWcgMap,float * p_atmap_data);
/*
 * 计算两点之间进行射击的战损数据, 需要指定攻击者所使用的武器编号weapen_index
 * 输入参数： const struct BasicOperator *p_attacker
 *	      const struct BasicOperator *p_objective
 *	      const int weapen_index 
 * 返回参数： float  damage_value(>0 有效) | 不符合规则的战损(-1)
 * 注意： 内部检查攻击算子所使用的武器 weapen_index, 武器无效，返回-1
 *	  内部调用attacklevelP2P()函数计算攻击等级，然后查表计算战损数据
 * 检查攻击算子/武器能否进行设计/ 目标算子是否符合攻击条件
 */
float  damagelevelP2P(const struct BasicOperator *p_attacker, const struct BasicOperator *p_obj, const int weapen_index);

/*
 *
 * 给定攻击算子与目标算，在攻击算子的机动范围内找出有效攻击位置
 * 输入参数： p_attacker
 *	      p_obj
 x*	      p_dicwicg 攻击算子的机动范围
 * 输出参数： p_gadamagelist 
 * 注意：元素格式 attr_bytenum = sizeof(float).数组长度 == 3+武器数量（3标识有效攻击位置的行，列索引，在此位置的剩余机动力），后面数字依次标识在此位置上每个武器对目标算子造成的估计毁伤，该条目被记录的条件是：攻击算子至少有一件武器在此位置能够对目标算子造成>0的实际毁伤效果。
 * ___ ___ ___ ________
 * row col pow damge_wx ...
 *
 */
void listdamages(const struct BasicOperator *p_attacker , const struct BasicOperator *p_obj, const struct dictionary* p_dicwicg, struct GA *p_gadamagelist);


/*
 * 以listdamages()输出为输入，找出最优设计条件
 * 输入参数： p_gadamagelist
 *	      const int len : p_ele所占用的内存长度
 * 输出参数： p_ele 
 * 数据格式： row col leftpow weapon_index damagelevel (5元组)
 * 注意： 按照战损最大 ==> 战损相同，最节省机动力的方式进行选择
 *	  “BUG“ 在遍历过程中，记录最大战损的变量 maxdamage的初始数值设置为 DAMAGVALUE_MIN (该数值保证一定大于DAMAGVALUE_INVALID)
 *		因此可以过滤掉无效战损（不符合规则的射击方案）
 */
int optShootingCond(const struct GA *p_gadamagelist, const int len , float *p_ele);

/*
 *  武器选择模块，针对目标算子为攻击算子选择攻击武器
 *  输入参数： const struct BasicOperator * p_attacker
 *	       const struct BasicOperator * p_obj
 *  输出参数： float * p_maxvalue 毁伤战损
 *	       int * p_maxindex   武器编号
 *  返回值  ：
 *    毁伤战损数值>0标识所选的攻击武器有效, 返回true
 *    否则返回false
 *  注意： 和listdamages/optShootingCond比较的话，本函数输出P2P模式的武器选择与攻击效果，上面两个函数输出攻击算子在机动范围内的最优攻击位置，以及在该位置上的最有武器选择与攻击毁伤信息
 */
bool weaponSelectionForAttacker(const struct BasicOperator *p_attacker, const struct BasicOperator *p_obj, float * p_maxvalue, int *p_maxindex);

/*
 * 计算战损图 damageMapP2P
 * 输入参数：
 *    const struct *p_attacker
 *    const struct *p_obj
 * 输出参数：
 *    float * p_damagemap
 * 注意： 1 该模块计算，算子p_obj在地图各个位置上，算子p_attacker对其造成的战损
 *	  2 如果算子p_attacker具有行进间射击能力,剩余机动力&没有射击,需要计算其在机动范围内所有位置生成的战损,然后累加
 *
 */

void  damageMapP2P(const struct BasicOperator *p_attacker, const struct BasicOperator *p_obj, float * p_damagemap);



/*
 * 函数说明：计算指定武器下的战损图，和damageMapP2P进行区分（该函数计算所有武器下的综合战损图）
 * 输入参数：攻击算子与目标算子 const struct BasicOperator * p_bop_att, p_bop_obj
 *	     攻击算子选择的武器索引 const int wp_index (第wp_index件武器)
 * 输出参数：float * p_damagemap 返回的战损图
 * 返回参数：void 
 * 注意事项：1 与damageMapP2P进行区分
 *	     2 比较对象的的cuda-c函数
 *	     3 如果算子有行射能力，是否需要考虑算子的机动范围？
 *
 * */
void  separateDamageMap(const struct BasicOperator *p_attacker, const struct BasicOperator *p_obj, const int wp_index, float * p_damagemap);



/*
 *  基于侦察参数（方向和侦察范围/结合机动范围确定侦察点的候选位置）
 *  输入参数:
 *    const struct BasicOperator *p_bop	    当前算子
 *    const int dir			    侦察方向[dir in range(6)]
 *    const int mindis, maxdis		    侦察区间（mindis >=1 && maxdis >= mindis）
 *    
 *  输出参数：
 *    struct GA * p_gahexs	    三元组（row,col,flag） flag = -1 位置无效，当前算子机动到该位置剩余的机动力
 *
 *  注意事项：
 *    侦察点的选择策略很有可能随时变动，因此先实现最基本的选点策略，其余策略逐渐筛选实现
 *    侦察点的选点策略，一方面是为了保证动作的合理性和可解释性，另一方面是还是保证动作的随机性，从学习的角度来讲，后者的重要性优于前者
 *
 * */

bool getCandidateScoutlocs(const struct BasicOperator * p_bop, const int dir, const int mindis, const int maxdis, struct GA *p_gahexs);


/*
 *  给定攻击算子和目标算子类型，寻找最佳的攻击武器编号
 *  输入参数:
 *    const struct BasicOperator *p_attacker	   攻击算子
 *    const int tar_type 目标算子类型
 *  返回参数：
 *    int 	攻击算子最佳武器索引
 *  Bug0:
 *		武器攻击等级与距离有关，程序中用距离为0的时候选择武器，会有问题
 * */

int getBestWeaponIndex(const struct BasicOperator *p_attacker,const int tar_type);

#endif 
