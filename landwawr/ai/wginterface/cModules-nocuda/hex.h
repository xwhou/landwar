/*
 *  2017年5月5日/gsliu/PAL_Wargame
 *  基本功能：
 *    与六角格/坐标系相关的数据结构与函数定义
 *  更新
 *    2017年5月5日 建立文档/定义立方坐标六角格HexOfCude，偏移坐标六角格HexOfOffset/两者之间的转换函数
 *		   定义外部接口函数：外部接口均以偏移坐标为标准，内部计算会涉及到立方坐标
 *		   对应函数： cvtHexFromCubeToOffset / cvtHexFromOffsetToCube
 *    2017年5月5日 定义SeqHexsOfOffset/SeqHexsOfCube 六角格序列结构体/ 
 *		   计算给定两个偏移坐标下的六角格连线上的所有六角格，保存在SeqHexsOfOffset数据结构中
 *		   对应函数： getHexsOnLineOfCube / getHexsOnLineOfOffset / freeSeqHexsCube 
 *    2017年5月5日 定义六角格方向等常量/ 获取指定方向或者全部方向上的六角格
 *    2017年5月7日 在偏移坐标下计算当前六角格的6个相邻六角格 getNeighborHexsOfOffset() 
 *    2017年5月10日 修正icuIsOk()函数： 按照《兵棋推演》59中有关距离与高程变化的关系
 *		    遍历以当前六角格为圆心，在指定半径下的所有六角格，填充序列 
 *    2017年5月24日 增加函数： 计算两个偏移坐标六角格之间的距离 getDistanceBetweenHexOfOffset 内部调用getDistanceBetweenHexOfCube()
 *    2017年5月27日 去掉SeqHexsOfOffset， SeqHexsOfOffset等类型，统统换成GA类型,
 *		    更新所有使用了SeqHexsOfOffset的函数
 *		    增加函数：getHexsOnRingOfOffset() 六角格基于指定半径的环形序列
 *    2018-06-01：  增加函数模块：计算指定方位（方向）和区域范围（距离区间（最大距离和最小距离））上的六角格集合
 *		    （1）首先计算六角格集合和中心六角格在cube坐标系下的偏移向量
 *		    （2）通过偏移量计算最终的六角格坐标
 */

#ifndef HEX_
#define HEX_

#include <stdlib.h>
#include <assert.h>
#include <math.h> /* round */

#include "queue.h" /* struct Queue */
#include "common.h" /* cvtIntLocTo4StrOffLoc */
#include "hashdict.h" /* struct dictionary */ 
#include "general_array.h" /* struct GA */

#define DIRECTION_NUM 6
extern int g_dir_map[DIRECTION_NUM];

/* 数据结构定义部分 */

// 立方六角格坐标结构体, 内部计算使用
struct HexOfCude{
  int q;
  int r;
  int s;
};
// 立方六角格浮点坐标结构体
struct HexOfCudeInFraction{
  double dq;
  double dr;
  double ds;
};
// 偏移坐标六角格结构体，与外部接口交互使用
struct HexOfOffset{
  int row;
  int col;
};


/*函数声明 */

/* 
 * 立方坐标转换到偏移坐标 
 * 输入与输出：均为对应结构体的指针，需要提前为输出数据p_hex_o 申请内存空间
 *
 */
void cvtHexFromCubeToOffset(const struct HexOfCude * p_hex_c, struct HexOfOffset * p_hex_o);

/*  
 *  偏移坐标转换为立方坐标
 *  输入与输出：指针类型，提前申请内存空间
 */

void cvtHexFromOffsetToCube(const struct HexOfOffset * p_hex_o, struct HexOfCude * p_hex_c);

/*
 *  计算两个立方坐标之间的六角格距离， 曼哈顿距离的1/2
 *  输入：两个立方六角格指针
 *  返回值：距离（int）
 */
int getDistanceBetweenHexOfCube(const struct HexOfCude *p_c_hexa, const struct HexOfCude * p_c_hexb);

/*
 * 计算两个偏移坐标之间的六角格的距离，内部调用getDistanceBetweenHexOfCube()
 * 输入参数：const struct HexOfOffset *p_o_hexa, p_o_hexb
 * 输出参数：距离(int)
 */
int getDistanceBetweenHexOfOffset_com(const struct HexOfOffset *p_o_hexa , const struct HexOfOffset *p_o_hexb);

/*
 *  计算两个立方六角格上的之间（t=[0,1]）的浮点立方六角格
 *  输入：立方六角格
 *	  double t[0,1] t = 0时，返回p_c_hexa, t=1时，返回p_c_hexb, 均以浮点类型返回（数据的复制）
 *  输出：返回浮点六角坐标
 */

void getCubeLerp( const struct HexOfCude * p_c_hexa, const struct HexOfCude *p_c_hexb, const double  t, struct HexOfCudeInFraction * p_f_hex);

/*  
 *  将浮点六角格坐标圆整到整形六角格坐标上
 *  输入：浮点六角格坐标的数据指针
 *  输出：整形六角格坐标的数据指针
 */

void cubeRound (const struct HexOfCudeInFraction * p_f_hex, struct HexOfCude *p_c_hex);


/*
 *  计算任意两个偏移hex直线上的所有偏移hexs， 利用立方坐标计算，并进行转换
 *  输入：  两个偏移hex的数据指针
 *  输出：  hexs序列，存储结构为GA类型 p_gahexsoffset
 *  
 */

void getHexsOnLineOfOffset(const struct HexOfOffset *p_o_hexa, const struct HexOfOffset * p_o_hexb, struct GA *p_gahexsoffset);

/*
 * 同getHexsOnLineOfOffset, 在立方坐标下进行实际计算
 * 谁申请，谁释放机制
 */

void getHexsOnLineOfCube(const struct HexOfCude * p_c_hexa, const struct HexOfCude * p_c_hexb, struct GA* p_gahexscube);


/*
 *  计算相邻六角格（基于偏移坐标）
 *  输入参数： const struct HexOfOffset * p_o_hex 
 *  输出参数： 6个方向上的六角格组成的序列数据 struct GA *p_gahexsoffset
 */
void getNeighborHexsOfOffset(const struct HexOfOffset *p_hex_o, struct GA *p_seq_hexs_o );


/*
 *  辅助函数：在立方坐标下基于当前hex在指定方向与步长的六角格
 *  输入参数： 当前六角格 cosnt struct HexOfCude *p_hex_c 
 *	       指定方向 const int dir [0,6)
 *	       指定步长 const int step [0,+NAN）
 *  输出参数： struct HexOfCude *p_hex_c
 */

 void getHexInSpecifiedDirAndStepOfCube(const struct HexOfCude *p_hex_c, const int dir, const int step, struct HexOfCude *p_rhex_c);



/*
 * 计算指定中心p_centorhex_o，指定半径radius的环形六角格序列
 * 输入参数：环中心 const struct HexOfOffset *p_centorhex_o 
 *	     环半径 const int radius
 * 输出参数：const GA * p_gahexsoffset 环序列
 * 注意： radius = 0 返回环中心位置的单个元素
 *	  radius = 1 等价调用getNeighborHexsOfOffset()函数
 *	  radius > 1 序列长度 radius * 6 
 */

void getHexsOnRingOfOffset(const struct HexOfOffset *p_centorhex_o, const int radius, struct GA *p_gahexsoffset);
/*
 *  找到指定圆心与半径范围内的所有偏移坐标下的六角格
 *  输入参数  圆心坐标 const struct HexOfOffset *p_centorhex_o
 *	      指定半径 const int radius， radius>=0 
 *  输出参数  返回指定范围内的所有六角格序列 struct GA *p_gahexsoffset
 *  注意：  内部调用 getHexsOnRingOfOffset()函数
 */

void getHexsInCircleOfOffset(const struct HexOfOffset *p_centorhex_o, const int radius, struct GA *p_gahexsoffset);

/**
 *  给定方向,距离区间（最小距离和最大距离），返回立方坐标下的偏移向量（相对于中心点）
 *  输入参数：
 *    const int dir	  方位【0，5】
 *    const int mindis , maxdis	    距离区间（【mindis, maxdis)）
 *  输出参数：
 *    struct GA * p_gaoffvecs;
 *
 *  返回参数： 
 *    bool flag
 *
 *  注意事项：
 *    1: 计算偏移向量的算法是归纳出来的，立方坐标下应该会有解析数值解！
 *    2: mindix >= 1
 **/

bool getDirOffVectorSet(const int dir, const int mindis, const int maxdis, struct GA* p_gaoffvecs);


#endif
