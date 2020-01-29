#ifndef QUEUE_
#define QUEUE_

/*
 *
 *  2017年5月8日/gsliu/PAL_Wargame 
 *  文件描述：
 *    实现自增长的queue数据结构
 *  2017年5月8日： 完成基本功能： queue_init/ queue_delete / queue_push / queue_pop
 *		   问题： queue_pop中还需要再加入动态所见内存的功能 
 */

#include <stdlib.h> /* calloc */
#include <assert.h> /* assert */
#include <string.h> /* memcpy */
#include <stdio.h> /* printf */





/*  宏定义 */

#define INITMAX 200		// 初始队列长度
#define INCRE_THRESHOLD (0.8)	// 有效数据超过当前内存长度的80%时候，申请更多的内存
#define INCRE_FACTOR 2		// 增长系数 = 下一次申请的内存空间 / 当前的内存空间

typedef int ELEMENT_TYPE;

/* 定义基本数据结构 */
struct Queue
{
  ELEMENT_TYPE *data;		  // 动态申请内存
  int  mem_len ;	  // data的内存长度 ( 以sizeof(ELEMENT_TYPE)为基本单位 )
  int  front, tail;	  // 分别指向有效数据的首部/  尾部的下一个位置
  int  count;		  // 有效数据长度 = tail - front 
};


/* 函数定义 */

/*
 *  初始化一个新的queue对象
 *  输入参数： int mem_len 指定初始的内存长度；如果为0， 使用INITMAX
 *  返回    ： struct Queue * p_queue
 */

struct Queue * queue_init(int mem_len);

/*
 *  释放一个queue对象
 *  输入参数： struct Queue *p_queue
 */
void queue_delete(struct Queue *p_queue);


/*
 *  在队列末尾添加一个元素, 时刻检查是否需要 调整重置有效数据段的位置 或者 申请新的内存空间
 *  输入参数 队列对象指针 struct Queue * p_queue
 *	     新元素的指针 ELEMENT_TYPE * p_newone
 */
void queue_push(struct Queue * p_queue, const ELEMENT_TYPE * p_newone);


/*
 *  取出队列第一个元素
 *  输入参数： 对类对象指针 struct Queue * p_queue
 *  输出参数： 队列首个元素的地址 ELEMENT_TYPE * p_firstone
 *  返回数值： int 0(队列为空，不存在首地址) / 1(队列非空，获取到有效首地址)
 */

int queue_pop (struct Queue *p_queue, ELEMENT_TYPE * p_firstone);

#endif
