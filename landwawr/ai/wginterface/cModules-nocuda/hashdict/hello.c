//#include <sys/time.h>
//
#include <stdio.h>
#include "hashdict.h"
/*
struct dictionary* dic_new(const int initial_size, const int value_bytenum);

  *  删除字典： 删除字典本身与字典内部的key_node指针数组
   *  对应函数： dic_new() 中的malloc / calloc
  /
  void dic_delete(struct dictionary* dic);

  
   * 添加keynote： 中间会遇到重新调整内存大小的操作 dic_resize / dic_reinsert_when_resize 操作
   * 输入参数： struct dictionary *dic
   *	      void* key 
   *	      void* value 一对需要加入的新数值
   *	      const int key_bytenum key的字节数目
   *	      const int value_bytenum value 占据的字节数目
   * 返回：0 当前dic中不存在keynote / 1 当前dic中已经存在keynote 
   * 不论返回0/1， dic->value 均为目标keynote中的value变量的地址，后续可以通过*dic->value设置或者更新value的数值
 

  int dic_add(struct dictionary* dic, void *key,void* p_value, const int key_bytenum, const int value_bytenum);


   *  搜索指定的keynote 
   *  找到返回1，未找到返回0

  int dic_find(struct dictionary* dic, void *key, int keyn);

*/
int main() {

    int k = 1;
    while (k--)
    {
      struct dictionary* dic = dic_new(10, sizeof(int)*2);
      printf("count = %d, length = %d, value_bytenum = %d\n", dic->count, dic->length, dic->value_bytenum);
      for(int i = 0 ; i < 10000 ; i ++)
      {
	char key[6]="AAAAA";
	key[0]+= (i%10);
	key[1]+= (i%10);
	key[2]+= (i%10);
	key[3]+= (i%10);
	key[4]+= (i%10);
	key[5]+= '\0';
	int value[2] = {i*2,i*2+1};
	printf("cur_key = %s\n", key);
	dic_add(dic,key,&value,6,sizeof(int)*2);
      }
      printf("count = %d, length = %d, value_bytenum = %d\n", dic->count, dic->length, dic->value_bytenum);
      for(int i = 0 ; i < 20000 ; i ++)
      {
      	char key[6]="AAAAA";
	key[0]+= (i%20);
	key[1]+= (i%20);
	key[2]+= (i%20);
	key[3]+= (i%20);
	key[4]+= (i%20);
	key[5]+= '\0';
	if(dic_find(dic, key, 6))	
	{
	  printf("key = %s, key_bytenum = %d, value[0] = %d, value[1] = %d\n", key,7,*((int*) dic->p_findvalue), *(((int*)dic->p_findvalue)+1));
	}
	else
	{
	  printf("key = %s\n",key);
	}
      }
//      dic_forEach(dic);
      dic_delete(dic);
    }

    return 1;

}
