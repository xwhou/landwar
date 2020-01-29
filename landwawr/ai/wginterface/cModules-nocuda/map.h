#ifndef MAP_
#define MAP_

/*
 *  2017年4月26日/gsliu/PAL_Wargame
 *  基本功能
 *    读取python中的地图数据，为特征生成模块提供其所需要的数据信息
 *  更新过程：
 *    2017年5月4日  测试读取python传来的numpy（2d-array）结构的地图数据
 *		    函数  cCheckReadNumpyIntData()
 *    2017年5月6日  定义struct Map_Attr 地图属性结构体/ 实例化全局变量g_map_attr/删除cCheckReadNumpyIntData()函数...
 *		      其主要功能融合到initMapAttr()函数中
 *		    函数  initMapAttr() / freeMapAttr() 
 *		    定义 strcut Map_EdgePower 六角格单边机动力消耗全局变量g_map_eptable / 初始化与内存释放
 *		    函数  initMapEdgePower() / freeMapEdgePower()
 *		    函数  地图上任意两个六角格判断通视icuIsOk() / 基于当前六角格计算可视范围icuMap()
 *    2017年5月7日  对可视范围存有疑问？
 *		    基于当前机动力/位置/g_map_eptable ==> 计算可机动范围，函数 whereICanGoMap()
 *    2017年5月10日 修正可视范围函数icuIsOk()： 地形对高程的更新 / 地形对观察目标的遮蔽作用 / 通视规则
 *		    主要函数：观测视线是否被遮挡的函数 isViewBeInterruptted()
*		    加入攻击等级函数  attacklevelMap(), 并在utilities.h中进行封装被python调用
*     2017年5月12日 修正icuIsOk错误，gridtype == 3 为遮蔽 /  (gridtype == 2 + cond == 7) 同样也是遮蔽
*		    之前只考虑了gridtype==3的情况, 将六角格是否位于遮蔽区域封装到函数 checkHexIsInCover()中
*     2017年5月15日 在攻击等级中加入高差与距离的攻击等级修正，该修正与被攻击对象的类型人或者车有关系
*		    rectification about elevation and distance
*		    增加两个全局变量：直瞄武器对车/人的攻击等级高度修正表格 g_zm2soilder_elerect_table 
*									    g_zm2car_elerect_table
*		    增加函数 getEleAndDisRectValue(hex0, hex1, object_type) 读取攻击等级高差修正表格
*		    修改函数 1：attacklevelMap()增加参数: const int flag_elerect 该武器（不）需要（0）1 高差修正
*				const int object_type 该武器的射击目标类型 1(人) 2（车），读取哪个表格
*			     2：针对攻击等级添加高差修正
*     2017年5月16日 修正icuMap attacklevelMap 函数的接口，参数float * p_map_data 全部转换为strcut GA *p_ga
*		    三张图像统一返回模块计算出来的感兴趣的 位置+属性 序列，保存到p_ga中，然后统一返回到外部主调函数中
*		    注意： 同类型的函数whereICanGoMap没有修正接口，仍然使用p_map_data，模块内部依赖p_map_data记录中间结果
*     2017年5月24日 增加计算攻击等级的点对点函数 attacklevelP2P();
*		    增加计算机动方位whereICanGoMap的GA输出版本 whereICanGoGA()
*     2017年5月27日 hex.h/c中去掉了SeqHexsOfOffset,map.c/h中进行修正
*		    整理冗余全局变量 g_map_layout可以只保留地图宽度与高度，合并g_map_attr/g_map_eptable 后者本身为地图属性的一部分
*     2017年5月31日 去掉mapc/h中与地图属性无关的函数模块，将各种特征地图存放在features.c/h中，map.c/h只负责索引地形数
*     2017年8月16日 在全局变量中加入道路网的邻接表 dic_loc2roadnet;
*		    数据格式： key(centor_str4loc) -> value([13位整数]: n n0_int4loc t0 ... n5_int4lo, t5)
*		    其中centor_str4loc标识当前道路六角格的索引，n标识当前六角格扩展出的道路六角格的数目， 
*		    ni_str4loc标识第i个相邻道路六角格的坐标，ti 标识第i个六角格和中心六角格的连线（道路类型）
*		    0 乡村道路（黑色）/ 1 红色道路 / 2 等级公路橙色
*		    每个条目的有效个数： 1 + n * 2 
*    2017年8月16日  修改initMapAttr()的函数接口，读取道路网的邻接矩阵表； 对应更新freeMapAttr()函数
*    2017年8月18日  定位距离指定六角格最近的道路六角格, 找到返回 true, 未找到返回 false; getNeighRoadHex()
*    2017年8月28日  更新通视模块icuIsOk()，以及该模块需要的辅助数据:每个六角格对应的左上角的像素坐标；
*		    坐标信息加入到全局变量g_map_attr.dic_loc2geodata中的后两位上（0：行 / 1列）
*		    补充函数获取六角格对应的像素坐标(y,x) getMyPixelLoc()
*   2017年8月29日   给定相邻的两个道路六角格，返回两者之间的道路类型
*   2017年9月11日   增加全局变量，dic_wpid2attrs（武器编号=>武器属性）
*   2018年3月14日   通视信息表 dic_pairlocs2icudis，放在g_map_attr中，数据格式，(a_row*100+a_col) * 10e5 + (b_row * 100 + b_col) * 10 + flag(实际上没有必要！)
*
*/

#include <stdio.h>
#include <stdlib.h>
#include "hex.h" /* HexOfOffset, GA, Quene 等 */
#include "time.h"

/* 宏函数 */
#define max(x,y) (x>y ? x:y)
#define min(x,y) (x<y ? x:y)


/* 宏定义 */

// 地图布局相关
#define MAP_YMAX 70
#define MAP_XMAX 66
#define ELEVATION_QUANINTER 20	  // 地图设置：每单位高程20m (注意common.h中有关于绝对像素坐标的宏定义，一旦换地图，需要更新)
#define BOARDER_WIDTH 3 // 屏蔽地图边缘3格
//#define MAP_YMAX 60
//#define MAP_XMAX 51
#define MAP_XMIN 0
#define MAP_YMIN 0
#define MAP_XNUM (MAP_XMAX - MAP_XMIN)
#define MAP_YNUM (MAP_YMAX - MAP_YMIN)

// 地图像素六角格相关
#define  FirstID  0
#define  HexRowWidth  52 // JAVA代码中出现HexWidth,我重命名为HexRowWidth, 为和HexRowHeight保持一致
#define  HexRowHeight  90
#define  HexHalfWidth  (HexRowWidth / 2)  
#define  HexHalfRowHeight (HexRowHeight / 2)

// 道路类型相关的宏定义
#define BLACKROAD_TYPE 0    //黑色道路，编码0，乡村道路
#define REDROAD_TYPE 1	    //红色道路，编码1，一般公路
#define ORANGEROAD_TYPE	2   //橙色道路，编码2，等级公路

// 地图六角格相关
#define HEXPIC_HEIGHT 58 // 六角格图片高度（像素单位）
#define HEXPIC_WEIGHT 58 // 六角格图片宽度（像素单位）


/* 标记Map中data_attr各个列对应的属性含义，便于索引 */
// Map.data_attr中一共4列，分别为 gridid / cond / gridtype / elveaiton
#define CONDLOC 0		  // 地质 0 普通 / 6 松软地 / 7 居民地 : 暂时不用，不可信
#define GRIDIDLOC 1		  // HEX/文件夹下的子图编号
#define GRIDTYPELOC 2		  // 六角格类型 0 普通 / 1 水系 / 2 道路 / 3 遮蔽 
#define ELEVATIONLOC 3		  // 高程信息所在的位置
#define PIXELROWLOC  4		  // 六角格在地图上像素坐标的行
#define PIXELCOLLOC  5		  // 六角格在地图上像素坐标的列

// 定义传入到全局变量g_map_attr不同属性的矩阵的列的长度
#define COLNUM_GEOMAT 6
#define COLNUM_EPMAT 6
#define COLNUM_ROADNETMAT 13
#define COLNUM_WPTABLE	  132


/* 全局变量声明 */
extern struct Map_Attr g_mapattr;
extern struct Map_Stage g_mapstage;

/* 数据结构/类型定义 */

// Map_Attr 集成与地图属性(位置：高程、地形地貌、机动力消耗表等)相关数据
struct Map_Attr
{
  struct dictionary * dic_loc2geodata;	        // 四位坐标chars4loc 映射到该坐标下六角格的地质信息表
  struct dictionary * dic_loc2epdata;		// 坐标==>进入该坐标下六角格的单边机动力消耗表
  struct dictionary * dic_loc2roadnet;		// 四位坐标 => 道路网的邻接表
  struct dictionary * dic_wpid2attrs;		// 武器编号（2位数字） ==> 武器属性
  struct dictionary * dic_pairlocs2icudis;	// 地图通视信息:位置对=>位置对之间的六角格距离（存储在该字典中的位置对默认通视）
  struct dictionary * dic_pairlocs2pow;		// 地图机动力消耗信息：位置对==> 位置A到位置B消耗的机动力（存储的位置对默认可以以最大机动力（7）达到）
  struct dictionary * dic_pairlocs2dis;		// 位置对之间的距离表(有效数据为30，因此表中没有的位置对需要单独计算)
};


// Map_Stage 状态属性(在对战过程中算法会用到的实时态势信息) 
// 1 被发现程度：用在路径规划中 和 DA模型最优路径选择中 getBestDAroute()函数

struct Map_Stage{
  int * p_sawcount_map;	    // 算子被发现程度，使用前更新，使用后重置

};


/* 函数方法定义  */

/*
 *  初始化地图的地质信息以及机动力消耗信息，主要在于填充g_mapattr的数据
 *  输入参数：const int *p_geodata 地质信息，首列代表4位整形六角格坐标，剩余列为宏定义CONDLOC等标记
 *	      const int *p_epdata 单边机动力消耗信息 首列为4位整型六角格坐标，剩余6列代表从6个方向进入该六角格的机动力消耗
 *	      const int *p_roadnet 道路网的邻接表，14列，首个元素为4位整形六角格坐标，后续作为字典的key, 剩余13列作为values
 *	      const int georows,  const int geocols
 *	      const int eprows,  const int epcols // 上述两块数据的行列数目
 *	      const int rnetrows , const int rnetcols // p_roadnet代表的二维数组的行列尺寸
 *  输出参数：未指定，默认写入到全局变量g_mapattr的两个数据表中
 */

void initMapAttr(int *p_geodata, int *p_epdata, int *p_roadnet, int *p_wptable, const int georows, const int geocols, const int eprows, const int epcols, const int rnetrows, const int rnetcols, const int wprows, const int wpcols);


/*
 * 函数说明： 加载缓存数据：通视信息表
 * 输入参数： const int * p_1d_icudata 1D 整形树组，存放数据格式 (a_row*100+a_col) * 10e5 + (b_row * 100 + b_col) * 10 + flag
 *	      const int len_icu , 树组长度
 * 输出参数： void
 * 返回参数： void 
 * 注意事项： 将数据保存在g_mapattr.dic_pairlocs2icudis中，格式为key['posa_int4loc*10000 + posb_int4loc'] ==> value [dis]
 * */

void initIcuCacheData(const int * p_1d_icudata, const int len);

/*
 * 函数说明： 加载缓存数据：机动范围表
 * 输入参数： const int * p_1d_wicgdata 1D 整形树组，存放机动范围表 yyxxyyxxzz从位置yyxx移动到yyxx需要消耗的机动力zz，zz>=0 && zz <= max_ep的位置对
 *	      const int len 树组长度
 * 输出参数： void
 * 返回参数： void 
 * 注意事项： 将数据保存在g_mapattr.dic_pairlocs2pow中，格式为key['posa_int4loc*10000 + posb_int4loc'] ==> value [used_power]
 * BUG0: g_mapattr.dic_pairlocs2pow 保留的是车辆算子从A到B的机动力消耗，不适用于人员算子
 * */

//void initWicgCacheData(const int *p_1d_wicgdata, const int len);

void initWicgCacheData(const long long *p_1d_wicgdata, const int len);


/*
 * 函数说明：加载缓存数据，距离表
 * 输入参数：const long long * p_1d_disdata, const int len_dis
 * 输出参数：数据格式yyxx|yyxx|di(s) 442的格式，填充到g_mapattr.dic_pairlocs2dis中 
 * 返回参数：void 
 * 注意事项：1 数据指针是long long *
 *	     2 距离表中的有效距离为0-30（见genData.py中的max_dis），因此，距离表中不存在的位置对，需要计算
 *	     3 该数据同样用于gpu中对应数据的初始化
 * 
 * */

void intiDisCacheData(const long long * p_1d_disdata, const int len);
/*
 * 释放全局变量g_mapattr内部的两个字典
 */

void freeMapAttr();

/*
 *  得到全局变量g_map_attr中p_data_attr中的指定行与指定列上的数据
 *  输入参数：	const struct HexOfOffset *p_hex // 定位行
 *		const int col // 定位列
 *		const int object_type ： 0 人 / 1 车， 确定最大观测距离
 *  输出参数：	int （有效数据>=0） / <0 无效数据（不存在行）
 *  注意： 使用该函数之前先进行六角格有效性的检查
 *
 */

int getMySpecifiedColDataFromGMapAttr(const struct HexOfOffset* p_hex, const int col);

/*  辅助函数: 根据偏移六角格获取高程信息
 *    内部调用getMySpecifiedColDataFromGMapAttr()函数
 *  输入： const struct HexOfOffset * p_hex
 *  输出： 高程（int） 或者 -1（地图上无词六角格）
 */

int getMyElevation(const struct HexOfOffset *p_hex);


/*  辅助函数: 根据偏移六角格获取高程信息
 *    内部调用getMySpecifiedColDataFromGMapAttr()函数
 *  输入： const struct HexOfOffset * p_hex
 *  输出： 高程（int） 或者 -1（地图上无词六角格）
 */

int getMyGridtype(const struct HexOfOffset *p_hex);

/*
 * 辅助函数：计算给定六角格的cond 属性，同getMyElevation / getMyGridtype 函数
 * 输入： const struct HexOfOffset *p_hex
 * 输出： 具体的cond数值
 */

int getMyCond(const struct HexOfOffset *p_hex);

/*
 * 辅助函数 从地图中获取给定六角格的hex图像编号，同getMyGridtype()函数
 * 输入 ： cosnt struct HexOfOffset *p_hex
 * 输出： 指定图像编号
 */
int getMyHexNum(const struct HexOfOffset *p_hex);

/* 给定相邻的两个六角格，返回两者之间的道路类型编号，0/1/2
 * 输入参数：
 *  const struct HexOfOffset *p_hexa, *p_hexb
 * 返回数值：
 *  -1(无效) / 0（乡村） / 1（一般公路） / 2 （等级公路）
 */
int getRoadTypeBetweenHex(const struct HexOfOffset *p_hexa, const struct HexOfOffset *p_hexb);


/*
 * 辅助函数： 获取给定六角格对应的像素坐标
 * 输入参数： const struct HexOfOffset *p_hex
 * 输出参数： double *y , double *x
 * 返回值：bool 找到对应的像素坐标(true), 否则返回false
 */

bool getMyPixelLoc(const struct HexOfOffset *p_hex, double *y, double *x);

/*
 * 函数说明：计算两个偏移坐标之间的六角格的距离，内部调用getDistanceBetweenHexOfCube()
 * 输入参数：const struct HexOfOffset *p_o_hexa, p_o_hexb
 * 返回数值：距离(int)
 * 注意事项：1 首先查表g_map_attr.dic_pairlocs2dis
 *	     2 表中不存在，调用getDistanceBetweenHexOfOffset_com进行计算
 *	     3 调用getDistanceBetweenHexOfOffset_com之后需要更新字典dic_pairlocs2dis
 *	     4 BUG0 2018-03-27：C计算模式比C缓存模式（查表)快20倍左右，因此直接采用C缓存模式
 */

int getDistanceBetweenHexOfOffset(const struct HexOfOffset *p_o_hexa , const struct HexOfOffset *p_o_hexb);

/*
 * 检查一个偏移坐标的六角格是否在地图中
 * 输入参数: const struct HexOfOffset * p_hex_o
 * 返回值： 0 不在 / 1 在
 */
bool checkHexIsValid(const struct HexOfOffset *p_hex);

/*
 * 检查一个偏移坐标的六角格是否在地图有效边界范围内（BOARDER_WIDTH,MAX-BOARDER_WIDTH）
 * 输入参数: const struct HexOfOffset * p_hex_o
 * 返回值： 0 不在 / 1 在
 */
bool checkHexIsInValidRange(const struct HexOfOffset *p_hex);

/*
 * 检查当前六角格是否处于遮蔽地址位置
 * gridtype == 3 或者 gridtype == 2 && cond == 7
 * 输入参数： const struct HexOfOffset *p_hex_o
 * 输出参数： 0 不在/ 1 在
 *
 */
bool checkHexIsInCover(const struct HexOfOffset *p_hex);

/*
 * 检查当前六角格是否为道路六角格，道路六角格的标志GRIDTYPELOC位置是否为2
 * 输入参数 const struct HexOfOffset *p_hex
 * 输入参数： 0 不是道路 / 1 是道路 
 */
bool checkHexIsRoad(const struct HexOfOffset *p_hex);

/*
 *  辅助函数： 判断六角格为普通六角格0，居民地六角格1，丛林六角格2， 工事六角格3
 *  输入参数： const struct HexOfOffset *p_hex
 *  输出参数： 六角格标志 int 
 *  如何判断丛林与居民地
 *    hex 52 丛林
 *    hex 51 居民地
 *    gridtype == 2 && cond == 7 居民地
 *    其他 = 0 
 */

int getCorrepondingHexFlagCond(const struct HexOfOffset *p_hex);
/*
 *  返回进入指定方向的相邻六角格所需要的机动力
 *  输入参数： const int int_loc 整形偏移坐标( row * col)
 *	       const int direction_flag [0-6)
 *  返回数值： int needed_poer 需要的最小机动力
 */
int getEnterHexNeededPower(const int int_loc, const int direction_flag);


/*
 * 定位距离指定六角格最近的道路六角格
 * 输入参数：
 *  const struct HexOfOffset *p_objhex 指定六角格
 *  const int dis_threshold   阈值（最近邻的标准）
 * 输出参数：
 *  struct HexOfOffset *p_neighhex
 * 返回参数：
 *  在指定阈值内部找到最近六角格，返回true, 否则返回false 
 * 注意：
 *  按照环形在指定六角格上进行搜索
 */

bool getNeighRoadHex(const struct HexOfOffset *p_objhex, const int dis_threshold, struct HexOfOffset *p_neighhex);

/*
 * 转换像素坐标为四位整形坐标，参考陶总的GID(X，Y)
 * 输入参数： int pixel_row, int pixel_col 像素坐标的行索引，列索引
 * 返回参数：对应的六角格的四位整形坐标
 * 注意：来自袁如意老师的代码
 */
int getInt4locFromPixelLoc(int pixel_row, int pixel_col);


/*
 *  给定中心坐标（偏移坐标系下）和立方坐标的偏移向量集合，计算偏移六角格集合（偏移坐标集合）
 *  输入参数：
 *    const struct HexOfOffset *p_hex
 *    const int dir 
 *    const int mindis, maxdis
 *  输出参数：
 *    struct GA * p_gahexs
 *  返回参数：
 *    bool
 *  注意事项：
 *    1 内部调用了getDirOffVectorSet()函数，注意GA对象的资源释放
 *    2 mindis >= 1
 *    3 内部调用了checkHexIsValid()对候选点进行了检查
 *
 */

bool getDirHexSet(const struct HexOfOffset *p_hex, const int dir, const int mindis, const int maxdis, struct GA * p_gahexs);



#endif
