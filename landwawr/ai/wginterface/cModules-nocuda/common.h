#ifndef COMMON_
#define COMMON_

/* 
 *  2017年5月7日/gsliu/War_game
 *  文件描述
 *    汇总常用的工具函数（4/6位坐标转换等）, 宏定义等
 *  更新  
 *    将map.h中的cvtIntLocTo4StrOffLoc itoa两个函数移动到本文件中
 *    6位chars_loc转换为偏移坐标 cvtChars6locToOffsetIntLoc()
 *    2017年5月24日 将偏移坐标抓换成为6位chars类型的坐标 cvtOffsetIntLocToChars6()
 *		    将偏移坐标抓换成为整数化的int6类型 cvtOffsetIntLocToInt6()
 *    2017年5月26日 修复错误：函数cvtChars6locToOffsetIntLoc()六位坐标转换为四位坐标，前2后2变成前2后3
 */


#include <stdlib.h>
#include <stdio.h> /*printf*/
#include <string.h> /* memcpy */
#include <assert.h> /* assert */
#include <math.h> /* floor */



#define bool int 
#define true 1
#define false 0


/* 函数声明部分 */

/*
 * 整数转换成为字符串
 *  输入参数：num   需要转换的数字
 *	      str   转换结果
 *	      radix 进制 默认为10
 *  输出参数：返回转换结果
 */
char* itoa(int num,char*str,int radix);

/*
 * 将小于4位数的整数补充为4位字符串:在开头位置补充'0'
 *  e.g. 0 > '0000' / 1 > "0001" / "1000" > "1000
 *  输入参数： int_loc	    小于或者等于4位的整数 [0-9999]
 *	       str_4_offloc 转换结果 对应六角格的四位偏移坐标，需要提前申请好内存空间，大小为参数3定义
 *	       arr_char_len str_4_offloc的内存大小，按照字节定义，设置为5（包含最后'\0'）
 */
bool cvtIntLocTo4StrOffLoc(const int int_loc, char *str_4_offloc, const int arr_char_len);

/*  6位chars_loc转换为偏移坐标中的行与列
 *  规则：
 *    后2位为奇数： row = 前2位 * 2 + 1 / col = （ 后2位 -1 ）/ 2
 *    后2位为偶数： row = 前2位 * 2 / col = 后2位/2
 *  输入参数  char * chars_6_loc 
 *  输出函数  int* p_row / p_col
 *  注意
 *    保证chars_6_loc内存够7位 e.g ==> 170023'\0' => 35/11 
 */
void cvtChars6locToOffsetIntLoc(const char * chars_6_loc, int * p_row, int *p_col);

/*
 * 将偏移坐标转换为6位字符串
 * 输入参数： const int row
 *	      const int col
 * 返回数值： 6位char类型==>整数化之后的int6loc
 * 方法：
 *	根据行/列取出前半部分tmpfirst, 后半部分tmplast return tmpfirst*10000 + tmplast
 *	以该函数为基础，结合整数==>字符串补'0'函数 cvtIntLocTo4StrOffLoc(), 找到真正的6位chars索引
 */
int cvtOffsetIntLocToInt6(const int row, const int col);


/*  利用cvtChars6locToOffsetIntLoc, cvtIntLocTo4StrOffLoc, 将int6loc转换成为int4loc
 *  输入参数： const int int6loc
 *  返回参数： int4loc
 *  注意：中间调用cvtChars6locToOffsetIntLoc, cvtIntLocTo4StrOffLoc两个函数
 */
int cvtInt6loc2Int4loc(const int int6loc);

/*  寻找输入数组的最大值
 *  输入参数： p_arr
 *	       len
 *  输出参数： 最大数值以及索引
 *  返回数值： 输入数组长度有效，len > 0, 返回true, 否则返回false
 *  注意：  浮点数
 */  
bool findmaxfloat(const float *p_arr, const int len, float * p_maxvalue, int *p_maxindex);


/* 
 *  拼接两个算子的位置为一个联合字符串
 *  输入： const  int int6loca 六位整数坐标
 *	   const  int int6locb
 *	   const  len_comchar = 13
 *  输出： char * p_comchar
 *
 * */
void getComLocFrom2Int6Locs(const int int6loca , const int int6locb, const int len_comchar, char* p_comchar);
#endif

