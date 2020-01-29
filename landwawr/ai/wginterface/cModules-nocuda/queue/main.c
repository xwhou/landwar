
/*
 *  测试queue数据结构
 */

#include <stdio.h>
#include "queue.h"

int main()
{
while(1){
  struct Queue *p_queue = queue_init(0);
  int i = 0;
  for (i = 0 ; i < 10; i ++)
  {
    queue_push(p_queue, &i);
    printf("i = %d, front = %d, tail = %d, count = %d, mem_len = %d\n",i, p_queue->front, p_queue->tail, p_queue->count, p_queue->mem_len);
  }

  for (i = 0 ; i < 5; i ++)
  {
    int tmp_firstone = 1;
    if (queue_pop(p_queue, &tmp_firstone))
      printf("%d,", tmp_firstone);
    else
     printf("\nerror\n");
    printf("i = %d, front = %d, tail = %d, count = %d, mem_len = %d\n",i, p_queue->front, p_queue->tail, p_queue->count, p_queue->mem_len);
  }
  printf("done!\n");
  printf("-----------------\n");
  for (i = 0 ; i < 12; i ++)
  {
    queue_push(p_queue, &i);
    printf("i = %d, front = %d, tail = %d, count = %d, mem_len = %d\n",i, p_queue->front, p_queue->tail, p_queue->count, p_queue->mem_len);
  }

  while(p_queue->count > 0)
  {
    
    int tmp_firstone = 1;
    if (queue_pop(p_queue, &tmp_firstone))
      printf("%d,", tmp_firstone);
    else
      printf("\nerror\n");
    printf(" front = %d, tail = %d, count = %d, mem_len = %d\n", p_queue->front, p_queue->tail, p_queue->count, p_queue->mem_len);
  }

 queue_delete(p_queue);
 }
 return 0;
}
