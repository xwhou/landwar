#ifndef WEAPON_
#define WEAPON_

/*********************************************
 *2017年5月4日/gsliu/PAL_Wargame
 *基本功能：
 *  2017年5月12日 使用struct结构定义武器与算子的属性，与python中定义的结构体保持一致
 *  2017年9月12日 重构武器数据结构，武器以武器编号进行索引，从map.h/c中读取武器属性表；
 *
 *
 ********************************************/


#include <stdlib.h>
#include <stdio.h>
#include <wchar.h>
#include <locale.h>
#include <assert.h>
#include "common.h"
#include "./hashdict/hashdict.h" /* struct dictionary */ 

/* 宏定义*/

// 武器属性字段的列索引的宏定义
// 注意射程的+1原则（射程为0）


#define MAX_AIMRANGE  (20+1)  // 最大射程
#define MAX_OBJNUM    5	      // 算子的最大车班数

#define LOC_WP_OBJTYPE  0   // 武器类型变量列索引，该位置变量数值为1（针对人）/ 2（针对车）/ 0（人车均可）
#define LOC_WP_AIMRANGE_PEO 1 // 对人射程
#define LOC_WP_AIMRANGE_CAR 2 // 对车射程
#define LOC_WP_F0     3 // 暂时无意义（占位）
#define LOC_WP_F1     4 // 暂时无意义（占位）
#define LOC_WP_F2     5 // 暂时无意义（占位）
#define LOC_WP_DLDATASTART_PEO	(LOC_WP_F2+1) // 对人攻击等级数据的起始位置
#define LOC_WP_DLDATASTART_CAR	(LOC_WP_DLDATASTART_PEO + MAX_OBJNUM * MAX_AIMRANGE)  //对车攻击等级数据的起始位置

#define HEIGHT_WPTABLE 9					    // 武器属性表的高度，武器数
#define WIDTH_WPTABLE (LOC_WP_F2+1 + MAX_AIMRANGE * (MAX_OBJNUM+1)) // 武器属性表的宽度

// 关于武器射击前的检查
#define ERROR_WEAPENCHECK_INDEXOUTOFBOUND -10		      // 武器编号不在算子武器列表内部，程序逻辑错误
#define ERROR_WEAPENCHECK_HAVESHOOTED	  -9		      // 武器所属的算子已经在本阶段已经射击过，所有武器均不能射击
#define ERROR_WEAPENCHECK_TYPEDONOTMATCH  -8		      // 武器类型与目标类型不匹配
#define ERROR_WEAPENCHECK_HAVENOAMMUNITION -7		      // 武器没有弹药
#define ERROR_WEAPENCHECK_OUTOFSHOOTINGRANGE -6		      // 目标超过武器的有效射程，需要使用六角格距离进行判断
#define ERROR_WEAPENCHECK_OK		  1		      // 武器检查正常


// 关于武器类型的宏
#define WEAPENTYPE_LTF 0 // 步兵轻武器
#define WEAPENTYPE_ZM  1 // 直瞄武器

/* 宏定义,不同类型的武器的数量 */
#define	  NUM_PEOPLE_WEAPONS 6  // 能够攻击人的武器数量
#define	  NUM_CAR_WEAPONS 7      // 能够攻击车的武器数量
#define	  NUM_DAODAN_WEAPONS 2   // 导弹类武器的数量

/* 定义类型 */
#define bool int
#define true 1
#define false 0

// 扩展全局变量
extern const int people_ids[NUM_PEOPLE_WEAPONS];
extern const int car_ids[NUM_CAR_WEAPONS];
extern const int daodan_ids[NUM_DAODAN_WEAPONS];

/*
 * 从武器属性表格中获取数据段，返回数据段指针
 * 输入数据
 *    struct dictionary * p_dic_wptable  武器属性表
 *    const int int2_wpid     // 武器编号
 *    cosnt int index_start   // 待索引数据的首地址的位置
 *    const int index_end     // 带索引数据的末地址的位置
 * 返回数值：
 *    int * p_data
 * 注意：
 *    索引按照[index_start, index_end)的格式
 *    该函数获取的是数据段的首地址
 */

int * getSpecifiedDataPointeFromWPTable(struct dictionary *p_dic_wptable, const int int2_wpid, const int index_start, const int index_end);

/*
 *  获取指定位置的数据
 *  输入参数：
 *    struct dictionary *p_dic_wptable 
 *    const int wpid  //武器ID
 *    cosnt int index_col
 *  输出参数：
 *    int 有效数据 （-1为无效数据）
 *
 */
int getSpecifiedColDataFromWPTable(struct dictionary *p_dic_wptable, const int wpid, const int index_col);

/*
 *  获取指定武器类型
 *  输入参数
 *    struct dictionary *p_dic_wptable
 *    cosnt int wpid 
 *  输出参数
 *    武器类型（对人射击还是对车射击） 0 1 2 (无效数据 -1 )
 */
int getWPObjtype(struct dictionary *p_dic_wptable, const int wpid);

/*
 * 获取武器射击
 * 输入参数 
 *  struct dictionary *p_dic_wptable
 *  const int wpid 
 *  const int tar_type 人（1） 对车（2）
 *
 * 返回参数
 *  int 攻击距离 / 无效返回 -1
 *  
 */
int getWPAimrange(struct dictionary *p_dic_wptable, const int wpid, const int tar_type); 

/*
 *  获取对人/车的攻击攻击等级的数据段的首地址
 *  输入参数：
 *    struct dictionary *p_dic_wptable 
 *    const int blood_att 攻击算子的血量
 *    const int wpid  
 *    const int tar_type  1 人 / 车 
 *  输出参数
 *    int * p_data (有效数值) / NULL 无效数值
 *  注意：
 *    对人不考虑攻击车班数的问题, 返回的是最原始的首地址; 为什么? 已经修正为考虑人员算子的血量
 */
int * getDLStartDataPointer(struct dictionary *p_dic_wptable, const int blood_att, const int wpid, const int tar_type); 


/*
 * 武器类型与武器编号的一致性检查，确保该武器能够攻击到指定类型的算子
 * 输入：
 *  struct dictionary *p_dic_wptable
 *  const int weaponid 武器编号
 *  const int obj_type 要攻击的算子类型
 * 返回数值：
 *  bool 该武器（weaponid）能够攻击该类型(obj_type)的算子 true / 不能攻击 false 
 * 注意： 
 *  需要进行二次检查（武器属性表格/ 静态数组）
 */

bool checkWeaponIDandType(struct dictionary *p_dic_wptable , const int wpid, const int tar_type);


/*
 * 给定武器编号，检查该武器是否是导弹类型的武器
 * 输入参数：
 *  const int weaponid,
 * 返回数值：
 *  bool true(导弹类武器) / false(非导弹类武器)
 *
 */ 
bool checkWeaponIsDaoDan(const int weaponid);


/* 给定算子编号，检查该武器是否是步兵轻武器
 * 输入参数： 
 *  const int weaponid,   武器编号 
 * 返回数值：
 *  bool true(是) / false (否)
 *  
 */
bool checkWeaponIsLTF(const int weaponid);

#endif

