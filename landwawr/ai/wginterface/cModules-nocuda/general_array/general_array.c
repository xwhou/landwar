#include "general_array.h"

struct GA * ga_init (const int ele_num, const int ele_len, const int attr_bytenum)
{

  assert( ele_num >= 0 && ele_len >= 1 && attr_bytenum >=1);
  struct GA *p_ga = (struct GA*)  calloc (sizeof(struct GA), 1);
  assert(p_ga != NULL);

  p_ga->count = ele_num;
  p_ga->attr_bytenum = attr_bytenum;
  p_ga->ele_len = ele_len;
  p_ga->ele_bytenum = p_ga->ele_len * p_ga->attr_bytenum;

  p_ga->capacity = p_ga->count > 0 ? (p_ga->count / INCRE_GATHRESHOLD) : INIT_GAMAX;
  p_ga->capacity_len = p_ga->capacity * p_ga->ele_len;
  
  p_ga->p_data = (char*)calloc( p_ga->attr_bytenum, p_ga->capacity_len);
  assert(p_ga->p_data != NULL);

  return p_ga;
}

void ga_delete(struct GA *p_ga)
{
  assert(p_ga != NULL && p_ga->p_data != NULL);
  free(p_ga->p_data);
  p_ga->p_data = NULL;
  free(p_ga);
  return;
}

void ga_incre(struct GA *p_ga)
{
  // assert(p_ga != NULL && p_ga->p_data != NULL);
  p_ga->capacity *= INCRE_GAFACTOR; // 一味增长，如何保证p_ga->capacity 不超int类型的最大值?
  p_ga->capacity_len *= INCRE_GAFACTOR;
  char* p_olddata = p_ga->p_data;
  p_ga->p_data = (char*)calloc(p_ga->attr_bytenum, p_ga->capacity_len);

  assert(p_ga->p_data != NULL);
  memcpy(p_ga->p_data, p_olddata, p_ga->count * p_ga->ele_bytenum);

  free(p_olddata);
  return;
}

void ga_appendele(struct GA *p_ga, void* p_ele, const int ele_len, const int attr_bytenum)
{
  assert(p_ele != NULL && p_ga->ele_bytenum == ele_len * attr_bytenum);
  float cur_ratio = p_ga->count / (float)(p_ga->capacity);  
  if ( cur_ratio >= INCRE_GATHRESHOLD)
    ga_incre(p_ga);
  memcpy(p_ga->p_data + p_ga->count * p_ga->ele_bytenum, (char*)p_ele, p_ga->ele_bytenum);
  p_ga->count ++;
  return;
}

void ga_setele(struct GA * p_ga , void* p_ele, const int ele_loc, const int ele_len, const int attr_bytenum )
{
  
  assert(p_ele != NULL && p_ga->ele_bytenum == ele_len * attr_bytenum);
  assert(ele_loc >=0 && ele_loc < p_ga->count);
  memcpy(p_ga->p_data + ele_loc * p_ga->ele_bytenum, (char*)p_ele, p_ga->ele_bytenum);
  return;
}
void *ga_getele(const struct GA* p_ga, const int ele_loc)
{
  return (p_ga->p_data + ele_loc * p_ga->ele_bytenum);
}

void* ga_getattr(const struct GA *p_ga, const int ele_loc, const int attr_loc) 
{
  return (p_ga->p_data + ele_loc * p_ga->ele_bytenum  + attr_loc * p_ga->attr_bytenum);
}


