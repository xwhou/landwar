#ifndef JUDGE_
#define JUDGE_


/*
 *  2017年5月16日/gsliu/PAL_Wargame
 *  文件描述：
 *    定义与结果裁决有关的函数与变量
 *  更新说明：
 *    2017年5月16日： 建立文档，函数 damagelevelMap() 以假定目标算子B为基础，将射击算子A对攻击等级图转换成为战损图
 *    2017年5月24日： 增加函数，计算点对点的战损数据，damagelevelP2P();
 *		      增加函数 getDamageLevelP2P() 点对点返回战损等级数据，与fillDamageLevelMapData()相对应
 *		      增加函数 getShootingLocs() 函数，针对目标算子B为攻击算子A在其机动范围之内选择好一组基于特定武器的射击位置
 *		      增加函数 getKeyShootingLocs() 在getShootingLocs()的基础上选择具有最大战损的位置（每个武器选择一个）
 *    2017年5月25日： 增加函数 两种范围计算交集selectSpeicialEleForGA()
 *		      函数： getFFBTRoutesP2P()函数 点对点且战且走模式下基于攻击算子各个武器下的所有策略
 *		      函数： getKeyFFBTRoutesP2P()函数 以getFFBTRoutesP2P()的输出为输入，找出各个武器下的最优策略（战损）
 *		      函数： getOptFFBTRoutesP2P()函数，以getKeyFFBTRoutesP2P()的输出为输入，综合所有武器找出点对点的最有策略
 *		      函数： ffbtOptMap()函数，计算给定攻击/目标算子，基于战损计算各个位置的重要性
 *    2017年5月31日： judge中存放与规则有关的函数，部分来自原来map.h中的函数
 *			icuIsOk() 基于地形判断AB两点是否通视
 *			iouIsOk() 判断攻击算子A是否能够观察到目标算子B,	icuIsOk(A,B) == true
 *			getEleAndDisRectValue() 攻击等级的高程校正
 *			getDamageLevelP2P() 查表索引毁伤等级数据
 *			getRectValueWithoutCond() 毁伤等级的无地形矫正
 *    2017年6月4日： 修改iouIsOk()的接口，提供辅助可视范围参数
 *    2017年8月10日： 判断算子在当前阶段是否进行过机动或者射击，机动或者射击会影响各种机动路线的reward计算
 *		      hasMoved() hasShooted() hasEnoughPower() 分别标识算子在给定的阶段stageID是否机动过，射击过，有无剩余机动力;
 *		      isInMyStage()当前阶段是我方阶段？
 *    2017年8月23日： 修复icuIsOk函数的BUG，isViewBeInterruptted()函数的输入有问题，少了一个六角格
 *		      修复isViewBeInterruptted()函数的BUG， 实现刚刚被遮挡的情况
 *
 *    2017年8月28日： 重新按照陶总的规则修改icuIsOk()函数，以像素坐标为基础进行计算。
 */


#include <stdlib.h>
#include <assert.h>
#include "map.h" /* attacklevelMap  与 目标算子的地形信息*/
#include "operator.h" /* 解析utilities.c/h中主调函数的算子参数 */

/*  宏定义部分 */

#define PI 3.141592
// 行军道路相关的宏定义
#define LIMIT_BLACKRED_PASS 8    // 乡村道路[黑色，编码0]上的行军格子数目限制
#define LIMIT_REDROAD_PASS 14    // 一般公路[红色，编码1]上的行军格子数目限制
#define LIMIT_ORANGEROAD_PASS 18 // 等级公路[橙色，编码2]上的行军格子数目限制

// 通视范围相关的宏定义
#define PEOPLE 1     // 人的标志
#define CAR 	2     // 车的标志
#define MAXIOUDIS_PEOPLE 10	  // 人的最大观察距离
#define MAXIOUDIS_CAR 25	  // 车的最大观察距离


// 攻击等级高程矫正的宏定义
#define ZM_ELVATIONRECT_ROW 8		// 全局变量直瞄武器高程修正表的行数（对人/车一致）
#define ZM_ELVATIONRECT_COL_PEOPLE 10	// 高程修正表对人的列数
#define ZM_ELVATIONRECT_COL_CAR 12	// 高程修正表对车的列数

//  战损表格尺寸相关的宏定义
#define	  DAMAGELEVEL_DIM_TABLE_ROW 11 // 每张战损表格的行数 11
#define   DAMAGELEVEL_DIM_TABLE_COL 10 // 战损表格的列数 10
#define   DAMAGELEVEL_DIM_TABLE_SIZE (DAMAGELEVEL_DIM_TABLE_ROW * DAMAGELEVEL_DIM_TABLE_COL)  // 战损表格的尺寸
#define   SRC_MAXBLOOD 5 // 射击算子的最大车班数
#define	  DES_MAXBLOOD 5 // 目标算子的最大车班数目
#define   DES_MAXARMLEVEL 5 // 目标算子的最大装甲等级

// 战损相关的攻击者的武器类型（直瞄武器/步兵轻武器）与目标类型（人/车）的标志
#define	  DAMAGELEVEL_ZM2CAR 0	      // 直瞄武器对车
#define   DAMAGELEVEL_ILW2CAR 1	      // 步兵轻武器 Infantry light weapons对车
#define	  DAMAGELEVEL_ALLW2PEOPLE  2  // 所有类型的武器对人

// 直瞄武器对车的战损表格数目 src_blood * des_blood * des_arm_level
#define   DAMAGELEVEL_DIM_ZM2CAR_HEIGHT ( SRC_MAXBLOOD * DES_MAXBLOOD * DES_MAXARMLEVEL) 
// 步兵轻武器对车的战损表格数目 des_blood * des_arm_level 
#define	  DAMAGELEVEL_DIM_LTF2CAR_HEIGHT ( DES_MAXBLOOD * DES_MAXARMLEVEL) 
// 所有武器对人的战损表格数目  des_blood
#define   DAMAGELEVEL_DIM_ALLW2PEOPLE_HEIGHT ( DES_MAXBLOOD) 

// 游戏想定中关于回合，阶段与时节数目的宏定义
#define	  GAMEXD_NUM_HUIHE 5  // 回合数目
#define	  GAMEXD_NUM_STAGE 4  // 每个回合的阶段数目
#define	  GAMEXD_NUM_SHIJI 3  // 每个阶段的时节数目

/* 全局变量的使用 */
extern float g_p_damagelevel_zm2car[DAMAGELEVEL_DIM_ZM2CAR_HEIGHT * DAMAGELEVEL_DIM_TABLE_SIZE] ;
extern float g_p_damagelevel_ltf2car[DAMAGELEVEL_DIM_LTF2CAR_HEIGHT * DAMAGELEVEL_DIM_TABLE_SIZE];
extern float g_p_damagelevel_allw2people[DAMAGELEVEL_DIM_ALLW2PEOPLE_HEIGHT * DAMAGELEVEL_DIM_TABLE_SIZE];


/*
 * 通视函数icuIsOk()内部需要使用的辅助函数
 * 输入参数 
 *  const int obj_int4loc tar_int4loc test_int4loc 观察点，目标点，中间测试点的四位整形坐标
 *  const int obj_ele tar_ele test_ele 对应坐标位置的高程
 *  const int distance 观察点与目标点的六角格距离
 * 返回数值：
 */
bool seeStop(const int obj_int4loc, const int tar_int4loc, const int test_int4loc, const int obj_ele, const int tar_ele,  const int test_ele, const int distance);


/* 基于地形判断两个六角格之间是否通视
 * 输入参数：
 *	  const struct HexOfOffset *p_hexa, p_hexb(前者为主动观察目标，后者为被动观察目标)
 *	  const int maxdistance 默认最大观察距离，在特殊地形条件下需要减半
 * 隐式输入参数：从map.c/h中获取对应六角格的地形信息
 * 返回数值： 通视判断结果，true(1) 通视/ false(0) 不通视
 * 注意：
 *	六角格范围检查放在外层调用者上面
 *	p_hexa / p_hexb 有严格顺序，a为观察者所处六角格，b为目标所处六角格
 *	规则：
 *	  纯通视规则：高程遮挡, 计算连线上的六角格序列，基于高程信息判断是否通视， 为核心计算模块
 *	  地形影响： 1 目标处于丛林、居民地六角格，视线上有丛林、居民地六角格 不通视
 *		     2 目标处于丛林、居民地六角格，实现上无丛林、居民地六角格 观察距离减半
 *		     3 观察者与目标均处于丛林、居民地时候，书上规则为不通视，视频规则（新）为依赖规则2进行判断
 *	
 *	2018-03-14：函数内部封装了icuIsOk_com /icuIsOk_cache，并根据是否有缓存数据选择不同的模式，com表示计算，cache表示读取缓存
 */
bool icuIsOk(const struct HexOfOffset *p_hexa, const struct HexOfOffset *p_hexb, const int maxdistance);
bool icuIsOk_com(const struct HexOfOffset *p_hexa, const struct HexOfOffset *p_hexb, const int maxdistance);
bool icuIsOk_cache(const struct HexOfOffset *p_hexa, const struct HexOfOffset *p_hexb, const int maxdistance);

/*
 *  检测两个六角格观察线的六角格是否遮挡了观察视线
 *  输入参数 const int ele_a / ele_b 端点六角格的高程
 *	     const int *p_ele_excluded_onlinehexs 中间六角格高程
 *	     const int len 中间六角格的个数（对应p_ele_excluded_onlinehexs的内存长度）
 *  返回数值 bool true 观察视线被遮挡 / false 未被遮挡
 */

bool isViewBeInterruptted(const int ele_a, const int ele_b, const int *p_ele_excluded_onlinehexs , const int len);

/*
 * 检查算子A能够观察到算子B
 * 输入参数： const struct BasicOperator *p_bopa (观察者) / p_bopb (目标)
 *	      const float *p_comicumap 辅助可视范围参数 1（目标位置可视） / 0 （目标位置不可视）
 * 返回参数： bool 可观察 true / 不可观察 false
 * 方法：
 *  首先应该在icuIsOk()的基础上进行判断,本函数考虑了目标算子的状态信息
 *    目标算子处于遮蔽：观察距离减半，与地形有关，已经在icuIsOk()中进行了判断
 *    目标算子处于掩蔽状态：观察距离减半
 *    目标算子处于遮蔽地形+掩蔽状态：观察距离减半再减半
 *
 */
bool iouIsOk(const struct BasicOperator *p_bopa, const struct BasicOperator *p_bopb);
// bool iouIsOk(const struct BasicOperator *p_bopa, const struct BasicOperator *p_bopb, const float *p_comicumap);

/*
 * 获取武器对应的基于高程与距离的攻击等级修正数值
 * 输入参数： const struct HexOfOffset *p_o_hexa 攻击者位置
 *	      const struct HexOfOffset *p_o_hexb 目标位置
 *	      const int object_type 目标类型 1（人） 2（车）
 * 返回参数： int 需要修正的攻击等级
 * 注意：
 *	  中间需要计算攻击位置与目标位置的高度差以及距离差
 *	  攻击位置与目标位置的参数顺序保持一致
 *	  如果攻击位置处于较低高程，按照表格进行修正，否则不做修正，返回数值0
 * 注意： 
 *	  如果传入的算子在无效六角格的位置，不进行修正
 */
 int  getEleAndDisRectValue(const struct HexOfOffset *p_o_hexa, const struct HexOfOffset*p_o_hexb, const int object_type);

/*  给定参数读取指定战损文件，战损表格中的指定行/列的战损数据，由于是P2P模式，直接返回战损数据
 *  输入参数： 攻击算子 const struct BasicOperator *p_attacker,
 *	       目标算子 const struct BasicOperator *p_objective,
 *	       战损文件标志：读取哪个战损文件（DAMAGELEVEL_ALLW2PEOPLE/ DAMAGELEVEL_ZM2CAR / DAMAGELEVEL_ILW2CAR 3选1）
 *	       攻击算子对目标算子所造成的攻击等级 const int attacklevelvalue
 *  返回参数： float  索引到的战损数据
 *  注意：  如果输入数据不符合规则：攻击等级==0 / 血量有问题 直接返回无效战损 DAMAGVALUE_INVALID
 */
float  getDamageLevelP2P( const struct BasicOperator *p_attacker,
			  const struct BasicOperator *p_objective, 
			  const int flag_wz2obj,
			  const int attacklevelvalue);

/*
 * 根据输入参数确定本次使用哪张战损表格
 * 输入参数： const int flag_wz2obj 攻击类型标志
 *	      const int src_blood 射击算子的车班数
 *	      const int des_blood 目标的车班数
 *	      const int des_arm_level 目标的装甲等级
 * 输出参数： float *p_damagetable_data 需要使用的战损表格的首地址
 */
float*  getCorrepondingDamageLevelTable(const int flag_wz2obj, const int src_blood, const int des_blood, const int des_arm_level);

/*
 * 根据射击者与目标算子的状态，预先判断无地形条件下的随机数修正
 * 输入参数： const struct BasicOperator *py_p_bopa, const struct BasicOperator *py_p_bopb
 * 返回参数： 无地形条件下的随机数修正
 * 注意：
 *    py_p_bopa -> obj_keep 1压制/0无压制
 *    py_p_bopa -> obj_hide 1隐蔽/0无隐蔽
 *    py_p_bopa -> obj_pass 0 机动 / 2 短停（暂时不加入） / 其他（行军）
 *    如何确定堆叠？
 */

int getRectValueWithoutCond(const struct BasicOperator *py_p_bopa, const struct BasicOperator *py_p_bopb);

/*
 *  函数说明：获取从六角格A=>B所消耗的机动力
 *  输入参数： const struct HexOfOffset * p_hexa
 *	       const struct HexOfOffset * p_hexb
 *  输出参数：void
 *  返回参数：int 类型的机动力消耗数值
 *	      当没有缓存数据；或者消耗机动力超过算子的最大机动力max_ep == 8时候，返回默认数值（-1）
 *	      否则返回缓存中的机动力消耗数据
 *  注意事项：需要在有缓存数据的条件下调用，否则返回100(较大数值)
 *  
 * */

// int getUsedPower(const struct HexOfOffset * p_hexa, const struct HexOfOffset* p_hexb);

#endif

