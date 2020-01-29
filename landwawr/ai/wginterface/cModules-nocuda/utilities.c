#include "utilities.h"

bool g_flag_graphicmem_ok = false;
void warpInitMapAttr(const void *py_p_geodata, const void * py_p_epdata, const void* py_p_roadnet, const void *py_p_wptable, const int py_georows, const int py_geocols, const int py_eprows, const int py_epcols, const int py_rdnetrows, const int py_rdnetcols, const int py_wprows, const int py_wpcols)
{
  assert( py_p_geodata != NULL && py_p_epdata != NULL && py_p_roadnet != NULL);
  initMapAttr((int*)py_p_geodata, (int *)py_p_epdata, (int*) py_p_roadnet, (int*) py_p_wptable, py_georows, py_geocols, py_eprows, py_epcols, py_rdnetrows, py_rdnetcols, py_wprows, py_wpcols);
  return ;
}

void warpInitDamageTable(const void * py_p_damagetable_zm2car, const void * py_p_damagetable_ltf2car, const void * py_p_damagetable_allw2people)
{
  assert(py_p_damagetable_zm2car != NULL && py_p_damagetable_ltf2car != NULL && py_p_damagetable_allw2people != NULL);
  const float *p_damagetable_zm2car = (float* )py_p_damagetable_zm2car;
  const float *p_damagetable_ltf2car = (float*)py_p_damagetable_ltf2car;
  const float *p_damagetable_allw2people = (float*) py_p_damagetable_allw2people;
  memcpy(g_p_damagelevel_zm2car, p_damagetable_zm2car, sizeof(float) * DAMAGELEVEL_DIM_ZM2CAR_HEIGHT * DAMAGELEVEL_DIM_TABLE_SIZE);
  memcpy(g_p_damagelevel_ltf2car, p_damagetable_ltf2car, sizeof(float) * DAMAGELEVEL_DIM_LTF2CAR_HEIGHT * DAMAGELEVEL_DIM_TABLE_SIZE);
  memcpy(g_p_damagelevel_allw2people, p_damagetable_allw2people, sizeof(float) * DAMAGELEVEL_DIM_ALLW2PEOPLE_HEIGHT * DAMAGELEVEL_DIM_TABLE_SIZE);
  return; 
}

void warpInitCacheData(const void * py_p_1d_icutable, const int len_icu, const void * py_p_1d_wicgtable, const int len_wicg, const void * py_p_1d_distable , const int len_dis )
{
  assert(py_p_1d_icutable != NULL);
  assert(py_p_1d_wicgtable != NULL);
  assert(py_p_1d_distable != NULL);
  initIcuCacheData((int*)py_p_1d_icutable, len_icu);
  initWicgCacheData((long long*)py_p_1d_wicgtable, len_wicg);
  intiDisCacheData((long long*) py_p_1d_distable, len_dis);
  return;
}


void warpFreeMapAttr()
{
  freeMapAttr();
  // if (g_flag_graphicmem_ok) 
  //   feature_free();
  return;
}

void warpTestMapAttr()
{
  puts("-----------------\n");
  puts("检查字典\n");
  srand(time(0));
  int k = 10;
  char chars_loc[5]={'\0'};
  while ( k -- )
  {
    int tmp_row = rand() % MAP_YNUM;
    int tmp_col = rand() % MAP_XNUM;
    int tmp_int_loc = tmp_row * 100 + tmp_col;
    cvtIntLocTo4StrOffLoc(tmp_int_loc, chars_loc, 5);
    if (dic_find(g_mapattr.dic_loc2geodata, chars_loc, 5)) // 找到返回1.否则返回0
    {
      printf("%s\t", chars_loc);
      for (int i = 0 ; i < 4 ; i ++)
	printf("%d\t", ((int*)(g_mapattr.dic_loc2geodata->p_findvalue))[i]);
      printf("\n");
    }
    if (dic_find(g_mapattr.dic_loc2epdata, chars_loc, 5)) // 找到返回1.否则返回0
    {
      printf("%s\t", chars_loc);
      for (int i = 0 ; i < 6 ; i ++)
	printf("%d\t", ((int*)(g_mapattr.dic_loc2epdata->p_findvalue))[i]);
      printf("\n");
    }
 }
  return;
}

void warpTestWeaponData(const struct BasicOperator *py_p_bopa)
{
  setlocale(LC_ALL, "");
  const int num_wps = py_p_bopa->obj_wznum;
  // printf("%ls\t %d\n",py_p_bopa->obj_name, num_wps);

  for (int i = 0 ; i < num_wps; i++){
    printf("------------\n");
    const int wpid = py_p_bopa->p_obj_wpids[i];
    const int wp_objtype = getWPObjtype(g_mapattr.dic_wpid2attrs,  wpid);
    printf("武器编号[%d], 类型：[%d]\n", py_p_bopa->p_obj_wpids[i], getWPObjtype(g_mapattr.dic_wpid2attrs,  wpid));
    if (wp_objtype == 0){
      const int wp_aimrange_peo = getWPAimrange(g_mapattr.dic_wpid2attrs, wpid, 1);
      const int wp_aimrange_car = getWPAimrange(g_mapattr.dic_wpid2attrs, wpid, 2);
      printf("对人射程[%d]. 对车射程[%d]\n", wp_aimrange_peo, wp_aimrange_car);
      const int *p_dldata_peo = getDLStartDataPointer(g_mapattr.dic_wpid2attrs,py_p_bopa->obj_blood, wpid, 1);
      printf("对人的攻击等级\n");
      const int blood = 5;
      for (int i = 0 ;  i <= wp_aimrange_peo; i++){
	printf("\t %d, ", p_dldata_peo[ (blood-1) * MAX_AIMRANGE + i]);
      }
      printf("\n");

      printf("对车的攻击等级\n");
      const int* p_dldata_car = getDLStartDataPointer(g_mapattr.dic_wpid2attrs, py_p_bopa->obj_blood, wpid, 2);
      for(int i = 0 ; i <= wp_aimrange_car; i++){
	printf("\t %d, ", p_dldata_car[i]);
      }
      printf("\n");

    }else{
      printf("wp_objtype = %d\n", wp_objtype);
      const int wp_aimrange = getWPAimrange(g_mapattr.dic_wpid2attrs, wpid, wp_objtype);
      printf("射程[%d]\n", wp_aimrange);
      printf("攻击等级\n");
   if(wp_objtype == 1){
	printf("对人的攻击等级\n");
	const int blood = 4;
	const int *p_dldata_peo = getDLStartDataPointer(g_mapattr.dic_wpid2attrs,py_p_bopa->obj_blood, wpid, 1);
	const int wp_aimrange_peo = getWPAimrange(g_mapattr.dic_wpid2attrs, wpid, 1);
	for (int i = 0 ;  i <= wp_aimrange_peo; i++){
	  printf("\t %d, ", p_dldata_peo[ (blood-1) * MAX_AIMRANGE + i]);
	}
	printf("\n");
      }else{
	printf("对车的攻击等级\n");
	const int* p_dldata_car = getDLStartDataPointer(g_mapattr.dic_wpid2attrs,py_p_bopa->obj_blood, wpid, 2);
	const int wp_aimrange_car = getWPAimrange(g_mapattr.dic_wpid2attrs, wpid, 2);
	for(int i = 0 ; i <= wp_aimrange_car; i++){
	  printf("\t %d, ", p_dldata_car[i]);
	}
	printf("\n");
      }
    }
  }
  return;
}

void warpGetMyIcuMap(const struct BasicOperator *py_p_bop, struct BasicTensor *py_p_bt)
{
  assert(py_p_bop != NULL);
  assert(py_p_bt->data != NULL && py_p_bt->p_shapes!= NULL);
  //  assert(py_p_bop->obj_posy == py_p_bop->obj_posx);
  char chars_6_loc[7];
  cvtIntLocTo4StrOffLoc(py_p_bop->obj_pos, chars_6_loc, 7);
  // printf("chars_6_loc = %s\n", chars_6_loc);
  int cur_row, cur_col ;
  cvtChars6locToOffsetIntLoc(chars_6_loc, &cur_row, &cur_col);
  struct HexOfOffset centor_hex = {cur_row, cur_col};
  // printf("cur_row = %d, cur_col = %d\n", cur_row, cur_col);
  
  // 初始化两张图像为0【不可视】
  const int map_col = MAP_XNUM;
  for (int i = MAP_YMIN; i < MAP_YMAX; i ++)
    for (int j = MAP_XMIN; j <MAP_XMAX; j++)
    {
      int cur_loc = i * map_col + j;
      py_p_bt->data[ cur_loc ] = -1 ;
    }

  struct dictionary *p_dic = dic_new(0,sizeof(int));
  icuRange(&centor_hex, MAXIOUDIS_CAR, p_dic); //先车

  for (int i = 0; i < p_dic->length; i++) {
  if (p_dic->table[i] != 0) {
    struct keynode *k = p_dic->table[i];
    while (k) {
      cur_row = atoi(k->key) / 100;
      cur_col = atoi(k->key) % 100;
      py_p_bt->data[ cur_row * map_col + cur_col] =  ((int*)k->value)[0];
     // printf("%f\n", py_p_bt->data[cur_row * map_col + cur_col]);
      k = k->next;
      }
    }
  }
  dic_delete(p_dic);
  return; 
}

void warpGetMyIouMap(const int flag_mode , const struct BasicOperator *py_p_bopa, const struct BasicOperator *py_p_bopb, struct BasicTensor *py_p_bt)
{
  assert (flag_mode >= 0 && flag_mode <= 2);
  iouRange(py_p_bopa, py_p_bopb, (float*)(py_p_bt->data));
  return;
}

void warpGetMyIouDynamicMap(const int flag_mode, const struct BasicOperator *py_p_bopa, const struct BasicOperator *py_p_bopb, struct BasicTensor *py_p_bt)
{
  assert (flag_mode >= 0 && flag_mode <= 2);
  iouRange(py_p_bopa, py_p_bopb, (float*)(py_p_bt->data));
  return;
}

void warpGetMyAttacklevelMap(const int flag_mode, const struct BasicOperator * py_bop_att, const struct BasicOperator * py_bop_obj, struct BasicTensor * py_p_bt)
{
  assert (flag_mode >= 0 && flag_mode <= 2);
  assert(py_bop_att->obj_wznum == py_p_bt->ndim);
  assert(py_bop_att->obj_blood > 0);
  for(int wp_index = 0 ; wp_index < py_bop_att->obj_wznum; wp_index++){
    float *p_atmap_data = ((float*)(py_p_bt->data)) + wp_index * MAP_YNUM * MAP_XNUM;
    if (flag_mode < 2){
      attacklevelMap(py_bop_att, py_bop_obj, wp_index,  p_atmap_data);
    } else if (flag_mode == 2) {
      if(!g_flag_graphicmem_ok){
	printf("error in warpGetMyAttacklevelMap(): g_flag_graphicmem_ok is false\n");
	return;
      }
    }
  }
  return;
}


void warpGetDamageP2P(const struct BasicOperator *py_p_bopa, const struct BasicOperator *py_p_bopb, void *p_damage)
{
    int maxindex = 0;
    float maxvalue = 0;
    if (py_p_bopa->a1 == 0){ // 无行射能力
      weaponSelectionForAttacker(py_p_bopa, py_p_bopb, &maxvalue, &maxindex );
    } else{ // 有行射能力
      struct dictionary *p_objdicwicg = dic_new(0,sizeof(int));
      whereICanGoRange(py_p_bopa, p_objdicwicg);
      struct GA* p_objgadamagelist_o = ga_init(0, py_p_bopa->obj_wznum + 3, sizeof(float));
      listdamages(py_p_bopa, py_p_bopb,  p_objdicwicg, p_objgadamagelist_o);
      if(p_objgadamagelist_o->count > 0){
	float p_optele[5] = {0};
	optShootingCond(p_objgadamagelist_o, 5, p_optele);
	maxvalue = p_optele[4];
      }
      ga_delete(p_objgadamagelist_o);
      dic_delete(p_objdicwicg);
    }
    //((float *)p_damage)[0] = maxvalue * py_p_bopb->obj_value;
    ((float *)p_damage)[0] = maxvalue > 0 ? maxvalue : 0;
    return ;
}

void warpGetDirectDamageP2P(const struct BasicOperator *py_p_bopa, const struct BasicOperator *py_p_bopb, void *p_damage)
{
    int maxindex = 0;
    float maxvalue = 0;
    weaponSelectionForAttacker(py_p_bopa, py_p_bopb, &maxvalue, &maxindex );
    ((float *)p_damage)[0] = maxvalue > 0 ? maxvalue : 0;
    return ;
}



//  void warpGetMyDamageMap(const struct BasicOperator *py_p_bopa, const struct BasicOperator *py_p_bopb, void * p_damagemap)
//  { 
//    assert (py_p_bopa != NULL && py_p_bopb != NULL && p_damagemap!= NULL);
//    if (!g_flag_graphicmem_ok){
//      damageMapP2P(py_p_bopa, py_p_bopb,(float*)p_damagemap);
//    } else {
//      float * p_takeDamageMap = (float *) malloc (MAP_XNUM * MAP_YNUM * OPERATOR_MAX_BLOOD * sizeof(float));
//      // 攻击者所有
//      int *p_wcgAMap = (int*)malloc(sizeof(int)*MAP_YNUM*MAP_XNUM);
//      int a_int4loc = cvtInt6loc2Int4loc(py_p_bopa->obj_pos);
//      calWcgMapC(a_int4loc,py_p_bopa->obj_step,py_p_bopa->obj_type,p_wcgAMap);
//      // 目标者所有
//      int *p_wcgBMap = (int*) malloc( sizeof(int) * MAP_YNUM * MAP_XNUM); //计算机动范围图
//      int b_int4loc = cvtInt6loc2Int4loc(py_p_bopb->obj_pos);
//      calWcgMapC(b_int4loc, py_p_bopb->obj_step,py_p_bopb->obj_type, p_wcgBMap);

//      //计算战损图(全血量) 目标者作为参数1， 攻击者作为参数2
//      // printf ("a blood = %d, b blood = %d",py_p_bopa->obj_blood,py_p_bopb->obj_blood );
//      assert (py_p_bopb->obj_blood > 0 && py_p_bopa->obj_blood > 0);
//      calTakeDamageMapC(py_p_bopb, py_p_bopa, (int*)p_wcgBMap, (int*)p_wcgAMap, p_takeDamageMap);
//      free(p_wcgAMap);
//      free(p_wcgBMap);
//      memcpy((float*)p_damagemap, p_takeDamageMap + (py_p_bopa->obj_blood-1) * MAP_XNUM * MAP_YNUM , sizeof(float) * MAP_YNUM * MAP_XNUM);
//      free(p_takeDamageMap);
//    }
//    return;
// }
//
void warpGetMyDamageMap(const struct BasicOperator *py_p_bopa, const struct BasicOperator *py_p_bopb, void * p_damagemap)
{ 
  assert (py_p_bopa != NULL && py_p_bopb != NULL && p_damagemap!= NULL);
  damageMapP2P(py_p_bopa, py_p_bopb,(float*)p_damagemap);
  /*
  if (!g_flag_graphicmem_ok){
    damageMapP2P(py_p_bopa, py_p_bopb,(float*)p_damagemap);
  } else {
    
    // 攻击者所有
    int *p_wcgAMap = (int*)malloc(sizeof(int)*MAP_YNUM*MAP_XNUM);
    int a_int4loc = cvtInt6loc2Int4loc(py_p_bopa->obj_pos);
    calWcgMapC(a_int4loc,py_p_bopa->obj_step,py_p_bopa->obj_type,p_wcgAMap);
    // 目标者所有
    int *p_wcgBMap = (int*) malloc( sizeof(int) * MAP_YNUM * MAP_XNUM); //计算机动范围图
    int b_int4loc = cvtInt6loc2Int4loc(py_p_bopb->obj_pos);
    calWcgMapC(b_int4loc, py_p_bopb->obj_step,py_p_bopb->obj_type, p_wcgBMap);
 
    //计算战损图(全血量) 目标者作为参数1， 攻击者作为参数2
    // printf ("a blood = %d, b blood = %d",py_p_bopa->obj_blood,py_p_bopb->obj_blood );
    assert (py_p_bopb->obj_blood > 0 && py_p_bopa->obj_blood > 0);
    calTakeDamageMapC_oneblood(py_p_bopb, py_p_bopa, (int*)p_wcgBMap, (int*)p_wcgAMap, (float*)p_damagemap);
    free(p_wcgAMap);
    free(p_wcgBMap);
  }
  */
  return;
}
void warpGetAllDamageMap(const int flag_mode, const struct BasicOperator *py_p_bopa, const struct BasicOperator *py_p_bopb, struct BasicTensor * py_p_bt)
{
  assert (py_p_bt->ndim == py_p_bopa->obj_wznum);
  assert (flag_mode >= 0 && flag_mode < 3);
  for (int wp_index = 0 ; wp_index < py_p_bopa->obj_wznum; wp_index ++){
    float * p_damagemap = py_p_bt->data + wp_index * MAP_YNUM * MAP_XNUM;
    if (flag_mode < 2){
      separateDamageMap(py_p_bopa, py_p_bopb, wp_index, p_damagemap);
    } else if (flag_mode == 2){
      if(!g_flag_graphicmem_ok){
	printf("error in warpGetAllDamageMap(): g_flag_graphicmem_ok is false\n");
	return;
      }
      
    }
  }
  return;
}

void warpGetMyWhereICanGoMap(const struct BasicOperator *py_p_bop, struct BasicTensor *py_p_bt)
{
  
  char chars_6_loc[7];
  cvtIntLocTo4StrOffLoc(py_p_bop->obj_pos, chars_6_loc, 7);
  // printf("chars_6_loc = %s\n", chars_6_loc);
  const int map_col = MAP_XNUM;
  for (int i = MAP_YMIN; i < MAP_YMAX; i ++)
    for (int j = MAP_XMIN; j <MAP_XMAX; j++)
    {
      int cur_loc = i * map_col + j;
      py_p_bt->data[ cur_loc ] = -1 ;
    }
  struct GA *p_gawicg = ga_init(0, 3, sizeof(int));
  whereICanGoRangeGA(py_p_bop, p_gawicg);
  // printf("wicg count  %d \n", p_gawicg->count);
  for(int i = 0 ; i < p_gawicg->count ; i ++)
  {
    int *p_ele = (int*) ga_getele(p_gawicg,i);
    py_p_bt->data[ p_ele[0] * map_col + p_ele[1]] = (float)(p_ele[2]);
  }
  ga_delete(p_gawicg);
  return;
}


void warpGetMyICanPassMap(const struct BasicOperator *py_p_bop, struct BasicTensor *py_p_bt)
{
  const int map_col = MAP_XMAX;
  const int int4loc =  cvtInt6loc2Int4loc(py_p_bop->obj_pos);
  printf("当前算子的坐标位置:%d\n", int4loc);
  // 初始化为-1
  for (int i = MAP_YMIN; i < MAP_YMAX; i ++)
    for (int j = MAP_XMIN; j <MAP_XMAX; j++)
    {
      int cur_loc = i * map_col + j;
      py_p_bt->data[ cur_loc ] = -1 ;
    }

  struct GA *p_gawicp = ga_init(0, 3, sizeof(int));
  whereICanPassRangeGA(py_p_bop, p_gawicp);
  printf("机动范围内的道路六角格数量:%d \n", p_gawicp->count);

  for(int i = 0 ; i < p_gawicp->count ; i ++)
  {
    int *p_ele = (int*) ga_getele(p_gawicp,i);
    py_p_bt->data[ p_ele[0] * map_col + p_ele[1]] = (float)(p_ele[2]);
  }

  ga_delete(p_gawicp);
  return;
}

void warpGetDirRegionMap(const struct BasicOperator *py_p_bop, const int dir, const int mindis, const int maxdis, struct BasicTensor *py_p_bt)
{
  // 参数检查
  bool flag = py_p_bop != NULL && py_p_bt != NULL && dir >= 0 && dir <= 5;
  flag = flag && mindis >= 1 && mindis <= maxdis ;
  if (!flag){
    printf("error in warpGetDirRegionMap: flag is False\n");
    return ;

  }
  // 调用getCandidateScoutlocs()计算候选侦察点集合
  struct GA * p_gahexs = ga_init(0, 3, sizeof(int));
  getCandidateScoutlocs(py_p_bop, dir, mindis, maxdis, p_gahexs);
  // 将结果拷贝到py_p_bt中
  for (int i = 0; i < MAP_XNUM * MAP_YNUM; i++) py_p_bt->data[i] = -1 ;
  for (int i = 0 ; i < p_gahexs->count; i++){
    int  *p_tmp_array = (int *)ga_getele(p_gahexs, i); 
    py_p_bt->data[p_tmp_array[0] * MAP_XNUM + p_tmp_array[1]] = p_tmp_array[2];
  }
 
  // 资源释放
  ga_delete(p_gahexs);
  return;
}



void warpGetMyIcuFlag(const int cen_row, const int cen_col, const int cur_row, const int cur_col, const int maxdis, void * py_p_int_flag)
{
  const struct HexOfOffset cen_hex = {cen_row, cen_col};
  const struct HexOfOffset cur_hex = {cur_row, cur_col};
  assert (checkHexIsValid(&cen_hex) && checkHexIsValid(&cur_hex));
  *((int*)py_p_int_flag)= icuIsOk(&cen_hex, &cur_hex, maxdis) ? 1 : 0;
  return ;
}
/*
void warpGetMinPowConsume(const struct BasicOperator *py_p_bop, const int int6loc_b, void *py_p_int_powcon)
{
  assert(py_p_int_powcon != NULL);
  int int4loc_a = cvtInt6loc2Int4loc(py_p_bop->obj_pos);
  int int4loc_b = cvtInt6loc2Int4loc(int6loc_b);
  const struct HexOfOffset hex_a = {int4loc_a/100, int4loc_a%100};
  const struct HexOfOffset hex_b = {int4loc_b/100, int4loc_b%100};
  assert(checkHexIsValid(&hex_a) && checkHexIsValid(&hex_b));
  const int dis = getDistanceBetweenHexOfOffset(&hex_a, &hex_b);
  int retuevalue = dis;
  bool flag_cal = true;
  if (py_p_bop->obj_type == 2){ // for car
     if (g_mapattr.dic_pairlocs2pow != NULL && py_p_bop->obj_step <= 8){
        char chars_4pairlocs[9]={'\0'};
        int key = int4loc_a * 10000 + int4loc_b;
        assert(cvtIntLocTo4StrOffLoc(key, chars_4pairlocs, 9));
        if (dic_find(g_mapattr.dic_pairlocs2pow, chars_4pairlocs,9)){
          retuevalue = ((int*)g_mapattr.dic_pairlocs2pow->p_findvalue)[0];
          flag_cal = false;
        }
     }
  } else { // for peo
    flag_cal = false
  }
  // calculate min power-consumed value from loc_a to loc_bs
  if (flag_cal){
    bool flag_find = false;
    struct BasicOperator bopcopy = *py_p_bop;
    const int ori_stepvalue = 10000;
    bopcopy.obj_step = ori_stepvalue;
    struct GA *p_gawicg = ga_init(0, 3, sizeof(int));
    whereICanGoRangeGA_com(&bopcopy, p_gawicg);
    for (int i = 0 ; i < p_gawicg->count; i ++ ){
      int *p_ele = (int*) ga_getele(p_gawicg,i);
      if (p_ele[0] == hex_b.row && p_ele[1] == hex_b.col){
        retuevalue = ori_stepvalue - p_ele[2];
        flag_find = true;
        break;
      }
    }
    assert (flag_find);
    ga_delete(p_gawicg);
  }

  ((int*)py_p_int_powcon)[0] = retuevalue;
  return;
}
*/

void warpIouIsOk(const struct BasicOperator *py_p_bopa, const struct BasicOperator * py_p_bopb, void *py_p_int_flag)
{
  assert(py_p_int_flag != NULL);
  //printf("攻击算子：%d, 类型：%d\n", cvtInt6loc2Int4loc(py_p_bopa->obj_pos),py_p_bopa->obj_type);
  //printf("目标算子：%d, 类型：%d\n", cvtInt6loc2Int4loc(py_p_bopb->obj_pos),py_p_bopb->obj_type);
  //printf("进入iouIsOk()函数\n");
  *((int*)py_p_int_flag) =  iouIsOk(py_p_bopa, py_p_bopb) == false ? 0:1;
  return;
}

void warpGetNHideLoc(const struct BasicOperator* py_bop_obj, void * np_viewblinddata, void *py_int_hideloc)
{ 
  const int *p_viewblind_map = (int*)np_viewblinddata;
  assert(p_viewblind_map !=  NULL);
  const int center_int4loc = cvtInt6loc2Int4loc(py_bop_obj->obj_pos);
  const struct HexOfOffset center_hex = {center_int4loc / 100, center_int4loc % 100};
  const int map_col = MAP_XNUM;
  const int radius = 7;
  int hide_int6loc = 0;

  for (int i_radius = 1; i_radius <= radius; i_radius++ ){ // 环遍历
    if (hide_int6loc != 0) break;
    struct GA *p_gahexsoffset = ga_init(0,1,sizeof(struct HexOfOffset)); // ele_num ele_len attr_bytenum
    getHexsOnRingOfOffset(&center_hex, i_radius, p_gahexsoffset);
    for (int i = 0 ; i < p_gahexsoffset->count; i++){
      const struct HexOfOffset *p_tmphex = (struct HexOfOffset *)(ga_getele(p_gahexsoffset, i));
      if (p_viewblind_map[ p_tmphex->row * map_col + p_tmphex->col] == 0){
	hide_int6loc = cvtOffsetIntLocToInt6(p_tmphex->row, p_tmphex->col);
	break;
      }
    }
    ga_delete(p_gahexsoffset);
  }
  *((int*)(py_int_hideloc)) = hide_int6loc;
  return;
}


void warpGetMinDamgageLoc(const struct BasicOperator *py_p_bop, void *py_p_damagemap, const int len, void * py_p_locs)
{ 
  assert(len == 2);
  const float *p_damagemap = (float*) py_p_damagemap;
  const int map_col = MAP_XNUM;
  int * p_locs = (int*) py_p_locs;


  struct GA *p_gawicg = ga_init(0, 3, sizeof(int));
  whereICanGoRangeGA(py_p_bop, p_gawicg);

  // 计算最小战损点
  float min_damage = 1000; int min_loc = -1;
  int power_left = -1;
  for(int i = 0 ; i < p_gawicg->count ; i ++)
  {
    int *p_ele = (int*) ga_getele(p_gawicg,i);
    if (p_damagemap[p_ele[0] * map_col + p_ele[1]] < min_damage || 
	(p_damagemap[p_ele[0] * map_col + p_ele[1]] ==  min_damage && p_ele[2] > power_left))
    {
       min_damage = p_damagemap[p_ele[0] * map_col + p_ele[1]];
       min_loc = cvtOffsetIntLocToInt6(p_ele[0], p_ele[1]);
       power_left = p_ele[2];
    }
  }
  assert(min_damage < 1000);
  p_locs[0] = min_loc;
  power_left = -1;

  // 计算次优点
  float sec_min_damage = 1000; int sec_min_loc = -1;
  for(int i = 0 ; i < p_gawicg->count ; i ++)
  {
    int *p_ele = (int*) ga_getele(p_gawicg,i);
    if (p_damagemap[p_ele[0] * map_col + p_ele[1]] == min_damage) // 跳过最优
      continue;
    else if (p_damagemap[p_ele[0] * map_col + p_ele[1]] < sec_min_damage || 
	     (p_damagemap[p_ele[0] * map_col + p_ele[1]] == sec_min_damage && p_ele[2] > power_left))
    {
       sec_min_damage = p_damagemap[p_ele[0] * map_col + p_ele[1]];
       sec_min_loc = cvtOffsetIntLocToInt6(p_ele[0], p_ele[1]);
       power_left = p_ele[2];
    }
  }
  if (sec_min_damage >= 1000){
    p_locs[1] = min_loc;
  } else {
    p_locs[1] = sec_min_loc;
  }
  
  ga_delete(p_gawicg);
  return; 
}

void warptrendpathP2P(const struct BasicOperator *py_p_bopa, const struct BasicOperator *py_p_bopb, struct  BasicTensor *py_p_bt)
{  
  assert(py_p_bopa != NULL && py_p_bopb != NULL);
  assert(py_p_bt->data != NULL); 
  int cur_row, cur_col;
  getLocOfOffsetFromOperator(py_p_bopa, &cur_row, &cur_col);
  printf("attacker: row = %d, col = %d\n", cur_row, cur_col);
  getLocOfOffsetFromOperator(py_p_bopb, &cur_row, &cur_col);
  printf("objective: row = %d, col = %d\n", cur_row, cur_col);
  for(int i = 0 ; i < MAP_XNUM * MAP_YNUM; i++)
    py_p_bt->data[i] = -1;
  struct HexOfOffset objhex ;
  getLocOfOffsetFromOperator(py_p_bopb, &objhex.row, &objhex.col);  
  struct GA *p_gafullpath = ga_init(0, 3, sizeof(int));
  struct GA *p_gapartpath = ga_init(0, 3, sizeof(int));
  
  //  trendpathP2P(py_p_bopa, &objhex, p_gafullpath, p_gapartpath);
  trendpathP2P4Pass(py_p_bopa, &objhex, p_gafullpath, p_gapartpath);
  //先绘制full path
  printf("full path count = %d\n", p_gafullpath->count);
  printf("part path count = %d\n", p_gapartpath->count);
  for(int i = 0; i < p_gafullpath->count; i ++){
    int *p_ele = (int *) ga_getele(p_gafullpath, i);
    py_p_bt->data[p_ele[0] * MAP_XNUM + p_ele[1]] = p_ele[2];
  }
  
  ga_delete(p_gapartpath);
  ga_delete(p_gafullpath);

  return;
}


void warpMSAction(const struct BasicOperator *py_p_attacker, const struct BasicOperator *py_p_obj, const int flag_ss, const int flag_task, void *p_uniondamage_map, void *p_totalblind_map, void *p_aiaction)
{
  assert(p_aiaction != NULL);
  assert(flag_ss == 0 || flag_ss == 1);
  const int aiaction_len = AIACTION_ELELEN;
  // setlocale(LC_ALL, "");
  // printf("\t%ls --> %ls\n",py_p_attacker->obj_name, py_p_obj->obj_name );
  if (flag_ss == 1){ // 静态射击
    cvtStaticShooting2AIAction(py_p_attacker, py_p_obj, aiaction_len, (float*)p_aiaction);
  } else { // FFBT 模型
    if ( !g_flag_graphicmem_ok ){
      ((float*)p_aiaction)[0] = AIACTION_INVALID;
      struct GA* p_gaffbtroutes = ga_init(0, FFBTMODE_ELELEN, sizeof(float));
      float* p_bestroute = (float *) malloc( FFBTMODE_ELELEN * sizeof(float));
      if (py_p_obj->a1 == 0){
	getFFBTRoutes1000( py_p_attacker, py_p_obj, (float*)p_uniondamage_map, p_gaffbtroutes);
      }
      else {
	getFFBTRoutes1010( py_p_attacker, py_p_obj, (float*)p_uniondamage_map, p_gaffbtroutes);
      }
      if(getBestFFBTRoutes(p_gaffbtroutes, FFBTMODE_ELELEN, (int*)p_totalblind_map, p_bestroute )){
	cvtFFBTRoute2AIAction(py_p_attacker, py_p_obj, FFBTMODE_ELELEN, p_bestroute, aiaction_len,(float*) p_aiaction);
      } 
      ga_delete(p_gaffbtroutes);
      free(p_bestroute);
    } else {
      
    }
  } 
  return;
}
/*
void warpTankMsAction(const struct BasicOperator *py_p_att, const struct BasicOperator *py_p_obj, void * p_uniondamage_map, void * p_totalblind_map, void *p_aiaction)
{
  ((float*)p_aiaction)[0] = AIACTION_INVALID;
  if (p_aiaction != NULL && py_p_att->a1 == 1){
    printf("error in warpTankMsAction(): p_aiaction is null or py_p_att->a1 = %d\n", py_p_att->a1);
    return;
  }
  const int aiaction_len = AIACTION_ELELEN;
  struct GA* p_gaffbtroutes = ga_init(0, FFBTMODE_ELELEN, sizeof(float));
  float* p_bestroute = (float *) malloc( FFBTMODE_ELELEN * sizeof(float));
  // getFFBTRoutes1000( py_p_attacker, py_p_obj, (float*)p_uniondamage_map, p_gaffbtroutes);
  getALLFFBTRoutes(py_p_att, py_p_obj, p_gaffbtroutes)
  if(getBestFFBTRoutes(p_gaffbtroutes, FFBTMODE_ELELEN, (int*)p_totalblind_map, p_bestroute )){
    cvtFFBTRoute2AIAction(py_p_attacker, py_p_obj, FFBTMODE_ELELEN, p_bestroute, aiaction_len,(float*) p_aiaction);
  } 
  ga_delete(p_gaffbtroutes);
  free(p_bestroute);
  return;
}
*/

void warpGetALLFFBTRoutes(const struct BasicOperator*py_p_att, const struct BasicOperator*py_p_obj, const int max_routes_num, void * p_2d_routesdata)
{
  if (py_p_att == NULL || py_p_obj == NULL || py_p_att->a1 != 1){
    printf("error in warpGetALLFFBTRoutes(): p_aiaction is null or py_p_att->a1 = %d\n", py_p_att->a1);
    return;
  }
  struct GA* p_gaffbtroutes = ga_init(0, FFBTMODE_ELELEN, sizeof(float));
  getALLFFBTRoutes(py_p_att, py_p_obj, p_gaffbtroutes);
  // 将获取到的所有路径保存到p_2d_routesdata()中
  int cur_route_num = 0;
  for (int route_i = 0 ; route_i < p_gaffbtroutes->count; route_i ++){
    float *p_ele = (float*) ga_getele(p_gaffbtroutes, route_i);
    if (p_ele[FFBTMODE_SHOOTING_DAMAGELEVEL_A] > 0 && cur_route_num < max_routes_num){ // 能够攻击到对方算子
      float * p_cur_obj_mem = ((float*)p_2d_routesdata) + cur_route_num * FFBTMODE_ELELEN;
      memcpy(p_cur_obj_mem, p_ele, sizeof(float) * FFBTMODE_ELELEN);
      cur_route_num += 1;
    }
  }
  ga_delete(p_gaffbtroutes);
  return;
}


void warpTankMsAction(const struct BasicOperator *py_p_att, const struct BasicOperator *py_p_obj, void * p_uniondamage_map, void * p_totalblind_map, void *p_aiaction)
{
  ((float*)p_aiaction)[0] = AIACTION_INVALID;
  if (p_aiaction != NULL && py_p_att->a1 == 1){
    printf("error in warpTankMsAction(): p_aiaction is null or py_p_att->a1 = %d\n", py_p_att->a1);
    return;
  }
  const int aiaction_len = AIACTION_ELELEN;
  struct GA* p_gaffbtroutes = ga_init(0, FFBTMODE_ELELEN, sizeof(float));
  float* p_bestroute = (float *) malloc( FFBTMODE_ELELEN * sizeof(float));
  // getFFBTRoutes1000( py_p_attacker, py_p_obj, (float*)p_uniondamage_map, p_gaffbtroutes);
  getALLFFBTRoutes(py_p_att, py_p_obj, p_gaffbtroutes);
  if(getBestFFBTRoutes(p_gaffbtroutes, FFBTMODE_ELELEN, (int*)p_totalblind_map, p_bestroute )){
    cvtFFBTRoute2AIAction(py_p_att, py_p_obj, FFBTMODE_ELELEN, p_bestroute, aiaction_len,(float*) p_aiaction);
  } 
  ga_delete(p_gaffbtroutes);
  free(p_bestroute);
  return;
}
void warpSpecHideMSAction(const struct BasicOperator *py_p_attacker, const struct BasicOperator *py_p_obj, const int int_hideloc4,void *p_uniondamage_map,  void *p_aiaction)
{
  assert(p_aiaction != NULL);
  const int aiaction_len = AIACTION_ELELEN;
  ((float*)p_aiaction)[0] = AIACTION_INVALID;
  struct GA* p_gaffbtroutes = ga_init(0, FFBTMODE_ELELEN, sizeof(float));
  float* p_bestroute = (float *) malloc( FFBTMODE_ELELEN * sizeof(float));
  getFFBTRoutes1000( py_p_attacker, py_p_obj, (float*)p_uniondamage_map, p_gaffbtroutes);
  if (getSpecHideBestFFBTRoutes(p_gaffbtroutes,FFBTMODE_ELELEN,int_hideloc4,p_bestroute)){
    cvtFFBTRoute2AIAction(py_p_attacker, py_p_obj, FFBTMODE_ELELEN, p_bestroute, aiaction_len,(float*) p_aiaction);
  }
  ga_delete(p_gaffbtroutes);
  free(p_bestroute);
  return;
}

void warpDirectShootAction(const struct BasicOperator *py_p_attacker, const struct BasicOperator *py_p_obj, void * p_aiaction)
{
  assert(p_aiaction != NULL);
  const int aiaction_len = AIACTION_ELELEN;
  cvtStaticShooting2AIAction(py_p_attacker, py_p_obj, aiaction_len, (float*)p_aiaction);
  return;
}

void warpGetPath(const struct BasicOperator *p_attacker, const int obj_int6loc,const int len,void *p_path)
{
  for(int i=0;i<len;i++){
    ((int*)p_path)[i] = -1;
  }
  getPath(p_attacker, obj_int6loc, len,(int*)p_path);
  return;
}

void warpOneWeaponDirectDamageP2P(const struct BasicOperator *p_attacker,const struct BasicOperator *p_obj,const int weaponID,void *p_damage)
{
  ((float *)p_damage)[0]=damagelevelP2P(p_attacker,p_obj,weaponID);
  return;
}

void warpRushMovingAction(const struct BasicOperator *py_p_attacker, void * p_keyloc,  void * p_sawcount_map, void* p_aiaction)
{
  const int aiaction_len  = 20;
  assert(p_aiaction != NULL && aiaction_len == AIACTION_ELELEN);
  assert(p_keyloc != NULL && p_sawcount_map != NULL);

  setlocale(LC_ALL, "");
  // 更新被发现地图（全局变量）
  memcpy(g_mapstage.p_sawcount_map, (int*)p_sawcount_map, sizeof(int) * MAP_XNUM * MAP_YNUM);
  
  // 目标位置点选择
  const int global_key6loc = ((int*)p_keyloc)[0];
  const int stage_key6loc = ((int*)p_keyloc)[1];
  int obj_int6loc = stage_key6loc;
  if (global_key6loc != -1){
    struct dictionary* p_dicwicg = dic_new(0, sizeof(int));
    whereICanGoRange(py_p_attacker, p_dicwicg);
    char chars_4loc[5] = {'\0'};
    const int global_int4loc = cvtInt6loc2Int4loc(global_key6loc);
    cvtIntLocTo4StrOffLoc(global_int4loc, chars_4loc, 5); 
    // 全局关键点在单阶段内可以达到，选择全局关键点
    obj_int6loc = dic_find(p_dicwicg, chars_4loc, 5) == 1 ? global_key6loc : stage_key6loc;
    dic_delete(p_dicwicg);
  }

  // 目标点二次选择: 落脚点的选择
  const int obj_int4loc = cvtInt6loc2Int4loc(obj_int6loc);
  struct HexOfOffset obj_hex = {obj_int4loc / 100, obj_int4loc % 100};
  // printf("\t机动模型：%ls[%d], 目标点[%d, %d]\n",py_p_attacker->obj_name,py_p_attacker->obj_id , obj_hex.row, obj_hex.col );
  struct HexOfOffset find_hex = {0,0};
  if(findOptStopHex(py_p_attacker, &obj_hex, &find_hex)){
    obj_hex.row = find_hex.row;
    obj_hex.col = find_hex.col;
  } else {
    // printf("\t\t%ls[%d]没有找到最终落脚点，不机动\n", py_p_attacker->obj_name , py_p_attacker->obj_id);
    ((float *)p_aiaction)[0] = AIACTION_INVALID;
    // ((float *)p_aiaction)[1] = py_p_attacker->obj_id;
    // ((float *)p_aiaction)[2] = 1;
    memset(g_mapstage.p_sawcount_map, 0, sizeof(int) * MAP_YNUM * MAP_XNUM);
    return;
  }

  // 机动方式选择与机动路径规划==>AI可识别的指令字段p_aiaction
  obj_int6loc = cvtOffsetIntLocToInt6(obj_hex.row, obj_hex.col);
  if (checkHexIsValid( &obj_hex) == 0 || py_p_attacker->obj_step <= 0 || py_p_attacker->obj_pos == obj_int6loc){ 
    ((float *)p_aiaction)[0] = AIACTION_INVALID;
  } else {
    cvtRushMoving2AIAction(py_p_attacker, obj_int6loc, aiaction_len, (float*)p_aiaction);
  }

  // 重置全局变量被发现地图
  memset(g_mapstage.p_sawcount_map, 0, sizeof(int) * MAP_YNUM * MAP_XNUM);
  return;
}

void warpDA00SMAction(const struct BasicOperator *py_p_attacker, const struct BasicOperator *py_p_obj, const int flag_task , void * p_uniondamage_map, void * p_totalblind_map, void * p_aiaction)
{
  // 检查
  assert(p_aiaction != NULL) ;
  assert(py_p_attacker->a1 == 0 && py_p_attacker->obj_sonnum == 0 );
  if (!g_flag_graphicmem_ok){
    struct GA *p_gadaroutes = ga_init(0, DAMODE_0_ELELEN, sizeof(float));
    float * p_bestroute = (float *) malloc( DAMODE_0_ELELEN * sizeof(float));
    ((float *)p_aiaction)[0] = AIACTION_INVALID;
    if (py_p_obj->a1 == 0)
      getDARoutes0000( py_p_attacker, py_p_obj, (float*)p_uniondamage_map ,p_gadaroutes);
    else 
      getDARoutes0010( py_p_attacker, py_p_obj, (float*)p_uniondamage_map, p_gadaroutes);
    if(getBestDAroute( p_gadaroutes, 0, DAMODE_0_ELELEN, (int*)p_totalblind_map, flag_task,  p_bestroute)){
      /*
      // 防御任务下战车没有获得足够的战损，保持原地不动
      const float threshold_fanyu = py_p_obj->obj_blood * 0.3; // 能够打掉对方0.6以上的血量再出击；
      if(flag_task == 1 && (p_bestroute[DAMODE_0_DAMAGERESULT_FINAL] / py_p_obj->obj_value) < threshold_fanyu && py_p_attacker->obj_type == 2) 
      {
	((float*)p_aiaction)[0] = AIACTION_INVALID;
      } else {
	cvtDARoute2AIAction(py_p_attacker, py_p_obj, 0, DAMODE_0_ELELEN, p_bestroute, AIACTION_ELELEN, (float*)p_aiaction);
      }
    */
      ((float*)p_aiaction)[0] = AIACTION_INVALID;
      cvtDARoute2AIAction(py_p_attacker, py_p_obj, 0, DAMODE_0_ELELEN, p_bestroute, AIACTION_ELELEN, (float*)p_aiaction);
    }
    ga_delete(p_gadaroutes);
    free(p_bestroute);
  } else {
    
  }
  return ;
}

void warpDA01SMAction(const struct BasicOperator *py_p_attacker, const struct BasicOperator * py_p_peo, const struct BasicOperator *py_p_obj, const int flag_task , void * p_uniondamage_map, void * p_totalblind_map, void * p_aiaction)
{
  // 检查
  assert(p_aiaction != NULL) ;
  assert(py_p_attacker->a1 == 0 && py_p_attacker->obj_sonnum == 1 );
  if (!g_flag_graphicmem_ok){
    struct GA *p_gadaroutes = ga_init(0, DAMODE_1_ELELEN, sizeof(float));
    float * p_bestroute = (float *) malloc( DAMODE_1_ELELEN * sizeof(float));
    ( (float *)p_aiaction)[0] = AIACTION_INVALID;

    // printf("\twarpDA01SMAction\n");
    if (py_p_obj->a1 == 0){
      getDARoutes0100( py_p_attacker, py_p_peo, py_p_obj, (float*)p_uniondamage_map ,p_gadaroutes);
    } else {
      getDARoutes0110( py_p_attacker, py_p_peo, py_p_obj, (float*)p_uniondamage_map, p_gadaroutes);
    } 
    if(getBestDAroute( p_gadaroutes, 1, DAMODE_1_ELELEN, (int*)p_totalblind_map, flag_task,  p_bestroute)){
      /*
      // 防御任务下战车没有获得足够的战损，保持原地不动
      const float threshold_fanyu = py_p_obj->obj_blood * 0.6; // 能够打掉对方0.6以上的血量再出击；
      if(flag_task == 1 && (p_bestroute[DAMODE_1_DAMAGERESULT_FINAL] / py_p_obj->obj_value) < threshold_fanyu && py_p_attacker->obj_type == 2) {
	((float*)p_aiaction)[0] = AIACTION_INVALID;
      } else {
	cvtDARoute2AIAction(py_p_attacker, py_p_obj, 1, DAMODE_1_ELELEN, p_bestroute, AIACTION_ELELEN, (float*)p_aiaction);
      }
      */
      ((float*)p_aiaction)[0] = AIACTION_INVALID;
      cvtDARoute2AIAction(py_p_attacker, py_p_obj, 1, DAMODE_1_ELELEN, p_bestroute, AIACTION_ELELEN, (float*)p_aiaction);
    }
    ga_delete(p_gadaroutes);
    free(p_bestroute);
  } else {
    
  }
  return ;

}

void warpDC00Action(const struct BasicOperator * py_p_bop, const int city_loc6 , const float city_value, void * p_totaldamage_map, void * p_aiaction)
{
    assert(p_aiaction != NULL);
    assert(py_p_bop->obj_typex == 2 || (py_p_bop->obj_typex ==1 )); // 有人/无人战车/人员算子（策略AI未区分有人/无人战车）
    if (!g_flag_graphicmem_ok){
      struct GA * p_ga_dcroutes = ga_init(0, DCMODE_0_ELELEN, sizeof(float));
      float * p_best_dcroute = (float*) malloc(DCMODE_0_ELELEN * sizeof(float));
      ((float*)p_aiaction)[0] = AIACTION_INVALID;
      
      getDC00Routes(py_p_bop, city_loc6, city_value, (float*)p_totaldamage_map, p_ga_dcroutes);
      if (getBestDCRoute(p_ga_dcroutes, 0, p_best_dcroute)){
	cvtDCRoute2Aiaction(py_p_bop, p_best_dcroute, 0, 20, (float*)p_aiaction);
      }
      ga_delete(p_ga_dcroutes);
      free(p_best_dcroute);
    } else {
      
    }
    return;
}

void warpOccupyAction(const struct BasicOperator * py_p_bop, const int loc_city_int6, const float value_city,  void * p_totaldamage_map, const int aiaction_len, void * p_aiaction)
{
  bool flag_validpointers = py_p_bop != NULL && p_totaldamage_map != NULL && p_aiaction != NULL;
  bool flag_validdata = aiaction_len == 20;
  if (!flag_validdata || ! flag_validpointers){
    printf("error in warpOccupyAction() - flag_validroutes or flag_validdata is false\n");
    return;
  }
  if (!g_flag_graphicmem_ok) {
    //调用3个模块计算（层层递进）
    struct GA * p_ga_occupyingroutes = ga_init(0, OCCUMODE_ELELEN, sizeof(float));
    float * p_best_route = (float*) malloc (sizeof(float) * OCCUMODE_ELELEN);
    getOccupyingRoutes(py_p_bop, loc_city_int6, (float*)p_totaldamage_map, p_ga_occupyingroutes);
    if(getBestOccupyingRoute(p_ga_occupyingroutes, p_best_route)){
      cvtOccupyRoute2AIAction(py_p_bop, p_best_route, value_city, (float*)p_aiaction);
    }else{
      ((float*)p_aiaction)[0] = AIACTION_INVALID;
    }
    ga_delete(p_ga_occupyingroutes); free(p_best_route);
  } else {
    
  }
  return;
}

void warpScoutAction(const struct BasicOperator *py_p_bop, const int dir, const int mindis, const int maxdis, const int methodflag, const int aiaction_len, void * p_aiaction)
{
  // 参数检查
  bool flag = py_p_bop != NULL && p_aiaction!= NULL && dir >= 0 && dir <= 5;
  flag = flag && mindis >= 1 && mindis <= maxdis ;
  if (!flag){
    // printf("error in warpGetDirRegionMap: flag is False\n");
    ((float*)p_aiaction)[0] = AIACTION_INVALID;
    return ;
  }
  // 调用getCandidateScoutlocs()计算候选侦察点集合
  struct GA * p_gahexs = ga_init(0, 3, sizeof(int));
  getCandidateScoutlocs(py_p_bop, dir, mindis, maxdis, p_gahexs);
  // 计算获取到的最优位置
  char *p_str_criterion = "random";
  struct HexOfOffset hex_o = {0,0};
  if(getBestScoutloc(p_gahexs, p_str_criterion, &hex_o )){
    const int obj_int6loc = cvtOffsetIntLocToInt6(hex_o.row, hex_o.col);
    cvtRushMoving2AIAction(py_p_bop, obj_int6loc, aiaction_len, (float*)p_aiaction);
  } else{
    ((float*)p_aiaction)[0] = AIACTION_INVALID;
  }
  // 资源释放
  ga_delete(p_gahexs);
  return;
}

// /*---------------------------------宋国瑞添加--------------------------*/
// //特征向量初始化
// bool warpCuFeatureInit(const int redOpeNum,const int blueOpeNum,const int cityNum)
// {
//   bool flag_featureInit = featurecu_init(redOpeNum,blueOpeNum,cityNum);
//   return flag_featureInit; 
// }


// /*---------------------封装特征图计算函数-------------*/
// //是否为隐蔽点图特征图 维数：MAP_YNUM*MAP_XNUM
// void warpCalIsInCoverMap(void *p_isInCoverMap)
// {
//   assert(p_isInCoverMap!=NULL);
//   if(g_flag_graphicmem_ok)
//     calIsInCoverMapC((int*)p_isInCoverMap);
//   else{
//     for(int row = MAP_YMIN;row<MAP_YMAX;row++)
//       for(int col= MAP_XMIN ;col<MAP_XMAX;col++){
//         struct HexOfOffset cur_hex = {row,col};
//         bool flag_inCover = checkHexIsInCover(&cur_hex);
//         ((int*)p_isInCoverMap)[row*MAP_XNUM+col] = flag_inCover==true ? 1 : 0;
//       }
//   }
// }
// /* 机动范围图: 可以机动值为剩余机动力，不能机动值为-1 维数：MAP_YNUM*MAP_XNUM*/
// void warpCalWcgMap(int cur_int4loc,int cur_step,int obj_type,void *p_wcgMap)
// {
//   assert(p_wcgMap != NULL); 
//   calWcgMapC(cur_int4loc,cur_step,obj_type,(int*)p_wcgMap);
// }
// //c 计算机动范围图
// void warpCalWcgMapC(const struct BasicOperator *py_p_bop,void *p_wcgMap)
// {
//   assert(p_wcgMap != NULL);  

//   if(!g_flag_graphicmem_ok){
//     for (int i = MAP_YMIN; i < MAP_YMAX; i ++)
//       for (int j = MAP_XMIN; j <MAP_XMAX; j++)
//       {
//         int cur_loc = i * MAP_XNUM + j;
//         ((int*)p_wcgMap)[ cur_loc ] = -1 ;
//       }
//     struct GA *p_gawicg = ga_init(0, 3, sizeof(int));
//     whereICanGoRangeGA(py_p_bop, p_gawicg);
//     for(int i = 0 ; i < p_gawicg->count ; i ++)
//     {
//       int *p_ele = (int*) ga_getele(p_gawicg,i);
//       ((int*)p_wcgMap)[p_ele[0] * MAP_XNUM + p_ele[1]] = p_ele[2];
//     }
//     ga_delete(p_gawicg);
//   }
//   else{
//     int cur_int4loc = cvtInt6loc2Int4loc(py_p_bop->obj_pos);
//     int cur_step = (int)(py_p_bop->obj_step);
//     warpCalWcgMap(cur_int4loc,cur_step,py_p_bop->obj_type,p_wcgMap);
//   }
// }
// /* 造成战损图(不能机动的位置战损为-1) 维数：最大血量*MAP_YNUM*MAP_XNUM(可变的为攻击算子的血量)*/
// void warpCalDamageMap(const struct BasicOperator *p_attacker,const struct BasicOperator *p_obj,void *p_damageMap)
// {
//   assert(p_damageMap != NULL); 
//   //计算机动范围图
//   int *p_wcgAttMap = (int*)malloc(sizeof(int)*MAP_YNUM*MAP_XNUM);
//   int att_int4loc = cvtInt6loc2Int4loc(p_attacker->obj_pos);
//   calWcgMapC(att_int4loc,p_attacker->obj_step,p_attacker->obj_type,p_wcgAttMap);
//   //计算战损图
//   calDamageMapC(p_attacker,p_obj,p_wcgAttMap,(float*)p_damageMap);
//   free(p_wcgAttMap);  
// }

// //承受战损图(不能机动的位置战损为-1) 维数：算子最大血量×MAP_YNUM*MAP_XNUM(可变的为B算子的血量)
// void warpCalTakeDamageMap(const struct BasicOperator *p_bopA,const struct BasicOperator *p_bopB,void *p_takeDamageMap)
// {
//   assert(p_takeDamageMap != NULL);

//   //计算机动范围图
//   int *p_wcgAMap = (int*)malloc(sizeof(int)*MAP_YNUM*MAP_XNUM);
//   int a_int4loc = cvtInt6loc2Int4loc(p_bopA->obj_pos);
//   calWcgMapC(a_int4loc,p_bopA->obj_step,p_bopA->obj_type,p_wcgAMap);

//   int *p_wcgBMap = (int*)malloc(sizeof(int)*MAP_YNUM*MAP_XNUM);
//   int b_int4loc = cvtInt6loc2Int4loc(p_bopB->obj_pos);
//   calWcgMapC(b_int4loc,p_bopB->obj_step,p_bopB->obj_type,p_wcgBMap);

//   //计算战损图
//   if(p_bopA->obj_blood > 0)
//     calTakeDamageMapC(p_bopA,p_bopB,(int*)p_wcgAMap,(int*)p_wcgBMap,(float*)p_takeDamageMap);

//   free(p_wcgAMap);
//   free(p_wcgBMap);
// }

// void warpCalWholeTakeDamageMap(const struct BasicOperator *p_bopA,const struct BasicOperator *p_bopB,void *p_takeDamageMap)
// {
//   assert(p_takeDamageMap != NULL);

//   //计算机动范围图
//   int *p_wcgAMap = (int*)malloc(sizeof(int)*MAP_YNUM*MAP_XNUM);
//   int a_int4loc = cvtInt6loc2Int4loc(p_bopA->obj_pos);
//   calWcgMapC(a_int4loc,p_bopA->obj_step,p_bopA->obj_type,p_wcgAMap);

//   int *p_wcgBMap = (int*)malloc(sizeof(int)*MAP_YNUM*MAP_XNUM);
//   int b_int4loc = cvtInt6loc2Int4loc(p_bopB->obj_pos);
//   calWcgMapC(b_int4loc,p_bopB->obj_step,p_bopB->obj_type,p_wcgBMap);

//   //计算战损图
//   if(p_bopA->obj_blood > 0)
//     calWholeTakeDamageMapC(p_bopA,p_bopB,(int*)p_wcgAMap,(int*)p_wcgBMap,(float*)p_takeDamageMap);

//   free(p_wcgAMap);
//   free(p_wcgBMap);
// }
// // //计算A算子机动到各个位置之后在剩余机动范围内承受的最小战损图 维数： 算子最大血量 * MAP_YNUM*MAP_XNUM(可变的为B算子的血量)
// // void warpCalMoveTakeMinDamageMap(const struct BasicOperator *p_bopA,const struct BasicOperator *p_bopB,void *p_moveTakeDamageMap)
// // {
// //   //assert(p_wcgAMap != NULL && p_takeDamageMap != NULL && p_moveTakeDamageMap != NULL);
// //   assert(p_moveTakeDamageMap != NULL);
 
// //   //计算机动范围图
// //   int *p_wcgAMap = (int*)malloc(sizeof(int)*MAP_YNUM*MAP_XNUM);
// //   int a_int4loc = cvtInt6loc2Int4loc(p_bopA->obj_pos);
// //   calWcgMapC(a_int4loc,p_bopA->obj_step,p_bopA->obj_type,p_wcgAMap);

// //   int *p_wcgBMap = (int*)malloc(sizeof(int)*MAP_YNUM*MAP_XNUM);
// //   int b_int4loc = cvtInt6loc2Int4loc(p_bopB->obj_pos);
// //   calWcgMapC(b_int4loc,p_bopB->obj_step,p_bopB->obj_type,p_wcgBMap);

// //   //计算承受战损图
// //   float *p_takeDamageMap = (float*)malloc(sizeof(float)*OPERATOR_MAX_BLOOD*MAP_YNUM*MAP_XNUM);
// //   calTakeDamageMapC(p_bopA,p_bopB,p_wcgAMap,p_wcgBMap,p_takeDamageMap);

// //   //计算移动战速图
// //   calMoveTakeMinDamageMapC(p_bopA,p_bopB,(int*)p_wcgAMap,(float*)p_takeDamageMap,(float*)p_moveTakeDamageMap);  
  
// //   free(p_wcgAMap);
// //   free(p_wcgBMap);
// //   free(p_takeDamageMap);
// // }

// //计算是否在夺控点一格范围内图  维数：MAP_YNUM*MAP_XNUM
// void warpCalCityDefMap(const int city_int4loc,void *p_isCityDefMap)
// {
//   assert(p_isCityDefMap != NULL);
//   calCityDefMapC(city_int4loc,(int*)p_isCityDefMap);
// }

// /*---------------------宋国瑞2018年08月10日重新封装特征计算函数---------------------*/
// void warpAttackLevelMap(const struct BasicOperator *p_attacker,const struct BasicOperator *p_obj,void *p_attLevelMap)
// {
//   int flag_spec_wpindex = 0; //不指定武器类型
//   int wp_index = getBestWeaponIndex(p_attacker,p_obj->obj_type);
//   if(!flag_spec_wpindex)
//     wp_index = -1;
//   //计算机动范围图
//   int *p_wcgAttMap = (int*)malloc(sizeof(int)*MAP_YNUM*MAP_XNUM);
//   warpCalWcgMapC(p_attacker,p_wcgAttMap);

//   if(!g_flag_graphicmem_ok){
//     attacklevelMap_attMove(p_attacker, p_obj, wp_index, p_wcgAttMap,(float*)p_attLevelMap);  
//   }
 
//   free(p_wcgAttMap);
//   return;
// }

// void warpIsBlindMap(const struct BasicOperator *p_bop,void *p_blindMap)
// {
//   int loc_int4 = cvtInt6loc2Int4loc(p_bop->obj_pos);
//   struct HexOfOffset centor_hex = {loc_int4/100, loc_int4%100};
  
//   // 初始化图像为0【是盲区】
//   const int map_col = MAP_XNUM;
//   for (int i = MAP_YMIN; i < MAP_YMAX; i ++)
//     for (int j = MAP_XMIN; j <MAP_XMAX; j++)
//     {
//       int cur_loc = i * map_col + j;
//       ((int*)p_blindMap)[ cur_loc ] = 1 ;
//     }

//   struct dictionary *p_dic = dic_new(0,sizeof(int));
//   icuRange(&centor_hex, MAXIOUDIS_CAR, p_dic); //先车

//   for (int i = 0; i < p_dic->length; i++) {
//   if (p_dic->table[i] != 0) {
//     struct keynode *k = p_dic->table[i];
//     while (k) {
//       int cur_row = atoi(k->key) / 100;
//       int cur_col = atoi(k->key) % 100;
//       ((int*)p_blindMap)[ cur_row * map_col + cur_col] =  0; // 不是视野盲区
//       k = k->next;
//       }
//     }
//   }
//   dic_delete(p_dic);
// }
