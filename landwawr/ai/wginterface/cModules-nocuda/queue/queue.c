#include "queue.h"

struct Queue * queue_init(int mem_len)
{
  struct Queue *p_queue  = (struct Queue *) calloc (sizeof(struct Queue), 1);
  assert (p_queue != NULL);
  
  p_queue->mem_len = mem_len > 0 ? mem_len : INITMAX;
  p_queue->data = (ELEMENT_TYPE *) calloc (sizeof (ELEMENT_TYPE), p_queue->mem_len); // 在主调函数中释放
  assert(p_queue->data != NULL);

  p_queue->front = 0;
  p_queue->count = 0;
  p_queue->tail = p_queue->front + p_queue->count; // 无有效数据时候，tail == front  
  
  return p_queue;
}

void queue_delete(struct Queue *p_queue)
{
  free(p_queue->data);
  p_queue->data = NULL;
  free(p_queue);
  p_queue = NULL;
  return;
}

void queue_push(struct Queue *p_queue, const ELEMENT_TYPE* p_newone)
{
  if (p_queue->tail /(double)(p_queue->mem_len) >= INCRE_THRESHOLD)
  {
    if (p_queue->count / (double)(p_queue->mem_len) >= INCRE_THRESHOLD)
    {
      //申请新内存
      ELEMENT_TYPE *p_olddata = p_queue->data;
      p_queue->mem_len *= INCRE_FACTOR;
      //重置数据段
      p_queue->data = (ELEMENT_TYPE *) calloc (sizeof(ELEMENT_TYPE) , p_queue->mem_len);
      memcpy(p_queue->data, p_olddata + p_queue->front, sizeof(ELEMENT_TYPE) * p_queue->count);
      p_queue->front = 0;
      p_queue->tail = p_queue->count + p_queue->front ;
      free(p_olddata);
    } 
    else
    {
      //重置数据段
      memcpy(p_queue->data, p_queue->data + p_queue->front, sizeof (ELEMENT_TYPE) * p_queue->count);
      p_queue->front = 0;
      p_queue->tail = p_queue->count + p_queue->front ;
    }
  }
  // 添加新元素
  // printf("new ele = %d\n", *p_newone);

  memcpy(p_queue->data + p_queue->tail, p_newone, sizeof(ELEMENT_TYPE) * 1);
  p_queue->tail += 1;
  p_queue->count += 1; 
  return;
}

int queue_pop (struct Queue *p_queue, ELEMENT_TYPE *p_firstone)
{
  if ( p_firstone == NULL || p_queue->count == 0 )
    return 0;
  else
  {
    memcpy(p_firstone, p_queue->data + p_queue->front, sizeof(ELEMENT_TYPE) * 1);
    p_queue->front += 1;
    p_queue->count -= 1;
    return 1;
  }
}
