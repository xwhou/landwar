#ifndef OPERATOR_
#define OPERATOR_


#include <stdlib.h> 
#include <assert.h> /* assert */
#include "weapen.h" /* struct  BasicWeapen*/
#include "common.h"   /* cvtChars6locToOffsetIntLoc/ cvtIntLocTo4StrOffLoc */

/*
 *  2017年5月7日/gsliu/PAL_Wargame
 *  文件描述：
 *    和算子相关的数据结构与函数的定义
 *  更新记录：
 *    2017年5月7日  定义算子结构体 struct BasicOperator(与python中定义的类型保持一直，二者相互通信)
 *    2017年5月10日 封装const struct BasicWeapen结构体，返回算子中关于BasicWeapen的一些属性信息的函数
 *		    函数： getSpecifiedWeaponAttackLevelData() // 返回算子中指定武器的攻击等级数据指针
 *			   getSpecifiedWeaponAttackAim() // 返回算子中指定武器的攻击距离
 *    2017年5月16日 增加函数 getLocOfOffsetFromOperator() 根据算子生成偏移坐标
 *    2017年5月24日 增加函数 算子武器在开火前进行检查 checkSpecifiedWeaponBeforeShooting()
 *		    增加辅助函数：返回算子指定的武器类型武器 getSpecifiedWeaponType()
 *		    辅助函数： 更新算子的位置坐标 updateOperatorLoc()
 *    2017年8月15日 使用算子的堆叠状态obj_stack完成对战损的精准矫正(堆叠需要在python中更新算子属性时手工设置)
 *    2017年8月18日 在BasicOperator中添加数据obj_army,与 game_color, obj_type 放在一起组成的字符串可以作为算子的唯一标识
 *    2017年8月31日 增加武器编号与其攻击类型的检查函数checkWeaponIDandType()
 */





/* 数据类型定义 */

struct BasicOperator
{
  int obj_id;		  //  算子自身ID（算子有唯一性）
  int room_id;		  //  该算子属于哪个房间（房间唯一性质）
  int user_id;		  //  操作员ID（谁控制该算子）
  int game_color;	  //  游戏双方 红：0，蓝：1 =ObjFlag=ObjColor
  //  wchar_t* obj_name;	  //  算子的汉语名称（坦克棋子、炮兵棋子、战车棋子）
  int obj_army;		  //  111 标记算子属于1连1排1班,与game_color合并在一起，可以作为算子的唯一标识
  // wchar_t * obj_ico;	  //  算子名称=ObjName
  int obj_type;		  //  算子类型 人：1，车：2
  int obj_typex;	  //  算子类型的进一步细化 坦克 0 / 战车 1 / 人员 2

  int a1;		  //  行进间射击能力 无：0 有：1
  int d1;		  //  行军：单位机动力移动的格子数目
  int d3;		  //  行军总格数目
  int b0;		  //  装甲类型 无装甲：0，轻型装甲：1，中型装甲：2，重型装甲：3，复合装甲：4
  int s1;		  //  对人观察距离
  int s2;		  //  对车观察距离

  int obj_pos;		  //  当前位置Y 
  int obj_lastpos;	  //  上一时刻位置，用于同格交战不败后的位置回退
  float obj_step;	  //  剩余机动力
  float obj_stepmax;	  //  算子机动力上限

  int obj_pass;		  //  车辆机动状态 机动：0 行军：非0  短停：2
  int obj_keep;		  //  是否被压制 否：0 是：非0
  int obj_hide;		  //  是否遮蔽 否：0 是：非0
  int obj_round;	  //  是否已机动 否：0 是：非0
  int obj_attack;	  //  是否已射击 否：0 是：非0
  int obj_tired;	  //  疲劳度 正常：0 一级疲劳：1 二级疲劳：2
  int obj_stack;	  // 算子是否处于堆叠状态？ 1 处于/ 0 不处于
  int obj_tongge;	  // 算子当前处于同格交战状态的标志位
  int obj_tonggeorder;	  // 主动同格2 / 被动同格1
  int obj_tonggeshootcountleft; // 同格交战环节，剩余的射击次数

  int obj_blood;	  //  当前车班数
  int c2;		  //  剩余导弹数
  int c3;		  //  剩余弹药数

  int obj_wznum;	  //  关联武器数量
  int obj_maxwznum;	  //  所允许关联的最大武器数量


  // int *p_obj_wpids;	  //  关联的武器ID的数组（数组长度为obj_maxwznum, 有效长度为obj_wznum）
  int p_obj_wpids[5];	  //  关联的武器ID的数组（数组长度为obj_maxwznum(5), 有效长度为obj_wznum）
  /*
  int obj_wz0;
  int obj_wz1;
  int obj_wz2;
  int obj_wz3;
  int obj_wz4;
  */
  int obj_sup;		  // 0 算子没有在车上， 1 算子在车上
  int obj_space;	  //  运兵数量上限
  int obj_sonnum;	  //  当前运兵数量
  int obj_sonid;	  //  乘车的步兵算子的ID（一辆车最多放一个班，使用int类型即可）
  float obj_value;	  //  算子分值

  // 算子的模型属性
  int obj_flagtask;	  // 基于态势的任务分配 0 进攻 / 1 防御 / 2 撤退
  int obj_flagmoving;	  // 限制战车/人员算子的机动能力(便于进行最终射击)
  int is_visible;	  // 该算子是否能够被对方看到,能(1)不能(0)

  // 策略AI的标记
  int obj_actstate;	  // 算子激活态标记，处于激活态(1)的算子才能进入策略图生成动作
  int obj_canshoot;
  int obj_canoccupy;
  int obj_cansuicide;
  // sgr 增加算子的索引信息，对应算子在GPU中的特征
  int obj_index;
};

//  基本张量
struct BasicTensor
{
  int ndim;	  //  维度数目
  int* p_shapes;  //  各维大小 (维度权重从高到低：行->列)
  float* data;	  //  核心数据	(和地图尺寸保持一致)
};


/*  函数定义部分 */

/*
 * 基于给定算子计算六角格偏移坐标
 * 输入: const struct BasicOperator *p_bop 给定算子
 * 输出参数: int * p_cur_row / p_cur_col 坐标变量地址
 */

void getLocOfOffsetFromOperator(const struct BasicOperator *p_bop, int *p_cur_row , int *p_cur_col);

/*
 * 检查算子能否进行射击
 * 输入参数： struct dictionary *p_dic_wptable; 武器属性表
 *	      射击算子 const struct BasicOperator *p_attacker
 *	      目标算子 const struct BasicOperator *p_objective 
 *	      射击算子拟采用的武器编号 const int weapen_index 
 *	      两个算子之间的六角格距离 const int distance 判断目标是否在射程内
 * 返回数值： 在weapen.h中定义的各种武器射击检查的宏常量
 *	      检查 目标类型，射程与攻击距离
 */

int  checkSpecifiedWeaponBeforeShooting(struct dictionary *p_dic_wptable, const struct BasicOperator *p_attacker, const struct BasicOperator *p_objective, const int weapen_index, const int distance);

/*
 * 更新算子的位置坐标
 * 输入参数： struct BasicOperator *p_bop 
 *	      const int row
 *	      const int col
 * 输出参数： 更新坐标后的p_bop
 */
void updateOperatorLoc(struct BasicOperator *p_bop, const int row, const int col);

/*
 * 返回算子中中指定武器的tartype
 * 输入参数： struct dictionary *p_dic_wptable
 *	      const struct BasicOperator *p_bop
 *	      const int i  第i件武器
 *	      
 * 返回数值：
 *	    返回第i件武器的射击类型 0 / 1 / 2 / -1 无效
   int getSpecifiedWeaponTartype(struct dictionary *p_dic_wptable,  const struct BasicOperator *p_bop, const int i);
 */


/*
 *  返回算子指定武器的武器类型（人员轻武器还是直瞄武器） id == 29?
 *  输入参数：
 *    const struct BasicOperator *p_bop
 *    const int i     武器索引
 *  返回参数
 *    int WEAPENTYPE_ZM / WEAPENTYPE_LTF
 *  内部调用weapen.h/c中的checkWeaponIsLTF()函数
 */
int getSpecifiedWeaponType(const struct BasicOperator *p_bop, const int i);


/*
 * 返回算子中中指定武器的射程
 * 输入参数： struct dictionary *p_dic_wptable
 *	      const struct BasicOperator *p_bop
 *	      const int i  第i件武器
 *	      const int tar_type 针对人 1 还是针对车 2
 * 返回： int  找到的武器攻击等级数据指针
 * 注意：内部进行武器检查，如果武器与算子类型不匹配，返回-1
 */

int getSpecifiedWeaponAttackAim( struct dictionary *p_dic_wptable,  const struct BasicOperator *p_bop, const int i ,const int tar_type);

/*
 * 返回算子中中指定武器的攻击等级数据指针
 * 输入参数： struct dictionary *p_dic_wptable  武器属性表
 *	      const str BasicOperator *p_bop	      指定算子
 *	      const int i			      指定武器编号 
 *	      const int tar_type		      针对人 1 还是针对车 2
 * 返回： int * 找到的武器攻击等级数据指针 / NULL （武器与类型不匹配）
 * 注意： 
 *	内部检查了武器编号与其能够攻击的算子类型，如果类型不匹配，返回NULL；
 *	内部封装 weapen.h/c中的getSpecifiedDataPointeFromWPTable()函数
 */

int * getSpecifiedWeaponAttackLevelData(struct dictionary *p_dic_wptable, const struct BasicOperator *p_bop, const int i ,const int tar_type);

/*
 * 计算当前算子中有效的武器列表函数：根据算子的当前状态，剩余弹药数目等
 */
int* getSpecifiedWeaponAttackLevelData(struct dictionary *p_dic_wptable, const struct BasicOperator *p_bop, const int i, const int tar_type );

// 保留一个空位函数


#endif
