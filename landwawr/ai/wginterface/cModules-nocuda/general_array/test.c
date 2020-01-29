#include "general_array.h"
#include <stdio.h>
struct S
{
  int a;
  double b;
  int c;
};

#define int_bytenum sizeof(int)
#define float_bytenum sizeof(float)
#define S_bytenum sizeof(struct S)


void main()
{
  int k = 1;
  struct GA *p_ga = ga_init(10, 1, S_bytenum); // 初始化设定1个元素，每个元素1个属性，每个属性S_bytenum个字节
  while(k--)
  {
    struct S tmp_s = {-1,-2,-4};
    ga_setele(p_ga, &tmp_s, 0, 1, S_bytenum);
    for (int i = 0 ; i < 10; i ++)
    {
      struct S tmp_s={i*3+0,i*3+1,i*3+2};
      ga_appendele(p_ga, &tmp_s, 1, S_bytenum);
      printf("i = %d,count = %d, attr_bytenum = %d, ele_len = %d, capacity = %d, capacity_len = %d\n", i, p_ga->count,p_ga->attr_bytenum, p_ga->ele_len, p_ga->capacity, p_ga->capacity_len);
    }
    
    for(int i = 0 ;  i< p_ga->count ; i++)
    {
      printf("i = %d,", i);
      printf("S_a = %d , S_b = %f , S_c = %d ", ((struct S*)ga_getele(p_ga,i))->a, ((struct S*)ga_getele(p_ga,i))->b, ((struct S*)ga_getele(p_ga,i))->c);
      printf("\n");
      printf("i = %d,count = %d, ele_len = %d, capacity = %d, capacity_len = %d\n", i, p_ga->count, p_ga->ele_len, p_ga->capacity, p_ga->capacity_len);
    }
    
  }
  ga_delete(p_ga); 
  return;
}
