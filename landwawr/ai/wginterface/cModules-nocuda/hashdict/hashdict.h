#ifndef HASHDICTC
#define HASHDICTC

/*  
 *   2017年5月7日： 建立文档与基本数据结构
 *   2017年5月27日：修改value的类型，通过sizeof(type)代替type本身，使得该结构能够容纳各种自定义类型
 */

/*
 * dictionary的内存示意图
 * p_dict->table-> keynode_00->next -> keynode_01 -> next ->keynode_02 ->next -> keynode_03->NULL--------
 *	  |->|	       |										|   
 *	  |  |	       ------>|  key_bytenum  |							        |
 *	  |  |	       |       ___ ___ ___                                                              |
 *	  |  |	       ->key->|_k_|_e_|_y_|                                                             |
 *	  |  |	       |         __ __ __                                                               |
 *	  |  |	       ->value->|__|__|__|                                                              |
 *	  |  |                                                                                          |
 *	  l  |-> keynode_10->next -> keynode_11 -> next ->keynode_12 ->next -> NULL----------------	|
 *	  e  |	    |										  |     |
 *	  n  |	    ------>|  key_bytenum  |							        |
 *	  g  |	    |       ___ ___ ___								  |     |
 *	  t  |	    ->key->|_k_|_e_|_y_|							  |     |
 *	  h  |	    |         __ __ __ __							  |     |
 *	  |  |	    ->value->|__|__|__|__|							  |     |
 *	  |  |											  |     |   
 *	  |  |											  |     |
 *	  |->|-> keynode_20->next -> keynode_21 -> next ->keynode_22 ->next -> keynode_23->NULL	  |     |
 *	  |	    |									    |	  |     |
 *	  |	    -------|  key_bytenum  |						    |	  |     |
 *    	  |	    |       ___ ___ ___							    |	  |     |
 *	  |	    ->key->|_k_|_e_|_y_|						    |	  |     |
 *	  |	    |         __ __ __ __						    |	  |     |
 *	  |	    ->value->|__|__|__|__|						    |	  |     |
 *	  |----------------> |value_bytenum|						    |	  |	|
 *	  |->count = count0 + count1 + count2 +...                                          |	  |     |
 *        |            |        |         |_________________________________________________|	  |     |
 *        |            |	|_________________________________________________________________|     |
 *        |            |________________________________________________________________________________|
 *        |  
 *        ->p_findvalue 指向基于key查找到的value
 */ 


#include <stdlib.h> /* malloc/calloc */
#include <stdio.h> /* printf */
#include <stdint.h> /* uint32_t */
#include <string.h> /* memcpy/memcmp */
#include <assert.h> /* assert */

#define INCRE_DICTTHRESHOLD (2.0)
#define INCRE_DICTFACTOR (2)
#define INIT_DICMAX 200

// typedef int (*enumFunc)(void *key, int count, int *value, void *user);


struct keynode {
	struct keynode *next;
	char *key;
	uint8_t key_bytenum;
	char* value;
};
		
struct dictionary {
	struct keynode **table;
	int length, count; // len内存长度，count有效数据长度
	int value_bytenum; // key-value对中value的字节长度 sizeof(type(value))
	char* p_findvalue; // 查找key存在时，保存该key对应的value的首地址，外部通过自定义类型转换获取到该value的具体数据
};

/*  新建字典：
 *  输入参数：const int initial_size 初始化的字典长度，二维keynode数组的行数
 *	      const int value_bytenum 每个keynode中key-value对的value占据的字节数目，代替具体的value类型
 *  返回：字典结构体指针， struct dictionary * 
 *  中间使用了malloc函数，需要外部释放内存
 */
struct dictionary* dic_new(const int initial_size, const int value_bytenum);

/*  删除字典： 删除字典本身与字典内部的key_node指针数组
 *  对应函数： dic_new() 中的malloc / calloc
 */
void dic_delete(struct dictionary* dic);

/*
 * 添加keynote： 中间会遇到重新调整内存大小的操作 dic_resize / dic_reinsert_when_resize 操作
 * 输入参数： struct dictionary *dic
 *	      void* key 
 *	      void* value 一对需要加入的新数值
 *	      const int key_bytenum key的字节数目
 *	      const int value_bytenum value 占据的字节数目
 * 返回：0 当前dic中不存在keynote / 1 当前dic中已经存在keynote 
 * 不论返回0/1， dic->value 均为目标keynote中的value变量的地址，后续可以通过*dic->value设置或者更新value的数值
 */

int dic_add(struct dictionary* dic, void *key,void* p_value, const int key_bytenum, const int value_bytenum);

/*
 *  搜索指定的keynote 
 *  找到返回1，未找到返回0
 *  注意：如果返回1，标识找到，设置dic->p_findvalue为对应value的首地址,在主调函数中调用p_findvalue索引keynode中的value数据
 */
int dic_find(struct dictionary* dic, void *key, int keyn);

// void dic_forEach(struct dictionary* dic);



#endif
