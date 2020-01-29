#ifndef GENERAL_ARRAY_
#define GENERAL_ARRAY_

/*
 *  2017年5月16日/gsliu/PAL_Wargame
 *  文件描述
 *    定义一个广义增量的数组数据类型
 *    数组中的每一个元素是一块指定大小与类型的内存条(数组)，存储该元素的所有属性信息
 *    所有的元素通过general_array结构统一管理
 *    图示说明：
 *			  __ __ __ __ __ __ __	 __ __ __ __ __ __ __	__ __ __ __ __ __ __	    __ __ __ __ __ __ __
 *     p_ga --> p_data ->|0 |1 |2 | 3|4 |5 |6 |	|		     | |		    |......|			|
 *     |		 |__|__|__|__|__|__|__|	|__ __ __ __ __ __ __| |__ __ __ __ __ __ __|	   |__ __ __ __ __ __ __|
 *     |------->	 |<-p_ga->ele_len(7)->|
 *     |------->      	 |<----------------------p_ga->count(3)---------------------------->|
 *     |------->      	 |<----------------------p_ga->capacity(N) ---------------------------------------------------->|
 *     |------->      	 |<----------------------p_ga->capacity_len(N*7) ---------------------------------------------->|
 *
 *    其中GA中的每一个元素是一个数组，数组中包含了p_ga->ele_len个相同类型的该数组的属性信息
 *    所有的元素与属性信息占据一块连续的内存
 *    capacity为GA的p_data的虚拟元素（数组）数量
 *    capacity_len为p_data的虚拟属性数量
 *
 *
 *  更新时间：
 *    2017年5月16日： 建立文档，定义数组
 *    2017年5月27日： 更改ga_init()函数接口，使general_array数据类型能够任意类型和任意长度的元素
 *		      原函数接口： struct GA * ga_init (const int init_capacity, const int ele_len);
 *		      新函数接口： struct GA ga_init (const int ele_num, const int ele_len, const int attr_bytenum);
 *			1 利用属性的字节长度扩展属性类型本身,使得属性可以支持自定义的struct类型
 *			2 虽然可以用自定义的struct类型使得ele_len==1，但是ele_len仍然有意义，用来支持不定长数组
 *    2017年5月27日： 增加函数：ga_setele() 设置指定元素的数值
 *				ga_getele() 得到指定元素的首地址，外部获取该元素
 *    2017年5月27日： 引入inline关键字设定 ga_getattr()， ga_getele()函数
 *		     
 *
 */

#include <stdlib.h> /* calloc */
#include <assert.h> /* assert */     
#include <string.h> /* memcpy */     
#include <stdio.h> /* printf */     

/*  宏定义部分 */
#define INIT_GAMAX 200 // 初始化的虚拟元素个数
#define INCRE_GATHRESHOLD  (0.9) // 数组自增长的系数（有效元素/虚拟元素）阈值
#define INCRE_GAFACTOR 2 // 自增长的比例



/*  数据类型定义 */

struct GA
{
  int count ;		    // 有效元素数量 (有多少个数组)
  int attr_bytenum;	    // 每个属性所占据的字节长度（以后按照字节数目申请内存，与类型无关）
  int ele_len ;		    // 每个元素中包含的属性个数（每一个元素为一个数组，该数组的长度）
  int ele_bytenum;	    // 元素的字节长度 = ele_len * attr_bytenum 
  int capacity;		    // 当前p_data所允许的元素数量的最大值
  int capacity_len;	    // 当前p_data的属性个数 = capacity * ele_len
  char* p_data;		    // 内存数据，用char*细化到字节上，p_data++意味着移动一个byte,与attr_bytenum相对应

};

/* 函数声明部分 */
/*  初始化
 *  输入参数：const int ele_num 初始化GA时候申请ele_num个有效元素 >=0
 *	      const int ele_len 每个数组结构的长度，每个元素的属性个数
 *	      const int attr_bytenum 利用属性的字节长度代替属性类型本身来申请内存
 *  返回：    struct GA *p_ga 生成好的对象的指针
 *  注意：该函数与ga_delete 成对使用
 */

struct GA * ga_init (const int init_capacity, const int ele_len, const int attr_bytenum);

/*
 *  释放p_ga的资源
 */
void ga_delete(struct GA *p_ga);

/*  自增长函数
 *  对p_ga->p_data进行扩展，同时更新p_ga->capacity 和 p_ga->capacity_len 
 */

void ga_incre(struct GA *p_ga);

/*  在p_ga->p_data中append一个元素数组p_ele
 *  输入参数： p_ga
 *	       void * p_ele 需要append进来的数组元素的首地址, void*设定可以接受任何类型的指针，在内部转换成为需要的char*类型
 *	       const int ele_len p_ele的元素个数（用于验证是否和p_ga->ele_len相等）
 *	       const int attr_bytenum 属性类型（验证是否和p_ga->attr_bytenum相等）
 */
void ga_appendele(struct GA *p_ga, void* p_ele, const int ele_len, const int attr_bytenum);

/*  设置指定元素ele_loc的数值 
 *  输入参数： struct GA* p_ga
 *	       void *p_ele 要设定的数值变量的首地址
 *	       const int ele_len 元素数值的属性个数
 *	       const int ele_loc [0,p_ga->count) （检验字节长度）
 *	       const int attr_bytenum 属性字节（检验字节长度）
 */
void ga_setele(struct GA * p_ga , void* p_ele, const int ele_loc, const int ele_len, const int attr_bytenum );



/*
 *  获取指定元素ele_loc的首地址，外部使用该地址索引指定元素
 *  输入参数： const struct GA *p_ga
 *	       const int ele_loc  [0,p_ga->count)
 *  返回参数： void* ele_index的地址，调用者需要自己转换成为合适类型
 */
 void *ga_getele(const struct GA* p_ga, const int ele_loc);

/*  获取指元素ele_len指定属性attr_loc的首地址，利用该地址索引指定属性
 *  输入参数： p_ga
 *	       const int ele_loc 指定元素位置
 *	       const int attr_loc 指定属性位置
 *  返回数值： void* 指向目标属性的指针，在外部程序时候需要转换成为具体的属性类型  (float*)ga_getattr(p_ga, 1, 1)[0] 
 */

void* ga_getattr(const struct GA *p_ga, const int ele_loc, const int attr_loc );

#endif 
