#include "hashdict.h"

#define hash_func meiyan


static inline uint32_t meiyan(const char *key, int count) {
	typedef uint32_t* P;
	uint32_t h = 0x811c9dc5;
	while (count >= 8) {
		h = (h ^ ((((*(P)key) << 5) | ((*(P)key) >> 27)) ^ *(P)(key + 4))) * 0xad3e7;
		count -= 8;
		key += 8;
	}
	#define tmp h = (h ^ *(uint16_t*)key) * 0xad3e7; key += 2;
	if (count & 4) { tmp tmp }
	if (count & 2) { tmp }
	if (count & 1) { h = (h ^ *key) * 0xad3e7; }
	#undef tmp
	return h ^ (h >> 16);
}

struct keynode *keynode_new( const char*key, const int key_bytenum, const int value_bytenum) 
{
  struct keynode *node = malloc(sizeof(struct keynode));
  node->key_bytenum = key_bytenum;
  node->key = (char*)malloc(node->key_bytenum);
  memcpy(node->key, key, key_bytenum);
  node->next = NULL;
  node->value = (char*) calloc(1,value_bytenum);
  return node;
}

void keynode_delete(struct keynode *node) {
  free(node->key);
  node->key = NULL;
  free(node->value);
  node->value = NULL;
  if (node->next) keynode_delete(node->next);
  free(node);
}

struct dictionary* dic_new(const int initial_size, const int value_bytenum) 
{
  struct dictionary* dic = malloc(sizeof(struct dictionary));
  dic->length = initial_size > 0 ? initial_size : INIT_DICMAX;
  dic->count = 0;
  dic->table = calloc( dic->length, sizeof(struct keynode*));
  dic->value_bytenum = value_bytenum;
  dic->p_findvalue = NULL;
  assert (dic->table != NULL);
 return dic;
}

void dic_delete(struct dictionary* dic) 
{
  assert (dic != NULL);
  for (int i = 0; i < dic->length; i++)
  {
    if (dic->table[i])
      keynode_delete(dic->table[i]); // keynode结构体有自己的释放内存的方法
  }
  free(dic->table);
  dic->table = NULL;
  free(dic);
}

void dic_reinsert_when_resizing(struct dictionary* dic, struct keynode *k2) {
	int n = hash_func(k2->key, k2->key_bytenum) % dic->length;
	if (dic->table[n] == 0) {
		dic->table[n] = k2;
//		dic->value = &dic->table[n]->value;
		return;
	}
	struct keynode *k = dic->table[n];
	k2->next = k;
	dic->table[n] = k2;
//	dic->value = &k2->value;
}

void dic_resize(struct dictionary* dic, int newsize) {
  int o = dic->length;
  struct keynode **old = dic->table;
  dic->table = calloc(sizeof(struct keynode*), newsize);
  dic->length = newsize;
  for ( int i = 0; i < o; i++) {
    struct keynode *k = old[i];
    while (k) {
      struct keynode *next = k->next;
      k->next = 0;
      dic_reinsert_when_resizing(dic, k);
      k = next;
    }
  }
  free(old);
}

int dic_add(struct dictionary* dic, void *key,void* p_value, const int key_bytenum, const int value_bytenum) 
{
  assert(value_bytenum == dic->value_bytenum);
  int n = hash_func((const char*)key, key_bytenum) % dic->length;
//  printf ("n = %d\n",n);
  if (dic->table[n] == 0) {
    float f = dic->count / (float)dic->length;
 //   printf("count = %d, lenth = %d, f = %f\n", dic->count, dic->length, f);
    if (f > INCRE_DICTTHRESHOLD) {
      dic_resize(dic, dic->length * INCRE_DICTFACTOR);
      return dic_add(dic, key, p_value, key_bytenum, value_bytenum);
    }
    dic->table[n] = keynode_new((char*)key, key_bytenum,value_bytenum);
    memcpy(dic->table[n]->value, (char*) p_value, value_bytenum);
    dic->count++;
    return 0;
  }
  struct keynode *k = dic->table[n];
  while (k)
  {
    if (k->key_bytenum== key_bytenum && memcmp(k->key, (char*)key, k->key_bytenum) == 0) 
    {
      memcpy(k->value, (char*) p_value, value_bytenum);
      return 1;
    }
    k = k->next;
  }
  dic->count++;
  struct keynode *k2 = keynode_new((char*)key, key_bytenum, value_bytenum);
  k2->next = dic->table[n];
  dic->table[n] = k2;
  memcpy(k2->value, (char*) p_value, value_bytenum);
  return 0;
}

int dic_find(struct dictionary* dic, void *key, int key_bytenum) 
{
    int n = hash_func((const char*)key, key_bytenum) % dic->length;
    __builtin_prefetch(dic->table[n]);
    struct keynode *k = dic->table[n];
    if (!k) return 0;
    while (k) {
      if (k->key_bytenum == key_bytenum && !memcmp(k->key, key, key_bytenum)) 
      {
	dic->p_findvalue = k->value; // dic-value可用于保存找到的数据指针
	return 1;
      }
      k = k->next;
    }
    return 0;
}

/*
void dic_forEach(struct dictionary* dic) {
  for (int i = 0; i < dic->length; i++) {
    if (dic->table[i] != 0) {
      struct keynode *k = dic->table[i];
      while (k) {
	printf("%s: ",k->key);
	for(int i = 0 ; i < 6 ; i ++)
	    printf (" %d,", *((int*)k->value + i));
	printf("\n");
	k = k->next;
      }
    }
  }
}
*/

#undef hash_func
