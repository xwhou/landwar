/*  2017年7月27日/gsliu/PAL_Wargame
 *  基本功能：
 *    定义与AI算子动作有关的函数：feature.h ==> utilities.h 
 *  更新：
 *    2017年7月27日：建立strategy.h strategy.c文件，完成且战且走模型FFBT的动作输出与延迟攻击模型DA的动作输出
 *    2017年7月27日：将与FFBT、DA模块有关的宏定义从judge.h中移动到本文件
 *		     对DA模型的细分模块（载人/不载人）两种字段进行选择，找出最优，类似与getBestFFBTRoutes函数
 *    2017年7月30日：FFBT和DA模型得到的最优路径==>算子实质性动作的函数； 检查三种类型的最优路径是否有效的函数（直接写入到getBest*系列函数中）
 *    2017年8月15日：对无行射能力的算子增加原地射击检查函数 checkStaticShooting(),代替了getDARoutes????()函数中的原地射击选项部分;
 *		     基本思想为如果checkStaticShooting()返回true,表示原地射击可行； 否则直接进入移动-->下阶段反击模型。
 *    2017年8月15日：及时更新算子在模拟战斗中的obj_blood参数，使得模拟更具有真实性；
 *    2017年8月18日：更新cvtRushMoving2AIAction(), 加入机动方式选择（机动、行军两种模式）
 *    2017年9月7日： 更新getFFBTRoutes*系列函数；敌方算子分为：目标算子（我方算子正在攻击的对对方算子） 和警惕算子（剩余的敌方算子）
 *    2017年9月7日： 将listdamages() optShootingCond() weaponSelectionForAttacker()函数移动到feature.c中
 *    2017年9月21日：修改getBest*系列函数，在最优条件中加上落脚地的选择，落脚点选择为隐蔽点（村庄，丛林地等）
 *    2017年9月21日：修正getBestFFBTRoutes()，检查无效路径（我方与对方算子均不射击，返回无效动作）
 *    2017年10月1日：修正模型错误:
 *			模型中需要及时copy算子的状态:位置,剩余机动力,血量等信息,在每次循环结束注意初始化
 *			战车=>坦克模型; getDARoutes0110() / getDARoutes0010() 对方坦克应该也使用攻击后躲避的getFFBTRoutes1000()模型
 *    2017年10月11日:修复getDARoutes0110()的BUG: 载人战车攻击坦克,坦克反击人/反击车的比较选择过程中,可能出现无效数据(攻击人/车均可; 只能攻击人;只能攻击车;三种情况要进行细分类1)
 *
 *    2017年12月4日：加入夺控模型（人/无人战车；坦克三种算子的夺控模型（坦克的射击点在python中加入））
 *		     人/战车为夺控模型（机动夺控的组合）/ 坦克在夺控路线的基础上寻找射击点: 夺控10 机动夺控14 夺控机动15， MOM:16
 *		     函数系列： getOccupyingRoutes/ getBestOccupyingRoute/ cvtOccupyRoute2AIAction 
 *    2017年12月12日： 加入守城墨模型（针对人员算子/无人战车）， getDefenceCityRoutes()
 *		      基本思路：根据算子的当前位置/当前剩余机动力/与夺控点的距离/安全区域 ==> 选择合适的机动路线到达夺控点1格以内的范围
 *    2018年3月21日： 利用高阶特征图加速计算
 *    2018年6月1日：  加入侦察动作模块：分为两部分（1）按照指定的侦察参数（当前算子，侦察程度，侦察方向，选点策略）选出侦察位置
 *						  （2）机动到该位置，返回一个完整的机动动作（该模块可通用于基于目的点生成机动动作的情景）
 */

 
#ifndef STRATAGE_
#define STRATAGE_ 

#include "feature.h"

// RUSHAI模式下射击的宏定义
#define RUSHMODE_SHOOTING_ROW 0  //射击位置行索引
#define RUSHMODE_SHOOTING_COL 1 // 射击位置列索引
#define RUSHMODE_SHOOTING_TYPE 2 // 射击类型（算子内部判断能够射击，该位置为shootingtype, 否则该位置=0）
#define RUSHMODE_SHOOTING_LEFTPOWER 3 // 移动到射击位置上的剩余机动力
#define RUSHMODE_SHOOTING_WZINDEX 4 // 使用的武器编号索引
#define RUSHMODE_SHOOTING_ATTACKLEVEL 5 // 修正后的攻击等级
#define RUSHMODE_SHOOTING_DAMAGELEVEL 6 // 战损输出  /*  7 8 位置存放python中的敌我双方的算子索引数值 */
#define RUSHMODE_SHOOTING_DISTANCE 9 // 攻击算子与目标算子之间的距离
#define RUSHMODE_SHOOTING_ELEDIFF 10  // 攻击算子与目标算子之间的高程差
#define	RUSHMODE_SHOOTING_MOVEHEXNUM 11 // 从算子初始位置移动到射击位置中间的六角格数目 //后续格式为（新的6位坐标、剩余机动力）二元组

// RUSHAI模式下移动的宏定义
#define RUSHMODE_MOVEROUTE_FLAG 0 // 是否进行了机动
#define RUSHMODE_MOVEROUTE_ROW 1 // 最后落脚位置行索引
#define RUSHMODE_MOVEROUTE_COL 2 // 最后落脚位置列索引
#define RUSHMODE_MOVEROUTE_LEFTPOWER 3 // 剩余机动力索引



#define FLAG_INVALID_ROUTE -1 // 无效路径位置标记
// 定义与且战且走模式策略有关的宏
#define FFBTMODE_ELELEN 17 // 表示一种策略需要的元素个数 
#define FFBTMODE_SHOOTING_ROW_A 0 // 攻击算子的射击位置行索引
#define FFBTMODE_SHOOTING_COL_A 1 // 攻击算子的设计位置列索引
#define FFBTMODE_SHOOTING_LEFTPOWER_A  2   // 攻击算子移动到射击位置上的剩余机动力量
#define FFBTMODE_SHOOTING_DAMAGELEVEL_A 3    // 攻击算子主动攻击造成的战损
#define FFBTMODE_DEFENSELOC_ROW_A 4 //攻击算子防御位置的行索引
#define FFBTMODE_DEFENSELOC_COL_A 5 //攻击算子防御位置的列索引
#define FFBTMODE_DEFENSELOC_LEFTPOWER_A 6 //攻击算子移动到防御位置剩余机动力
#define FFBTMODE_SHOOTING_ROW_O  7 // 目标算子射击（反击）位置的行索引
#define FFBTMODE_SHOOTING_COL_O  8 // 目标算子射击（反击）位置的列索引
#define FFBTMODE_SHOOTING_LEFTPOWER_O 9 // 目标算子在射击（反击）位置上的剩余机动力
#define FFBTMODE_SHOOTING_DAMAGELEVEL_O 10 // 目标算子在射击（反击）造成的战损索引
#define FFBTMODE_REWARD 11 // 本策略攻击算子最终取得的综合战损
#define FFBTMODE_WEAPENINDEX_A 12 // 攻击算子射击使用的武器
#define FFBTMODE_WEAPENINDEX_O 13 // 目标算子反击使用的武器
#define FFBTMODE_STRATEGYTYPE 14 // 记录当前策略类型索引
#define FFBTMODE_INITLOC_ROW_A 15 // 攻击算子的初始位置行索引
#define FFBTMODE_INITLOC_COL_A 16 // 攻击算子的初始位置列索引


//且战且走过程中的四种类型  
/* 注意：一条策略路径中，首先需要检查策略类型，以便保证x* x2 y*位置的有效性 */
#define FFBTMODE_DOUBLEFIRE 11   // 双方均进行了射击（数据位置索引为FFBTMODE_STRATEGYTYPE）
#define FFBTMODE_ONLYSHOOTING 10 // 仅有攻击算子进行了射击
#define FFBTMODE_ONLYDEFENSE 1  // 仅有目标算子进行了射击
#define FFBTMODE_NOFIRE	  0     // 双方都没有进行射击

// 不载人算子延迟射击模型的宏定义， 不论敌方算子是否有行射能力，使用同一套字段定义
#define DAMODE_0_ELELEN 13
#define DAMODE_0_FLAG_SHOOTING_A 0	// 己方算子是否射击 0 不射击/ 1原地射击 /2 移动后下个阶段射击

#define DAMODE_0_WEAPONINDEX_A_THIS 1	// 原地射击所用武器索引
#define DAMODE_0_DAMAGERESULT_A_THIS 2	// 原地射击造成战损

#define DAMODE_0_LOC_SHOOTING_A_NEXT 3	// 下阶段射击位置，也就是本阶段需要移动到的目标位置
#define DAMODE_0_LEFTPOWER_SHOOTING_A_NEXT 4 // 下阶段射击位置剩余的机动力
#define DAMODE_0_WEAPONINDEX_A_NEXT 5	// 下阶段射击使用的武器索引
#define DAMODE_0_DAMAGERESULT_A_NEXT 6	// 下阶段设计造成的战损

#define DAMODE_0_FLAG_SHOOTING_O 7	// 对方算子是否射击 1射击/ 0未射击
#define DAMODE_0_LOC_SHOOTING_O 8	// 对方算子的射击位置
#define DAMODE_0_LEFTPOWER_SHOOTING_O 9 // 对方算子的射击位置剩余机动力
#define DAMODE_0_WEAPONINDEX_O 10	// 对方算子使用的武器索引
#define DAMODE_0_DAMAGERESULT_O 11	// 对方算子射击造成的战损
#define DAMODE_0_DAMAGERESULT_FINAL 12	// 最终战损 

// 延迟攻击策略（攻击算子载人) 不论敌方算子是否可以行进间射击，都可以使用同一套
#define DAMODE_1_ELELEN 14
#define DAMODE_1_FLAG_PEOPLEOFF 0      // 人员是否下车标志 0 不下车， 1 下车
#define DAMODE_1_LOC_PEOPLEOFF 1	      // 人下车位置索引（6位整型坐标）
#define DAMODE_1_LEFTPOWER_PEOPLEOFF 2  // 人下车后车剩余的机动力
#define DAMODE_1_LOC_DEFENCE_A 3	      // 我方车的躲避位置

#define DAMODE_1_FLAG_SHOOTING_O 4      // 敌方下一个阶段是攻击人(1)还是攻击车(2) 还是不射击(0)
#define DAMODE_1_LOC_SHOOTING_O 5	// 敌方算子的射击位置
#define DAMODE_1_LEFTPOWER_SHOOTING_O 6 // 目标算子射击位置剩余机动力
#define DAMODE_1_WEAPONINDEX_O 7	// 目标算子射击的武器索引
#define DAMODE_1_DAMAGERESULT_O 8       // 目标算子造成的战损
#define DAMODE_1_LOC_DEFENCEN_O 9	// 目标算子躲避位置

#define DAMODE_1_FLAG_SHOOTING_A 10     // 己方下下阶段是人攻击(1)还是车攻击(2) 还是不射击(0)
#define DAMODE_1_WEAPONINDEX_A  11      // 攻击算子的武器索引
#define DAMODE_1_DAMAGERESULT_A 12      // 攻击算子造成的战损
#define DAMODE_1_DAMAGERESULT_FINAL 13  // 综合战损（我方-敌方）



// 夺控路线的红定义：
#define OCCUMODE_ELELEN 6
#define OCCUMODE_LOC_CITY 0	      // 夺控位置(城市位置（能够夺控）/-1（不能夺控）)
#define OCCUMODE_LEFTPOWER_CITY 1	      // 到达夺控位置剩余机动力
#define OCCUMODE_DAMAGE_CITY 2	      // 在夺控点位置上遭受的战损
#define OCCUMODE_LOC_HIDEN 3	      // 躲避位置（利用OCCUMODE_LEFTPOWER上的机动力寻找的最优躲避位置）
#define OCCUMODE_LEFTPOWER_HIDEN 4    // 到达躲避后剩余的机动力
#define OCCUMODE_DAMAGE_HIDEN 5	      // 在躲避点位置上遭受的战损

/*守城模型的宏定义*/
#define DCMODE_0_ELELEN	   5 //序列长度
#define DCMODE_0_LOC_CITY  0  // 目标城市
#define DCMODE_0_LOC_FINAL 1  // 最终位置（-1无法守城/有效位置；可以守城）
#define DCMODE_0_LEFTPOW_FINAL 2 // 在最终位置上剩余的机动力 
#define DCMODE_0_DAMAGE_FINAL 3  // 在最终位置上遭受的战损（不包含obj_value）
#define DCMODE_0_REWARD       4  // 守城路线得到的reward(包含obj_value)


// 宏定义：模型得到的路径=>具体AI可识别的动作的转换
#define AIACTION_ELELEN 20     // 定义AI可识别的动作字段的长度
#define AIACTION_INVALID 0     // 动作类型：无效动作
#define AIACTION_MOVEONLY 1    // 仅移动
#define AIACTION_SHOOTONLY 2   // 仅射击
#define AIACTION_GETOFFONLY 3  // 仅下车

#define AIACTION_MOVESHOOT  4  // 移动后射击
#define AIACTION_SHOOTMOVE  5  // 射击后移动
#define AIACTION_MOVESHOOTMOVE 6 // 移动后射击再移动（针对FFBT路径）

#define AIACTION_MOVEGETOFF   7 // 移动后下车
#define AIACTION_GETOFFMOVE   8 // 下车后移动
#define AIACTION_MOVEGETOFFMOVE 9 // 移动后下车再移动
#define AIACTION_PASSONLY	11  // 行军（0-10中的移动标识普通移动，而行军不能与其他动作进行组合，需要单独拿出来）
#define AIACTION_DONOTHING 12 // 不做任何动作，区别无效动作，原地不动也是一种选择
// 算子上车编码 13
#define AIACTION_OCCUPY  10 //夺控操作
#define AIACTION_MOVEOCCUPY 14 // 机动夺控
#define AIACTION_OCCUPYMOVE 15 // 夺控机动
#define AIACTION_MOVEOCCUPYMOVE 16  // 机动夺控再机动


/*
 *  且战且走( fly and fight by turns)模式下的点对点攻击策略,1010标识攻击算子有行射能力(1)不载人(0); 目标算子有行射能力(1),不载人(0)
 *  输入参数： const struct BasicOperator *p_attacker
 *	       const struct BasicOperator *p_obj
 *	       const float * p_uniondamage_map 对方剩余算子在各个位置上的最大输出战损地图
 *		
 *  输出参数： struct GA *p_gaffbtroutes (元素格式见judge.h中的FFBTMODE_*系列的宏定义)
 *  注意：     p_uniondamage_map由对方所有可射击的算子以在指定位置的最大战损输出构成， 需要提前计算; 
 *		  实际上是其他所有算子对于攻击算子在该位置上的战损的最大值
 *	       如果攻击算子在防御位置被目标算子射击，比较目标算子的战损与其他算子战损的最大数值，取最大防御战损
 *	       如果目标算子不能射击防御位置的算子，直接去其他算子的战损作为防御战损
 *
 *	       1 p_x2dict中x2是攻击算子的躲避位置，如果x2确定，目标算子(在剩余blood相同的情况下)的反击战损也是确定的，只需要计算1次即可
 *	       2 能够用规则再次缩减一些计算？ 攻击算子的循环*目标算子的循环
 *
 */
void getFFBTRoutes1010(const struct BasicOperator *p_attacker,const struct BasicOperator *p_obj, const float * p_uniondamage_map, struct GA *p_gaffbtroutes);

/*
 *  且战且走模式：1001 目标算子无行射能力(0),不载人(0) 
 *  输入参数： const struct BasicOperator *p_attacker
 *	       const struct BasicOperator *p_obj
 *	       const float * p_uniondamage_map 
 *  输出参数：
 *	       struct GA *p_gaffbtroutes (元素格式见judge.h中的宏定义系列, 同getFFBTRoutes1010()函数
 *  注意： 参数p_uniondamage_map的含义同getFFBTRoutes1010()模块
 */
void getFFBTRoutes1000(const struct BasicOperator *p_attacker, const struct BasicOperator * p_obj, const float *p_uniondamage_map,  struct GA* p_gaffbtroutes);

/*
 *  且战且走模式：1001 目标算子为人(2)，假设无行射能力
 *  输入参数： const struct BasicOperator *p_attacker
 *	       const struct BasicOperator *p_obj
 *  输出参数：
 *	       struct GA *p_gaffbtroutes (元素格式见judge.h中的宏定义系列, 同getFFBTRoutes1010()函数
 *
 * 
 */
/*
void getFFBTRoutes102(const struct BasicOperator *p_attacker, const struct BasicOperator * p_obj, struct GA* p_gaffbtroutes);
*/


/*
 *  2018-10-21：给定攻击坦克和目标算子，获取所有的FFBT路径信息（路径选择放到python中完成）
 *  输入参数：
 *    const struct BasicOperator * p_att, p_obj 攻击算子（坦克）和目标算子
 *  输出参数：
 *    struct GA* p_gaffbtroutes	  保存所有的攻击路径
 *  注意事项：
 *    1 该模块仅做路径收集，每一条攻击路径的有效元素为：
 *	主动攻击位置，
 *	主动攻击等级，
 *	主动攻击的武器编号
 *	主动攻击位置剩余机动力
 *	躲避位置
 *	对方算子的攻击位置与攻击等级
 *	躲避位置剩余的机动力
 *    2 该模块与getFFBTRoutes1000/ getFFBTRoutes1010属于同一类型，但是不计算无关元素（保证计算速度）
 * */

void getALLFFBTRoutes(const struct BasicOperator * p_att, const struct BasicOperator *p_obj, struct GA* p_gaffbtroutes);


/*
 * 计算FFBT模型最优攻击路线
 * 输入： const struct GA * p_gaffbtroutes (getFFBTRoutes1000/ getFFBTRoutes1010函数的输出)
 *	  ele_len = FFBTMODE_ELELEN
 *	  const int * p_totalblind_map 一些尽量不可达到的点（预定义危险点/ 防止堆叠点）
 * 输出： 输出单条路径，路径长度与FFBTMODE_ELELEN相等， 输出格式float* 
 *	  float * p_route;
 * 选择方法：
 *    战损最大
 *	非（预定义危险点/堆叠点）：python将点的位置设置为极大，传入
 *	    被发现程度点
 *		剩余机动力(可以选择)
 */

bool getBestFFBTRoutes(const struct GA* p_gaffbtroutes,const int ele_len, const int* p_totalblind_map, float * p_route);

/*
 * 将FFBT模型返回的float*p_route转换成为AI可识别的动作指令,后者的编码方式参考resources/key_item_dataformat
 * 输入参数：
 *  己方算子 const struct  BasicOperator* p_bopattacker
 *  对方算子 const struct  BasicOperator* p_bopobj
 *  FFBT格式的路径 float *p_ffbtroute
 *  p_ffbtroute的长度： const int ffbtroute_len == FFBTMODE_ELELEN
 *  AI动作统一编码字段： float *p_aiaction
 *  p_aiaction的长度 ： const int aiaction_len (需要定义一些宏常量)
 * 输出参数： 
 *  动作有效 true/ 动作无效false
 */
bool getSpecHideBestFFBTRoutes(const struct GA* p_gaffbtroutes, const int ele_len, const int goal_hidenloc4, float * p_route);

/*
 * 将FFBT模型返回的float*p_route转换成为AI可识别的动作指令,后者的编码方式参考resources/key_item_dataformat
 * 输入参数：
 *  己方算子 const struct  BasicOperator* p_bopattacker
 *  对方算子 const struct  BasicOperator* p_bopobj
 *  FFBT格式的路径 float *p_ffbtroute
 *  p_ffbtroute的长度： const int ffbtroute_len == FFBTMODE_ELELEN
 *  AI动作统一编码字段： float *p_aiaction
 *  p_aiaction的长度 ： const int aiaction_len (需要定义一些宏常量)
 * 输出参数：
 *  动作有效 true/ 动作无效false
 */
void cvtFFBTRoute2AIAction(const struct BasicOperator *p_bopattacker,const struct BasicOperator * p_bopobj, const int ffbtroute_len, const float *p_ffbtroute, const int aiaction_len, float *p_aiaction);



/*
 * DA模型原地射击：（我方机动阶段） 我方机动 -> 我方最终  -> 敌方机动 -> 敌方最终
 * 输入参数：
 *  const struct BasicOperator *p_attacker
 *  const struct BasicOperator *p_obj
 * 输出参数：
 *  float * p_static_reward 返回静态射击所预估的战损
 * 返回参数：
 *  bool 是否原地射击标志 true(原地射击) / false (不进行原地射击)
 * 注意：针对目标有无行射能力分别考虑。有行射能力的算子考虑连续两个阶段（我方射击两次，对方射击1次）；无行射能力的算子只考虑到本阶段（连续两个阶段，敌我对射2次可以简化到单个阶段，敌我对射1次）。如果计算的reward >0，返回true, 否则返回false。
 * 
 */
bool checkStaticShooting(const struct BasicOperator *p_attacker, const struct BasicOperator *p_obj, float *p_static_reward);


/*
 * 延迟攻击模型全部针对无行射能力的车辆算子 
 * 0110： 攻击算子无行射能力(0)，载人(1), 目标算子有行射能力(1)，不载人(0)
 * 输入参数：
 *    攻击车辆算子： p_ocar
 *    车上的人员算子： p_opeo
 *    目标算子	p_ucar
 *    const float * p_uniondamage_map 所有算子对攻击算子的综合战损(取max)
 * 输出参数：
 *   struct GA *p_gadaroutes(各个字段的定义参考DAMODE_1_*系列的宏定义，judge.h)
 */
void getDARoutes0110(const struct BasicOperator *p_ocar, const struct BasicOperator *p_opeo, const struct BasicOperator *p_ucar, const float * p_uniondamage_map, struct GA *p_gadaroutes);

/*
 * 延迟攻击模型全部针对无行射能力的车辆算子 
 * 0100： 攻击算子无行射能力(0)，载人(1), 目标算子无行射能力(0)，不载人(0)
 * 输入参数：
 *    攻击车辆算子： p_ocar
 *    车上的人员算子： p_opeo
 *    目标算子	p_ucar
 *    const float * p_uniondamage_map 所有算子对攻击算子的综合战损(取max)
 * 输出参数：
 *   struct GA *p_gadaroutes(各个字段的定义参考DAMODE_1_*系列的宏定义，judge.h),目标算子的射击位置与躲避位置都是初始位置
 */
void getDARoutes0100(const struct BasicOperator *p_ocar, const struct BasicOperator *p_opeo, const struct BasicOperator *p_ucar,const float * p_uniondamage_map , struct GA *p_gadaroutes);

/*
 * 延迟攻击模型全部针对无行射能力的车辆算子
 * 0010: 攻击算子无行射能力(0),不载人(0), 目标算子有行射能力(1),不载人(0)
 * 输入参数：
 *    攻击算子 p_ocar 
 *    目标算子 p_ucar
 *    const float * p_uniondamage_map 所有算子对攻击算子的综合战损(取max)
 *  输出参数：
 *    struct GA * p_gadaroutes(元素定义参考judge.h中的DAMODE_0_* 系列)
 */

void getDARoutes0010(const struct BasicOperator *p_ocar, const struct BasicOperator *p_ucar, const float * p_uniondamage_map, struct GA * p_gadaroutes);

/*
 * 延迟攻击模型全部针对无行射能力的车辆算子
 * 0000: 攻击算子无行射能力(0),不载人(0), 目标算子无行射能力(0),不载人(0)
 * 输入参数：
 *    攻击算子 p_ocar 
 *    目标算子 p_ucar
 *    const float * p_uniondamage_map 所有算子对攻击算子的综合战损(取max)
 *	每个点标识：攻击算子处于该位置，当前态势下敌方所有算子（包括目前处理的算子）对其造成的战损（不带分值）
 *  输出参数：
 *    struct GA * p_gadaroutes(元素定义参考judge.h中的DAMODE_0_* 系列)
 */

void getDARoutes0000(const struct BasicOperator *p_ocar, const struct BasicOperator *p_ucar, const float * p_uniondamage_map, struct GA * p_gadaroutes);

/*
 * DA模型中得到算子所有的动作路径，汇总到p_gadaroutes, 本函数从中选择出最优路径,类似getBestFFBTRoutes
 * 输入参数：
 *    const struct GA *p_gadaroutes DA模型搜索得到的多种路径
 *    const int flag_withpeople 标志是载人还是无人算子
 *    const int ele_len 输入数组的长度（DAMODE_1_ELELEN/ DAMODE_0_ELELEN中二选一）
 *    const int *p_totalblind_map, 对方算子的综合视野盲区
 *	MAP_XNUM * MAP_YNUM大小，数值表明表明算子在该位置能够被对方多少个算子观察到；用来计算最优路径
 *	0 纯盲区
 *	1 只能被敌方一个算子观察到
 *	x 能够被对方x个算子观察到
 *    const int flag_task  任务编号： 进攻 0 防御 1 撤退 2
 *    const int *p_keyloc : 2个(全局关键点+阶段关键点)
 *  输出参数：
 *    float *p_route
 *  返回数值： bool 如果找到最优路径,返回true, 否则返回false
 *  注意： 最优原则以能够进行最大毁伤输出为主。如果最大战损输出相同，看其他选项：
 *	   不载人模型：直接选择第一个最大条目
 *	   载人模型： 尽可能让人晚下车；选择人攻击为主的条目
 *	   该函数仅仅选择出最优条目(route)，该条目如何转换成为python中有效的动作标识需要另一套字段进行定义
 *  注意： 需要考虑p_gadaroutes->count === 0的情况，如果没有候选路径，直接返回false
 *	   BUG: 计算载人模型，算子的剩余机动力可能不足以让人下车，因此，得到的候选路径集合为空，导致在此函数中给出无效的最优路径
 *	   BUG2: 当所有候选路径给出的reward相同的时候，并且==0的时候，表明AB相互不能射击，这时候以最大reward得到的最优路径无意义
 *	   BUG3: 即使reward有大小之分，但是仍存在多个最大reward, 如何区分？
 *		    如果存在多个最优位置，如何继续进行选择？
 *		    1： 尽可能被更少的敌方算子看到(避免遭受多次直接打击)
 *		    2： 尽可能靠近关键点,为下个阶段做好准备（解决此问题可以直接忽略BUG2）
 *	  BUG4: 载人车辆算子不能依靠BUG3忽略BUG2
 *		载人算子的所有动作均有下车，下车本身不够合理；仍然需要判断最优选择是否在候选合理的范围内作出
 *  注意：附加参数
 *    const float * p_uniondamage_map  其他所有算子造成的综合战损
 */

bool getBestDAroute(const struct GA * p_gadaroutes, const int flag_withpeople, const int ele_len , const int *p_totalblind_map, const int flag_task, float *p_route);

/*
 * 转换DA系列route成AI可识别的动作字段，类似cvtFFBTRoute2AIAction()
 * 输入参数：
 *  const struct BasicOperator *p_bopattacker
 *  const struct BasicOperator *p_bopobj
 *  const int flag_withpeople 0 无人/ 1有人
 *  const int daroute_ele 
 *  const float * p_daroute
 *  const int aiaction_len 
 * 输出参数：
 *  float * p_aiaction
 */
void cvtDARoute2AIAction(const struct BasicOperator *p_bopattacker,  const struct BasicOperator *p_bopobj,  const int flag_withpeople, const int daroute_ele,  const float * p_daroute, const int aiaction_len, float * p_aiaction );



/*
 * 转换静态射击过程为AI可识别的动作字段： 如果外部规则决定AI只能进行静态射击（最终射击或者原地射击），则无必要运行DA/FFBT程序，可直接运行静态设计，并返回动作字段
 * 输入参数：
 *  const struct BasicOperator *p_attacker
 *  const struct BasicOperator *p_obj
 *  const int len
 * 输出参数：
 *  float *p_aiaction
 * 注意： 静态射击能够返回： 无效类型字段\ 仅射击类型字段，参考AIACTION_*系列的宏定义
 *	  函数代码参考: rushAiDamageLevelP2P()中的内容: 找出最大毁伤的武器
 *    
 */

void cvtStaticShooting2AIAction(const struct BasicOperator *p_attacker,const struct BasicOperator *p_obj, const int len, float *p_aiaction );

/*
 * 转换算子纯机动动作过程为AI可识别的动作字段，需要进行动作选择（机动、行军）
 * 输入参数：
 *  const struct BasicOperator *p_attacker
 *  const int obj_int6loc
 *  const int len 
 * 输出参数：
 * float * p_aiaction
 */

void cvtRushMoving2AIAction(const struct BasicOperator *p_attacker, const int obj_int6loc,  const int len , float * p_aiaction );


/*
 * 给定算子和目标位置，为算子选择机动方式（机动、行军），选择以当前机动力所能到达最接近目标位置的机动方式
 * 输入参数：
 *  const struct BasicOperator *p_attacker
 *  const int obj_int6loc 
 * 返回数值：
 *  bool true(选择机动方式) / false(行军方式)
 * 注意：因为其中使用到了 trendpathP2P4Pass / whereICanPassRange 函数，所以只针对车辆算子进行判断
 *	如果算子是人员算子，算法直接为算子选择机动模式
 */
bool stateSelectionForRushMoving(const struct BasicOperator *p_attacker, const int obj_int6loc);


/*
 * 辅助函数：计算算子以当前机动力朝目标进行机动，所能到达距离目标最近的六角格与目标六角格的距离
 * 输入参数：
 *  const struct BasicOperator *p_attacker
 *  const int obj_int6loc;
 *  const bool flag_go (true 机动/ false 行军)
 * 返回数值：
 *  int diff : 最近六角格与目标六角格的差距（>=0）
 */
int getErrorForSpecifiedMovingForm(const struct BasicOperator *p_attacker , const int obj_int6loc, const bool flag_go);

/* 
 * 输入参数： p_attacker / p_obj 攻击算子与目标算子
 *	      int shootingtype 射击类型  0 不能射击 1 行间射击 2 机会 3 掩护 4 最终
 *	      float *p_comicumap 辅助可视范围 可视1/不可视0 float*类型
 * 输出参数： float *p_shootingarray  float*类型， 数组长度为8
 * 方法： RUSHMODE_SHOOTINGTYPE 分为静态射击与动态射击，后者需要计算移动范围，以及机动力消耗
*/
void rushAiDamageLevelP2P(const struct BasicOperator *p_attacker, const struct BasicOperator *p_obj, const int shootingtype,
			  const float * p_comicumap, float *p_shootingarray);


/* 计算当前算子与目标位置最短路径上的单步移动位置
 * 输入参数： p_bop
 *	      const  struct HexOfOffset *p_objhex
 * 输出参数： float *p_moveroutearray  数组长度4，参考RUSHMODE_MOVEROUTE_系列的宏定义(judge.h/c)
 * 方法： 内部调用trendpathP2P()函数
 */

void rushAiOptNextRoute(const struct BasicOperator *p_bop, const struct HexOfOffset *p_objhex, float *p_moveroutearray);

/*
 *  给定当前算子与夺控点，找出一条夺控路线（机动->夺控->躲避）
 *  输入参数：
 *    const struct BasicOperator * p_bop 当前算子
 *    int int_cityloc6 城市6位坐标
 *    float * p_totaldamage_map 敌方所有算子对p_bop在每个位置上的单次静态攻击伤害
 *  输出参数：
 *    struct GA * p_ga_occupyingroutes 候选夺控路线的集和，每个位置的元素参照宏定义
 *  返回数值：
 *    true: 路线有效 / false 路线无效
 *  
 */

bool getOccupyingRoutes(const struct BasicOperator* p_bop, const int int_cityloc6, const float * p_totaldamage_map, struct GA *p_ga_occupyingroutes);

/*
 * 从夺控路线候选中选择Best的路线
 * 输入参数：
 *  struct GA * p_ga_occupyingroutes 夺控路线候选
 * 输出参数:
 *  float *p_best_route
 * 返回参数：
 *  bool true; 找到有效夺控路径/ false 未找到有效夺控路径
 * 最优标准：
 *  1 躲避战损最小
 *  2 躲避战损, 躲避剩余机动力最大（尽可能距离夺控点近）
 *  3 三者相同，尽可能处于隐蔽位置（村庄或者树林）
 *
 */
bool getBestOccupyingRoute(const struct GA *p_ga_occupyingroutes, float *p_best_route);


/*
 * 转换夺控路径为AI可识别的动作序列
 * 输入参数：
 *  const struct BasicOperator *p_bop 当前算子
 *  const float *p_best_route 最优路径
 *  const int value_city 城市分数，合并到夺控路径的最终的reward里
 * 输出参数:
 *  float * p_aiaction
 * 返回参数：
 *  true: 有效编码
 *  flase: 无效编码（或者内部错误）
 * 注意事项：
 *  -1 reward计算方法： max(OCCUMODE_DAMAGE_CITY, OCCUMODE_DAMAGE_HIDEN) >= p_bop.obj_blood ; reward == 0， 直接返回无效动作
 *			否则，reward = value_city - max * p_bop.obj_value, 并记录到对应位置上
 *  0 按照当前算子和城市点，躲避点的位置关系；确定AIACTION的类型 10/14(MO)/15(OM)/16(MOM)
 *  1 编码的类型 夺控/ 机动夺控 / 夺控机动/ 机动夺控再机动
 *  2 p_aiaction 的长度是20
 *  3 如何区分夺控与机动的位置属性？
 * */


bool cvtOccupyRoute2AIAction(const struct BasicOperator *p_bop, const float * p_best_route, const float value_city, float * p_aiaction);


/*
 *  针对人员算子和无人战车的守城模型:getDC00Routes() ==> getBestDCRoute() ==》 cvtDCRoute2Aiaction()
 *  输入参数：
 *     const struct BasicOperator * p_bop
 *     const int city_loc
 *     const float city_value
 *     const float * p_totaldamage_map
 *  输出参数：
 *	struct GA * p_ga_dcroutes
 *  返回参数：
 *	输出p_ga_dcroutes是否有效 
 * */

bool getDC00Routes(const struct BasicOperator *p_bop, const int city_loc6, const float city_value, const float * p_totaldamage_map, struct GA * p_ga_dcroutes);




/*  从候选DC路线中选择最优路径
 *  输入参数：
 *	候选路径 struct GA * p_ga_dcroutes
 *	const int flag_withpeople  0(DA00系列) / 1(DA01系列)
 *  输出参数：
 *	float * p_best_dcroute
 *  返回参数
 *	true; 找到最优路径/ false 未找到最优路径
 *  选择标准：
 *	战损最小；/ reward最大
 *	剩余机动力最大
 *	落脚点为隐蔽点
 *
 * */
bool getBestDCRoute(const struct GA * p_ga_dcroutes, const int flag_withpeople, float * p_best_dcroute );


/*
 *  将最优的DC路线转换成为AI可识别的动作编码 p_aiaction 
 *  输入参数：
 *	const struct BasicOperator * p_bop
 *	const float * p_best_dcroute
 *	const int flag_withpeople 0(来自DC00) 1（来自DC01系列）
 *	const int aiaction_len
 *  输出参数：
 *	float * p_aiaction
 *  返回参数：
 *	true/ false 
 *  注意事项：
 *	返回的动作类型： 无效动作/原地不动/纯机动动作
 *	  如果reward<0; 直接返回无效动作
 *	  否则： 判断当前位置与目标位置；然后判断是否进行机动以及机动路线
 *	
 * */
void cvtDCRoute2Aiaction(const struct BasicOperator * p_bop, const float * p_best_dcroute , const int flag_withpeople, const int aiaction_len, float * p_aiaction);



/*
 *  给定候选位置点p_gahexs（'int4loc' => flag）以及最优选择标准p_str_criterion,选出最优点
 *  输入参数：
 *    const struct dictionary * p_gahexs 候选节点集合
 *    const char * p_str_criterion	  选择标准
 *  输出参数：
 *    const struct HexOfOffset * p_hex_o  选择出的最优位置
 *  返回参数：
 *    bool flag	  true: 找到最优位置/ false： 没有找到最优位置
 *  注意事项
 *    1： 2018-06-02：暂时先保证模块能够找出一个点，完成整体框架，后续可进一步精细/筛选标准p_str_criterion
 *
 * */
bool getBestScoutloc(const struct GA *p_gahexs, const char * p_str_criterion, struct HexOfOffset *p_hex_o);

#endif



