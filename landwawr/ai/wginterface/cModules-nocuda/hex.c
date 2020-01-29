
#include "hex.h"






//全局变量 ：偏移坐标下6个相邻方向在0(col)/1(row)的偏移，当列为奇数时候，选择dir_offset_ji, 否则，选择dir_offset_ou
int dir_offset_ji[12] = {1,0, 1,-1, 0,-1,-1,0,0,1,1,1};
int dir_offset_ou[12] = {1,0, 0,-1,-1,-1,-1,0,-1,1,0,1};
// 全局变量： 立方坐标下6个方向上的偏移坐标的位置差，高维标识每个方向，低维标识q r s 方向上的偏移量
int g_diroffset_cube[6][3]={  {1, 0, -1}, {1, -1, 0},
			      {0, -1, 1}, {-1, 0, 1},
			      {-1, 1, 0}, {0, 1, -1}};


// 全局变量，相邻两个六角格的对应方向转换
int g_dir_map[DIRECTION_NUM] = {3, 4, 5, 0, 1, 2};

void cvtHexFromCubeToOffset(const struct HexOfCude * p_hex_c, struct HexOfOffset * p_hex_o)
{
  p_hex_o->col = p_hex_c->q + (p_hex_c->r - (p_hex_c->r & 1)) / 2 ;
  p_hex_o->row = p_hex_c->r;
}

void cvtHexFromOffsetToCube(const struct HexOfOffset * p_hex_o, struct HexOfCude * p_hex_c)
{
  p_hex_c->q = p_hex_o->col - (p_hex_o->row - (p_hex_o->row & 1 )) / 2 ;
  p_hex_c->r = p_hex_o->row ;
  p_hex_c->s = 0 - p_hex_c->q - p_hex_c->r ;

}

int getDistanceBetweenHexOfCube(const struct HexOfCude *p_c_hexa, const struct HexOfCude * p_c_hexb)
{
  return (abs(p_c_hexb->q - p_c_hexa->q) + abs(p_c_hexb->r - p_c_hexa->r) + abs(p_c_hexb->s - p_c_hexa->s))/2;
}


int getDistanceBetweenHexOfOffset_com(const struct HexOfOffset *p_o_hexa , const struct HexOfOffset *p_o_hexb)
{
  struct HexOfCude hexa_c = {0,0,0};
  struct HexOfCude hexb_c = {0,0,0};
  cvtHexFromOffsetToCube(p_o_hexa, &hexa_c);
  cvtHexFromOffsetToCube(p_o_hexb, &hexb_c);
  return  getDistanceBetweenHexOfCube(&hexa_c, &hexb_c);
}

void getCubeLerp( const struct HexOfCude * p_c_hexa, const struct HexOfCude *p_c_hexb, const double  t, struct HexOfCudeInFraction * p_f_hex)
{
  assert(p_c_hexa != NULL && p_c_hexb != NULL  && p_f_hex != NULL);
  p_f_hex->dq = p_c_hexa->q + (p_c_hexb->q - p_c_hexa->q) * t;
  p_f_hex->dr = p_c_hexa->r + (p_c_hexb->r - p_c_hexa->r) * t;
  p_f_hex->ds = p_c_hexa->s + (p_c_hexb->s - p_c_hexa->s) * t;
}

void cubeRound (const struct HexOfCudeInFraction * p_f_hex, struct HexOfCude *p_c_hex)
{

  int rq = round(p_f_hex->dq);
  int rr = round(p_f_hex->dr);
  int rs = round(p_f_hex->ds);
  double  diff_q = abs(rq - p_f_hex->dq);
  double  diff_r = abs(rr - p_f_hex->dr);
  double  diff_s = abs(rs - p_f_hex->ds);
  if(diff_q > diff_r && diff_q > diff_s)
    rq = -rr-rs;
  else if (diff_r > diff_s)
    rr = -rq-rs;
  else
    rs = -rq-rr;
  p_c_hex->q = rq;
  p_c_hex->r = rr;
  p_c_hex->s = rs;
}

void getHexsOnLineOfOffset(const struct HexOfOffset *p_o_hexa, const struct HexOfOffset * p_o_hexb, struct GA *p_gahexsoffset)
{
  struct HexOfCude tmp_c_hexa = {0,0,0};
  struct HexOfCude tmp_c_hexb = {0,0,0};
  cvtHexFromOffsetToCube(p_o_hexa, &tmp_c_hexa);
  cvtHexFromOffsetToCube(p_o_hexb, &tmp_c_hexb);

  struct GA *p_gahexscube = ga_init(0,1,sizeof(struct HexOfCude)); // ele_num ele_len attr_bytenum
  getHexsOnLineOfCube(&tmp_c_hexa, &tmp_c_hexb, p_gahexscube);

  struct HexOfOffset tmp_hexoffset={0,0};
  for(int i = 0 ; i <p_gahexscube->count; i++)
  {
    cvtHexFromCubeToOffset((struct HexOfCude*)ga_getele(p_gahexscube, i), &tmp_hexoffset);
    ga_appendele(p_gahexsoffset, &tmp_hexoffset, 1, sizeof( struct HexOfOffset));
  }
  
  ga_delete(p_gahexscube);
  return;
}


void getHexsOnLineOfCube(const struct HexOfCude * p_c_hexa, const struct HexOfCude * p_c_hexb, struct GA* p_gahexscube)
{
  int dis = getDistanceBetweenHexOfCube(p_c_hexa, p_c_hexb);
  double step = 1.0 / (dis > 1 ? dis : 1);
  struct HexOfCudeInFraction tmp_fraction_hexcube = {0.0, 0.0 ,0.0};
  struct HexOfCude tmp_hexcube = {0,0,0};
  for (int i = 0 ; i < dis+1; i++)
  {
    getCubeLerp(p_c_hexa, p_c_hexb, step * i , &tmp_fraction_hexcube);
    cubeRound (&tmp_fraction_hexcube, &tmp_hexcube);
    ga_appendele(p_gahexscube, &tmp_hexcube, 1, sizeof(struct HexOfCude));
  }
}

void getNeighborHexsOfOffset(const struct HexOfOffset *p_hex_o, struct GA *p_gahexsoffset)
{
  int * p_dirs_offset =  p_hex_o->row % 2 == 0 ?  dir_offset_ou : dir_offset_ji;
  struct HexOfOffset tmp_hexoffset = {0,0};
  for (int i = 0 ; i < DIRECTION_NUM; i ++)
  {
    tmp_hexoffset.row = p_hex_o->row + *(p_dirs_offset + 2 * i + 1);
    tmp_hexoffset.col = p_hex_o->col + *(p_dirs_offset + 2 * i );
    ga_appendele(p_gahexsoffset, &tmp_hexoffset, 1, sizeof(struct HexOfOffset));
  }
}


void getHexInSpecifiedDirAndStepOfCube(const struct HexOfCude *p_hex_c, const int dir, const int step,struct HexOfCude *p_rhex_c)
{
  assert(dir < DIRECTION_NUM && dir >= 0);
  p_rhex_c->q = p_hex_c->q + g_diroffset_cube[dir][0] * step;
  p_rhex_c->r = p_hex_c->r + g_diroffset_cube[dir][1] * step;
  p_rhex_c->s = p_hex_c->s + g_diroffset_cube[dir][2] * step;
}

void getHexsOnRingOfOffset(const struct HexOfOffset *p_centorhex_o, const int radius, struct GA *p_gahexsoffset)
{
  if (radius == 0)
  { 
    struct HexOfOffset tmp_hexoffset = *p_centorhex_o;
    ga_appendele(p_gahexsoffset,&tmp_hexoffset, 1, sizeof(struct HexOfOffset));
  }
  else
  {
    const int init_ring_dir = 4;
    struct HexOfCude centorhex_c, ring_starthex_c ;
    cvtHexFromOffsetToCube(p_centorhex_o, &centorhex_c);
    getHexInSpecifiedDirAndStepOfCube(&centorhex_c, init_ring_dir, radius, &ring_starthex_c);
    struct HexOfOffset eachedge_hex_o = {0,0};
    for (int j_dirs = 0 ; j_dirs < DIRECTION_NUM ; j_dirs ++) // 环上的方向遍历, （j_dirs初始==0 与 init_ring_dir有直接关系）
      for (int k_radius = 0 ; k_radius < radius; k_radius ++) // 每一个方向遍历 i_radius 个六角格
      {
	cvtHexFromCubeToOffset(&ring_starthex_c, &eachedge_hex_o);
	ga_appendele(p_gahexsoffset, &eachedge_hex_o, 1, sizeof(struct HexOfOffset));
	getHexInSpecifiedDirAndStepOfCube(&ring_starthex_c, j_dirs, 1, &ring_starthex_c);
      }
  }
}

void getHexsInCircleOfOffset(const struct HexOfOffset *p_centorhex_o, const int radius, struct GA * p_gahexsoffset)
{
  assert(radius >=0);
  for (int i_radius = 0; i_radius <= radius; i_radius++ ) // 环遍历
    getHexsOnRingOfOffset(p_centorhex_o, i_radius, p_gahexsoffset);
}

bool getDirOffVectorSet(const int dir, const int mindis, const int maxdis, struct GA * p_gaoffvecs)
{
  bool flag = dir <= 5 && dir >= 0 && mindis <= maxdis  && mindis >= 1 && p_gaoffvecs != NULL;
  if (!flag){
    printf("error in getDirOffVectorSet() in hex.c\n");
    return flag;
  }
  // printf("dir=%d, mindis=%d, maxdis=%d\n", dir, mindis, maxdis);
  // 归纳算法计算偏移向量
  const int sameloc = dir % 3;
  const int varyloc = (sameloc + 1) % 3;
  const int hastovaryloc = (sameloc + 2) % 3;
  const int increvalue = dir % 2 == 0 ? -1 : 1;
  const int *p_base_cur =  g_diroffset_cube[dir];
  int p_tmp_vector[3] ={0};
  int p_tmp_base[3] ={0};
  for (int dis_index = mindis; dis_index < maxdis ; dis_index ++){
    for (int i = 0 ; i < 3; i ++) p_tmp_base[i] = p_base_cur[i] * dis_index;
    ga_appendele(p_gaoffvecs, p_tmp_base, 3 , sizeof(int));
    for (int j = 1; j < dis_index; j++){
      p_tmp_vector[sameloc] = p_tmp_base[sameloc];
      p_tmp_vector[varyloc] = p_tmp_base[varyloc] + increvalue * j;
      p_tmp_vector[hastovaryloc] = 0 - p_tmp_vector[sameloc] - p_tmp_vector[varyloc];
      ga_appendele(p_gaoffvecs,p_tmp_vector, 3 , sizeof(int));
      // printf("[%d,%d,%d]\n", p_tmp_vector[0], p_tmp_vector[1], p_tmp_vector[2]);
    }
  }
  return flag;
}

