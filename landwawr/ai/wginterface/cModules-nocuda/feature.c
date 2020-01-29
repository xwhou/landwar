#include "feature.h"

void icuRange(const struct HexOfOffset *p_hex, const int maxdistance, struct dictionary *p_dicloc2dis)
{
  struct GA *p_gahexsoffset = ga_init(0,1,sizeof(struct HexOfOffset)); // ele_num ele_len attr_bytenum
  getHexsInCircleOfOffset(p_hex, maxdistance, p_gahexsoffset);

  for(int i = 0 ; i <p_gahexsoffset->count; i++)
  {
    struct HexOfOffset *p_tmp_hex = (struct HexOfOffset*)ga_getele(p_gahexsoffset, i);
    if ( checkHexIsValid(p_tmp_hex) &&  icuIsOk(p_hex, p_tmp_hex, maxdistance))
    {
      int distance = getDistanceBetweenHexOfOffset(p_hex, p_tmp_hex); 
      int int_4loc = p_tmp_hex->row * 100 + p_tmp_hex->col;
      char chars_4loc[5]={'\0'};
      cvtIntLocTo4StrOffLoc(int_4loc, chars_4loc, 5);
      dic_add(p_dicloc2dis,chars_4loc,&distance,5,sizeof(int));
    }
    p_tmp_hex= NULL;
  }
  ga_delete(p_gahexsoffset);
  return;
}


void iouRange(const struct BasicOperator *p_bopa, const struct BasicOperator *p_bopb, float *p_ioumap)
{
  assert(p_ioumap != NULL);
  struct BasicOperator bopbcopy = *p_bopb;
  const int map_col = MAP_XNUM;
  const int map_count = MAP_XNUM * MAP_YNUM;
  for(int i = 0 ; i < map_count; i ++)
    p_ioumap[i] = 0;

  char chars_6_loc[7]={'\0'};
  cvtIntLocTo4StrOffLoc(p_bopa->obj_pos, chars_6_loc, 7);
  int cur_row, cur_col ;
  cvtChars6locToOffsetIntLoc(chars_6_loc, &cur_row, &cur_col);
  struct HexOfOffset centor_hex = {cur_row, cur_col};
  const int distance = p_bopb->obj_type == 1 ? 10 : 25;
  struct dictionary *p_dic = dic_new(0,sizeof(int));
  icuRange(&centor_hex, distance, p_dic);

  for (int i = 0; i < p_dic->length; i++) {
    if (p_dic->table[i] != 0) {
      struct keynode *k = p_dic->table[i];
      while (k) {
        cur_row = atoi(k->key) / 100; cur_col = atoi(k->key) % 100;
	bopbcopy.obj_pos = cvtOffsetIntLocToInt6(cur_row, cur_col);
	if(iouIsOk(p_bopa, &bopbcopy)){
	 p_ioumap[ cur_row * map_col + cur_col] = 1;
	}
	k = k->next;
      }
    }
  }
  dic_delete(p_dic);
  return;
}

void iouDynamicRange(const struct BasicOperator* p_bopa, const struct BasicOperator* p_bopb, float *p_ioumap)
{
  assert(p_bopa != NULL && p_bopb != NULL && p_ioumap != NULL);
  // struct BasicOperator bopa_copy = *p_bopa;
  struct BasicOperator bopb_copy = *p_bopb;
  // 初始化
  const int map_col = MAP_XNUM;
  const int map_count = MAP_XNUM * MAP_YNUM;
  for(int i = 0 ; i < map_count; i ++) p_ioumap[i] = 0;
  // 计算p_bopa 的机动范围
  struct GA *p_gawicg = ga_init(0, 3, sizeof(int));
  whereICanGoRangeGA(p_bopa, p_gawicg);
  for(int i = 0 ; i < p_gawicg->count ; i ++){
    // 更新观察算子的位置
    int *p_ele = (int*) ga_getele(p_gawicg,i);
    // bopa_copy.obj_pos = cvtOffsetIntLocToInt6(p_ele[0], p_ele[1]);
    int cur_row = p_ele[0];
    int cur_col = p_ele[1];
    struct HexOfOffset centor_hex = {cur_row, cur_col};
    const int distance = p_bopb->obj_type == 1 ? 10 : 25;
    struct dictionary *p_dic = dic_new(0,sizeof(int));
    // 计算通视/观察
    icuRange(&centor_hex, distance, p_dic);
    for (int i = 0; i < p_dic->length; i++) {
      if (p_dic->table[i] != 0) {
	struct keynode *k = p_dic->table[i];
	while (k) {
	  cur_row = atoi(k->key) / 100; cur_col = atoi(k->key) % 100;
	  // 将被观察算子放在通视位置，看看是否能够被观察
	  bopb_copy.obj_pos = cvtOffsetIntLocToInt6(cur_row, cur_col);
	  if(iouIsOk(p_bopa, &bopb_copy)){
	   p_ioumap[ cur_row * map_col + cur_col] += 1;
	  }
	  k = k->next;
	}
      }
    }
    dic_delete(p_dic);
  }
  ga_delete(p_gawicg);
}


//计算模式下使用
void whereICanGoRangeGA_com(const struct BasicOperator *p_bop, struct GA *p_gawicg)
{
  // assert(p_bop->obj_type == 1 || p_bop->obj_type ==2);
  int *p_flagmap = (int*) malloc(sizeof(int) * MAP_XNUM * MAP_YNUM);
  const int map_col = MAP_XNUM;
  for (int i = 0 ; i < MAP_YNUM * MAP_XNUM; i++)
      p_flagmap[i] = -1;

  struct HexOfOffset hex = {0,0};
  getLocOfOffsetFromOperator(p_bop, &(hex.row), &(hex.col));
  int int_4loc = hex.row * 100 + hex.col;
  struct Queue *p_queue = queue_init(0);
  queue_push(p_queue, &int_4loc);
  p_flagmap[ hex.row * map_col + hex.col ] = p_bop->obj_step;
  while (p_queue->count > 0)
  {
    queue_pop(p_queue, &int_4loc);
    struct HexOfOffset first_hex = {int_4loc / 100, int_4loc % 100};
    const int first_one_power = p_flagmap[first_hex.row * map_col + first_hex.col];
    if(first_one_power > 0) // 还有剩余机动力
    {
      struct GA *p_gahexs =  ga_init(0,1,sizeof(struct HexOfOffset));
      getNeighborHexsOfOffset(&first_hex, p_gahexs);
      for (int i = 0 ; i <p_gahexs->count; i ++)
      {
        struct HexOfOffset *p_tmphex = (struct HexOfOffset *)ga_getele(p_gahexs,i);
        if(!checkHexIsValid(p_tmphex)) // 无效六角格
          continue;
        int_4loc = p_tmphex->row * 100 + p_tmphex->col;
        // int needpower = getEnterHexNeededPower(int_4loc, i);
        // 在基础机动力的基础上加上被发现程度变量 ； 路径回溯时需要注意路径起始点的顺序与方向
        int needpower = 0;
        if (p_bop->obj_type == 2)
          //needpower = getEnterHexNeededPower(int_4loc, i) + g_mapstage.p_sawcount_map[p_tmphex->row * MAP_XNUM + p_tmphex->col];
          needpower = getEnterHexNeededPower(int_4loc, i);
        else
          //needpower = 1 + g_mapstage.p_sawcount_map[p_tmphex->row * MAP_XNUM + p_tmphex->col];
          needpower = 1;

        int left_power = first_one_power - needpower;
        const int tmp_maploc = p_tmphex->row * map_col + p_tmphex->col;
        if (p_flagmap[tmp_maploc] >= left_power) // 已经被更节省机动力消耗的路径遍历过的六角格
          continue;
        if (left_power >= 0){
          p_flagmap[tmp_maploc] = left_power;
          if (left_power > 0) // 还有剩余机动力，加入队列
            queue_push(p_queue, &int_4loc);
        }
      }
      ga_delete(p_gahexs);
    }
  }
  
  int p_ele[3]={0};
  for (int i = 0 ; i < MAP_YNUM; i++)
    for (int j = 0 ; j < MAP_XNUM; j++){
      int power = p_flagmap[i * map_col + j];
      if (power != -1){
	    p_ele[0] = i; p_ele[1] = j; p_ele[2] = power;
	    ga_appendele(p_gawicg,p_ele, 3, sizeof(int));
      }
    }

  queue_delete(p_queue);
  free(p_flagmap);
  return;
}

// 缓存模式下使用
void whereICanGoRangeGA_cache(const struct BasicOperator *p_bop, struct GA *p_gawicg)
{
  assert(p_bop != NULL);
  struct HexOfOffset cen_hex = {0,0};
  getLocOfOffsetFromOperator(p_bop, &(cen_hex.row), &(cen_hex.col));
  const int cen_int4loc = cen_hex.row * 100 + cen_hex.col;
  char chars_4pairlocs[9]={'\0'};
  int p_ele[3]={0};
  for (int row = 0 ; row < MAP_YNUM; row ++){
    for(int col = 0 ; col < MAP_XNUM; col ++){
      const struct HexOfOffset cur_hex = {row, col};
      const int dis = getDistanceBetweenHexOfOffset(&cen_hex, &cur_hex);
      if (dis > p_bop->obj_step ) continue;
      if (p_bop->obj_type == 1){ // 人员算子
        const int used_power = dis;
        p_ele[0] = row; p_ele[1] = col; p_ele[2] = p_bop->obj_step - used_power;
        // assert (p_ele[2] >= 0);
        ga_appendele(p_gawicg,p_ele, 3, sizeof(int)); // 剩余机动力>=0，表明该位置机动可达
      } else { //车辆算子
        int cur_int4loc = row * 100 + col;
        int key = cen_int4loc * 10000 + cur_int4loc;
        assert(cvtIntLocTo4StrOffLoc(key, chars_4pairlocs, 9));
        if (dic_find(g_mapattr.dic_pairlocs2pow, chars_4pairlocs,9)){
          const int used_power = ((int*)g_mapattr.dic_pairlocs2pow->p_findvalue)[0];
          assert (used_power >= 0);
          //printf("key = %s, used_power = %d\n", chars_4pairlocs, used_power);
          p_ele[0] = row; p_ele[1] = col; p_ele[2] = p_bop->obj_step - used_power;
          if (p_ele[2] >= 0)
            ga_appendele(p_gawicg,p_ele, 3, sizeof(int)); // 剩余机动力>=0，表明该位置机动可达
        }
      }
    }
  }
  return;
}

void whereICanGoRangeGA(const struct BasicOperator *p_bop, struct GA *p_gawicg)
{
  // time_t start,end;  
  // start =clock();//or time(&start);  
  int leftpower = p_bop->obj_step;
  // if (false && g_mapattr.dic_pairlocs2pow != NULL && leftpower <= 8){ // 缓存模式
  if (g_mapattr.dic_pairlocs2pow != NULL && leftpower <= 8){ // 缓存模式
    whereICanGoRangeGA_cache(p_bop, p_gawicg);
  } else { // 计算模式
    whereICanGoRangeGA_com(p_bop, p_gawicg);
  }
  // end =clock();  
  // count++;
  // printf("id, loc, initpow, time, count =(%d,%d,%f,%f,%d)\n",p_bop->obj_id, p_bop->obj_pos, p_bop->obj_step, (double)(end-start), count); 
  return ;
}


void whereICanGoRange(const struct BasicOperator *p_bop, struct dictionary *p_dicwicg)
{
  struct GA *p_gawicg = ga_init(0, 3, sizeof(int));
  whereICanGoRangeGA(p_bop, p_gawicg);

  char chars_4loc[5] = {'\0'};
  int int_4loc = 0;
  for (int i = 0 ; i < p_gawicg->count ; i++){
    const int *p_ele = (int*)ga_getele(p_gawicg, i);
    int_4loc = p_ele[0] * 100 + p_ele[1];
    cvtIntLocTo4StrOffLoc(int_4loc, chars_4loc, 5);
    int leftpower = p_ele[2];
    dic_add(p_dicwicg, chars_4loc, &leftpower, 5, sizeof(int));
  }
  ga_delete(p_gawicg);
  return;
}

void whereICanPassRangeGA(const struct BasicOperator *p_bop, struct GA *p_gawicp)
{
  //检查：算子必须是车辆,并且起始位置必须在道路网上
  struct HexOfOffset hex = {0,0};
  getLocOfOffsetFromOperator(p_bop, &(hex.row), &(hex.col));
  if(!checkHexIsRoad(&hex)){
    printf("error in whereICanPassRangeGA() : checkHexIsRoad() failed \n");
    return;
  }
  if(p_bop->obj_type != 2){
    printf("error in whereICanPassRangeGA(): bop is not a car\n");
    return;
  } 

  // 初始化
  int *p_flagmap = (int*) malloc(sizeof(int) * MAP_XNUM * MAP_YNUM);
  const int map_col = MAP_XNUM;
  for (int i = 0 ; i < MAP_YNUM * MAP_XNUM; i++)
      p_flagmap[i] = -1;
  
  const int power_scale = 2 ; // 原始每个机动力可以行军的六角格数目
  char chars_4loc[5] = {'\0'};
  int int_4loc = hex.row * 100 + hex.col;
  struct Queue *p_queue = queue_init(0);
  queue_push(p_queue, &int_4loc);
  p_flagmap[ hex.row * map_col + hex.col ] = p_bop->obj_step * power_scale; // 每个机动力可以走2个六角格

  while(p_queue->count > 0){
    queue_pop(p_queue, &int_4loc);
    cvtIntLocTo4StrOffLoc(int_4loc, chars_4loc, 5);
    const int first_one_power = p_flagmap[ (int_4loc / 100) * map_col + (int_4loc % 100)];
    if (first_one_power > 0){
      if (!dic_find( g_mapattr.dic_loc2roadnet, chars_4loc, 5)){ // 当前六角格不在道路网中
	printf("hex %d is not on the roadnet in whereICanPassRangeGA() \n", int_4loc);
	free(p_flagmap); p_flagmap = NULL;
	queue_delete(p_queue);
	return;
      }else{
	const int num_edges = ((int*)g_mapattr.dic_loc2roadnet->p_findvalue)[0];
	for (int i = 0 ; i < num_edges; i++){ // 遍历周围的六角格
	  const int tmp_int4loc = ((int*)g_mapattr.dic_loc2roadnet->p_findvalue)[1 + i * 2]; // [2 + i * 2 ]为道路类型，扩展模块
	  hex.row = tmp_int4loc / 100; hex.col = tmp_int4loc % 100;
	  if(!checkHexIsValid(&hex)){ // 无效六角格
	    printf("hex %d is invalid in whereICanPassRangeGA() \n", tmp_int4loc);
	    free(p_flagmap); p_flagmap = NULL;
	    queue_delete(p_queue);
	    return;
	  }
	  // 机动力 = 基础机动力 + 被发现程度	  
	  const int needpower = 1 + g_mapstage.p_sawcount_map[hex.row * MAP_XNUM + hex.col]; // 在原有机动力的基础上增加被发现程度变量
	  int left_power = first_one_power - needpower; 
	  
	  const int tmp_maploc = hex.row * map_col + hex.col;
	  if (p_flagmap[tmp_maploc] >= left_power) // 该方案不是最短路径（已存在更节省机动力的方案）
	    continue;
	  if (left_power >= 0){
	    p_flagmap[tmp_maploc] = left_power;
	    if (left_power > 0){
	      queue_push(p_queue, &tmp_int4loc);
	    }
	  }
	}
      }
    }
  }


  // 整理p_flagmap,加入选中的六角格到p_gawicp
  int p_ele[3] = {0};
  for (int i = 0 ; i < MAP_YNUM; i++)
    for (int j = 0 ; j < MAP_XNUM; j++){
      int power = p_flagmap[i * map_col + j];
      if (power != -1){
	p_ele[0] = i; p_ele[1] = j; p_ele[2] = power;
	ga_appendele(p_gawicp, p_ele, 3, sizeof(int));
      }
    }

  queue_delete(p_queue);
  free(p_flagmap); p_flagmap = NULL;
  return;
}

void whereICanPassRange(const struct BasicOperator *p_bop, struct dictionary *p_dicwicp)
{
  struct GA *p_gawicp = ga_init(0, 3, sizeof(int));
  whereICanPassRangeGA(p_bop, p_gawicp);
  
  // 进行转换
  char chars_4loc[5] = {'\0'};
  int int_4loc = 0;
  for (int i = 0 ; i < p_gawicp->count ; i++){
    const int *p_ele = (int*)ga_getele(p_gawicp, i);
    int_4loc = p_ele[0] * 100 + p_ele[1];
    cvtIntLocTo4StrOffLoc(int_4loc, chars_4loc, 5);
    int leftpower = p_ele[2];
    dic_add(p_dicwicp, chars_4loc, &leftpower, 5, sizeof(int));
  }
  
  ga_delete(p_gawicp);
  return;
}

bool trendpathP2P(const struct BasicOperator *p_bop, const struct HexOfOffset *p_objhex, struct GA *p_gafullpath, struct GA *p_gapartpath)
{
  assert(p_bop->obj_type == 1 || p_bop->obj_type == 2);
  struct HexOfOffset inithex={0,0};
  getLocOfOffsetFromOperator(p_bop, &inithex.row, &inithex.col);
  if( inithex.row == p_objhex->row && inithex.col == p_objhex->col){// 当前位置即为目标点
    return false;
  }
  // printf("trendpathP2P\n");
  // printf("init loc = (%d, %d), obj loc = (%d, %d)\n",inithex.row, inithex.col, p_objhex->row, p_objhex->col);

  struct BasicOperator bopcopy = *p_bop;
  struct dictionary *p_dicwicg = dic_new(0,sizeof(int)); 
  const int oldpower = p_bop->obj_step;
  const int newpower = 500 ; // 小于python 中定义的maxslopepower = 1e6
  const int offsetpower = newpower - oldpower;
  bopcopy.obj_step = newpower;
  whereICanGoRange(&bopcopy, p_dicwicg);
  
  // 计算全局路径
  int p_ele[3]={0};
  char chars_4loc[5]={'\0'};
  char tmpchars_4loc_[5]={'\0'};
  int int_4loc = p_objhex->row * 100 + p_objhex->col;
  cvtIntLocTo4StrOffLoc(int_4loc, chars_4loc, 5);
  if (!dic_find(p_dicwicg, chars_4loc ,5)){// 目标太远
    dic_delete(p_dicwicg);
    return false;
  }

  int tmppow = ((int*)(p_dicwicg->p_findvalue))[0];
  struct HexOfOffset tmpHex = {p_objhex->row, p_objhex->col};
  p_ele[0]=tmpHex.row; p_ele[1]=tmpHex.col;p_ele[2] = tmppow;
  ga_appendele(p_gafullpath, p_ele, 3, sizeof(int));
  while(tmpHex.row != inithex.row || tmpHex.col != inithex.col){
    struct GA *p_gaseqhexs = ga_init(0, 1, sizeof(struct HexOfOffset));
    getNeighborHexsOfOffset(&tmpHex, p_gaseqhexs);
    int_4loc = tmpHex.row * 100 + tmpHex.col;
    cvtIntLocTo4StrOffLoc(int_4loc, tmpchars_4loc_, 5);

    for(int i = 0 ; i < p_gaseqhexs->count; i++){
      struct HexOfOffset *p_tmphex = (struct HexOfOffset *) ga_getele(p_gaseqhexs, i);
      int_4loc = p_tmphex->row * 100 + p_tmphex->col;
      cvtIntLocTo4StrOffLoc(int_4loc, chars_4loc, 5);
      // 区分谁是中心点，谁是邻域点， 谁进入谁，从哪个方向进入
      int needpower = 0;
      if (p_bop->obj_type == 2)
	//needpower =  g_mapstage.p_sawcount_map[tmpHex.row * MAP_XNUM + tmpHex.col] + getEnterHexNeededPower(tmpHex.row * 100 + tmpHex.col, g_dir_map[i]);
	needpower = getEnterHexNeededPower(tmpHex.row * 100 + tmpHex.col, g_dir_map[i]);
      else
	// needpower = 1 + g_mapstage.p_sawcount_map[tmpHex.row * MAP_XNUM + tmpHex.col];
	needpower = 1;
      if(dic_find(p_dicwicg, chars_4loc ,5) == 1 && *((int*)(p_dicwicg->p_findvalue)) - tmppow == needpower){
	tmppow = *((int*)(p_dicwicg->p_findvalue));
	tmpHex.row = p_tmphex->row; tmpHex.col = p_tmphex->col;
	p_ele[0]=tmpHex.row; p_ele[1]=tmpHex.col; p_ele[2] = tmppow;
	ga_appendele(p_gafullpath, p_ele, 3, sizeof(int));
	break;
      }
    }
    ga_delete(p_gaseqhexs);
  }
  dic_delete(p_dicwicg);

  // 更新局部路径 
  for(int i = p_gafullpath->count-1 ; i >= 0; i--){
      int *p_ele = (int*) ga_getele(p_gafullpath, i);
      p_ele[2] -= offsetpower;
      if(p_ele[2]>=0)
	       ga_appendele(p_gapartpath, p_ele, 3, sizeof(int));
      else
	       p_ele[2]= 0;// 路径可视化，保证该格子为>=0的数值
  }
  return (p_gapartpath->count >= 2);
}


bool getPath(const struct BasicOperator *p_attacker, const int obj_int6loc,int len,int *p_path)
{
  struct GA *p_gafullpath = ga_init(0,3,sizeof(int));
  struct GA *p_gapartpath = ga_init(0,3,sizeof(int));
  const int obj_int4loc = cvtInt6loc2Int4loc(obj_int6loc);
  struct HexOfOffset obj_hex = {obj_int4loc / 100, obj_int4loc % 100};
  trendpathP2P(p_attacker, &obj_hex, p_gafullpath, p_gapartpath);
  int num = 0;
  for(int i = p_gafullpath->count-1 ; i >= 0; i--){
      int *p_ele = (int*) ga_getele(p_gafullpath, i);
      p_path[num] = cvtOffsetIntLocToInt6(p_ele[0],p_ele[1]);
      num++;
      if( num == len)
        break;
  }
  ga_delete(p_gapartpath); ga_delete(p_gafullpath);
  return true;
}
bool findOptStopHex(const struct BasicOperator *p_bop, const struct HexOfOffset *p_objhex, struct HexOfOffset *p_findhex)
{

  bool flag_find = false;
  const int ori_int4loc = cvtInt6loc2Int4loc(p_bop->obj_pos);
  const struct HexOfOffset ori_hex = {ori_int4loc / 100, ori_int4loc % 100};
  int min_dis = getDistanceBetweenHexOfOffset(&ori_hex, p_objhex);// 最远距离设置为初始距离,至少保证呢个不能越走越远
  struct GA *p_gawicg = ga_init(0, 3, sizeof(int));
  whereICanGoRangeGA(p_bop, p_gawicg);
  
  for(int i = 0 ; i < p_gawicg->count ; i ++)
  {
    int *p_ele = (int*) ga_getele(p_gawicg,i);
    if (g_mapstage.p_sawcount_map[p_ele[0] * MAP_XNUM + p_ele[1]] <= 0 ){ // 是躲避点(没有任何算子能看到)
      struct HexOfOffset tmp_stophex = {p_ele[0], p_ele[1]};
      int tmp_dis = getDistanceBetweenHexOfOffset(p_objhex, &tmp_stophex);
      if (tmp_dis < min_dis){
	min_dis = tmp_dis;
	p_findhex->row = tmp_stophex.row;
	p_findhex->col = tmp_stophex.col;
	flag_find = true;
      }
    }
  }
  ga_delete(p_gawicg);
  return flag_find;
}

bool trendpathP2P4Pass(const struct BasicOperator *p_bop, const struct HexOfOffset *p_objhex, struct GA *p_gafullpath, struct GA *p_gapartpath)
{
  const int src_int4loc = cvtInt6loc2Int4loc(p_bop->obj_pos);
  struct HexOfOffset src_hex = {src_int4loc / 100, src_int4loc % 100};
  if (src_hex.row == p_objhex->row && src_hex.col == p_objhex->col){// 算子在目标位置上
    return false;
  }
  if (!checkHexIsRoad(&src_hex) ||(p_bop->obj_type != 2)){ // 算子不再道路上或者算子不是车辆
    return false;
  }
  struct HexOfOffset tmp_obj_hex = {p_objhex->row, p_objhex->col};
  struct HexOfOffset *p_tmp_objhex = &tmp_obj_hex;
  if (!checkHexIsRoad(p_objhex)){//目标位置不是道路，矫正目标位置到道路上
    const int dis_threshold = p_bop->obj_stepmax * 2;
    if (!getNeighRoadHex(p_objhex, dis_threshold, p_tmp_objhex)){ // 阈值范围内不存在最近临道路六角格,无法近似
     return false;
    }
  }

  struct BasicOperator bopcopy = *p_bop;
  const int oldpower = p_bop->obj_step;
  const int newpower = 200;
  const int offsetpower = (newpower - oldpower) * 2;// 行军单位机动力可以走2格
  
  bopcopy.obj_step = newpower;

  struct dictionary *p_dicwicp = dic_new(0, sizeof(int));
  whereICanPassRange(&bopcopy, p_dicwicp);

  int p_ele[3] ={0};
  char tmp_chars4loc[5] = {'\0'};
  int tmp_int4loc = p_tmp_objhex->row * 100 + p_tmp_objhex->col;
  cvtIntLocTo4StrOffLoc(tmp_int4loc, tmp_chars4loc, 5);
  if (!dic_find(p_dicwicp, tmp_chars4loc, 5)){
    dic_delete(p_dicwicp);
    return false;
  }

  int tmppow = ((int*)(p_dicwicp->p_findvalue))[0]; 
  p_ele[0] = p_tmp_objhex->row; p_ele[1] = p_tmp_objhex->col; p_ele[2] = tmppow;
  ga_appendele(p_gafullpath, p_ele, 3, sizeof(int));

  while(src_int4loc != tmp_int4loc ){
    const int needpower = 1 + g_mapstage.p_sawcount_map[(tmp_int4loc/100) * MAP_XNUM + (tmp_int4loc%100)];// 引入被发现程度作为附加机动力

    if(!dic_find(g_mapattr.dic_loc2roadnet, tmp_chars4loc, 5)) 
      break;
    const int num_edges = ((int*)g_mapattr.dic_loc2roadnet->p_findvalue)[0];
    bool flag_find = false;
    for (int i = 0 ;  i < num_edges ; i++){
      tmp_int4loc = ((int*)g_mapattr.dic_loc2roadnet->p_findvalue)[1 + 2 * i];
      cvtIntLocTo4StrOffLoc(tmp_int4loc, tmp_chars4loc, 5);
      if (dic_find(p_dicwicp, tmp_chars4loc, 5) == 1 && *((int*)(p_dicwicp->p_findvalue)) - tmppow == needpower){
	tmppow = *((int*)(p_dicwicp->p_findvalue));
	p_ele[0] = tmp_int4loc / 100; p_ele[1] = tmp_int4loc % 100; p_ele[2] = tmppow;
	ga_appendele(p_gafullpath, p_ele, 3, sizeof(int));
	flag_find = true;
	break;
      }
    }
    if(!flag_find){ // 正常情况下，每个中间节点能够找出下一个路径上的父节点
      printf("can not find next road hex\n");
      break;
    }
  }

  if(src_int4loc != tmp_int4loc){
    printf("error in trendpathP2P4Pass() \n");
    dic_delete(p_dicwicp);
    return false;
  }
  dic_delete(p_dicwicp);


  // 更新局部路径(结果需要按照道路类型进行修正，累积行军六角格的数量不超过该道路所能承载的限制)
  // *BUG* 下列代码，一旦中间存在一个失误的六角格，后续所有六角格都无法对齐
  // *BUG2* 一旦路径长度达到道路限制，后续添加不会成功，但是仍然会尝试添加
  for(int i = p_gafullpath->count-1 ; i >= 0; i--){
      int *p_ele = (int*) ga_getele(p_gafullpath, i);
      p_ele[2] -= offsetpower;

      const struct HexOfOffset cur_hex = {p_ele[0], p_ele[1]};
      int road_limit = 0;
      if(p_gapartpath->count <= 0){// 路径上尚未选出道路
	road_limit = 1e5;	
      } else {
	const int *p_lastele =  (int*) ga_getele(p_gapartpath, (p_gapartpath->count - 1)); // 当前已有路径上的最后一个六角格
	const struct HexOfOffset  last_hex = { p_lastele[0], p_lastele[1]};
	const int roadtype = getRoadTypeBetweenHex(&cur_hex, &last_hex);
	switch(roadtype){
	  case 0:{road_limit = LIMIT_BLACKRED_PASS; break;}
	  case 1:{road_limit = LIMIT_REDROAD_PASS; break;}
	  case 2:{road_limit = LIMIT_ORANGEROAD_PASS; break;}
	  default:{
	    printf("road type error in trendpathP2P4Pass()\n");
	    road_limit = -1;
	    break;
	  }
	}
      }
      if(p_ele[2] >= 0 && p_gapartpath->count < road_limit) // 存在路径 & 未达到道路限制
	ga_appendele(p_gapartpath, p_ele, 3, sizeof(int));
      else { 
	p_ele[2]= 0;// 路径可视化，保证该格子为>=0的数值
	break;
      }
  }
      
  return p_gapartpath->count >= 2;
}

int attacklevelP2P(const struct BasicOperator *p_attacker, const struct BasicOperator *p_obj, const int weapen_index)
{
  struct HexOfOffset hex_attacker, hex_obj;
  getLocOfOffsetFromOperator(p_attacker,&(hex_attacker.row),&(hex_attacker.col));
  getLocOfOffsetFromOperator(p_obj,&(hex_obj.row),&(hex_obj.col));

  // 检查算子位置的有效性
  if(!checkHexIsValid(&hex_attacker) || !checkHexIsValid(&hex_obj)){
    printf("error in attacklevelP2P(). checkHexIsValid hex_attacker(%d,%d), hex_obj(%d,%d)\n",
      hex_attacker.row, hex_attacker.col, hex_obj.row , hex_obj.col);
    return -1;
  }
  
  const int distance = getDistanceBetweenHexOfOffset(&hex_attacker, &hex_obj);
  const int object_type = p_obj->obj_type == 1 ? PEOPLE : CAR;
  const int aim = getSpecifiedWeaponAttackAim(g_mapattr.dic_wpid2attrs, p_attacker, weapen_index, object_type );
  if(distance > aim)
    return -1; // 超过射程,返回-1无效攻击等级

  // 检查武器与目标类型的一致性
  const int attacker_blood = p_attacker->obj_blood;
  const int *p_attacklevel = getSpecifiedWeaponAttackLevelData(g_mapattr.dic_wpid2attrs, p_attacker, weapen_index, object_type);
  if (p_attacklevel == NULL || attacker_blood <= 0){ 
    // printf("error in attacklevelP2P(). p_attacklevel == NULL\n");
    return -1;
  }
  int tmp_attacklevelvalue = p_attacklevel[distance]; // BUG0 人员算子不能射击人员算子的情况：计算的攻击等级数据首地址已经包含了p_attacklevel算子血量的偏移
  // if(object_type == PEOPLE ) // 任何武器对人，都需要考虑携带武器的算子的车/班数
    // tmp_attacklevelvalue = p_attacklevel[(attacker_blood - 1) * MAX_AIMRANGE  + distance];
  
  int tmp_attacklevel_rect = getEleAndDisRectValue(&hex_attacker, &hex_obj, object_type);
  tmp_attacklevelvalue += tmp_attacklevel_rect;
  tmp_attacklevelvalue = tmp_attacklevelvalue > 0 ? tmp_attacklevelvalue : 0;
  return tmp_attacklevelvalue;
}


bool attacklevelMap(const struct BasicOperator *p_bop_att, const struct BasicOperator *p_bop_obj, const int wp_index, float * p_atmap_data)
{
  assert(p_bop_obj != NULL && p_bop_att != NULL && p_atmap_data != NULL);
  assert(wp_index >= 0 && wp_index < p_bop_att->obj_wznum && p_bop_att->obj_blood > 0);
  // 检查算子位置
  struct HexOfOffset hex_att = {0,0};
  getLocOfOffsetFromOperator(p_bop_att, &(hex_att.row), &(hex_att.col));
  assert(checkHexIsValid(&hex_att));
  
  // 获取武器的攻击等级树组
  const int obj_type = p_bop_obj->obj_type;
  const int *p_attacklevel = getSpecifiedWeaponAttackLevelData(g_mapattr.dic_wpid2attrs, p_bop_att, wp_index, obj_type);
  if (p_attacklevel == NULL){ // 匹配武器与目标类型
   for (int row = 0 ; row < MAP_YNUM; row ++){
    for (int col = 0 ; col < MAP_XNUM ; col ++){
      const int cur_loc = row * MAP_XNUM + col;
      p_atmap_data[cur_loc] = DEFALUT_ZERO;
    }
   }
   return false;
  }
   
  // 目标算子遍历地图
  const int aim = getSpecifiedWeaponAttackAim(g_mapattr.dic_wpid2attrs, p_bop_att, wp_index, obj_type );
  for (int row = 0 ; row < MAP_YNUM; row ++)
    for (int col = 0 ; col < MAP_XNUM ; col ++)
    {
      struct HexOfOffset hex_obj={row, col};
      const int cur_loc = row * MAP_XNUM + col;
      int dis = getDistanceBetweenHexOfOffset(&hex_att, &hex_obj);
      if (dis > aim){
	p_atmap_data[cur_loc] = DEFALUT_ZERO;
	continue;
      } else {
	int tmp_attacklevelvalue = p_attacklevel[dis];
	if(obj_type == PEOPLE ) // 任何武器对人，都需要考虑携带武器的算子的车/班数
	  tmp_attacklevelvalue = p_attacklevel[(p_bop_att->obj_blood- 1) * MAX_AIMRANGE  + dis];
	int tmp_attacklevel_rect = getEleAndDisRectValue(&hex_att, &hex_obj, obj_type);
	tmp_attacklevelvalue += tmp_attacklevel_rect;
	tmp_attacklevelvalue = tmp_attacklevelvalue > 0 ? tmp_attacklevelvalue : 0;
	p_atmap_data[cur_loc] = tmp_attacklevelvalue;
      }
    }

  return true;
}

//Bug0;修改，加入wp_index = -1情况：选择最大战损的武器
bool attacklevelMap_attMove(const struct BasicOperator *p_bop_att, const struct BasicOperator *p_bop_obj, const int wp_index, const int* p_attWcgMap,float * p_atmap_data)
{
  assert(p_bop_obj != NULL && p_bop_att != NULL && p_atmap_data != NULL);
  assert(wp_index >= -1 && wp_index < p_bop_att->obj_wznum && p_bop_att->obj_blood > 0);
  
  // 检查算子位置
  struct HexOfOffset hex_att_init = {0,0};
  getLocOfOffsetFromOperator(p_bop_att, &(hex_att_init.row), &(hex_att_init.col));
  struct HexOfOffset hex_obj = {0,0};
  getLocOfOffsetFromOperator(p_bop_obj, &(hex_obj.row), &(hex_obj.col));
  assert(checkHexIsValid(&hex_obj) && checkHexIsValid(&hex_att_init));

  int min_wpindex = wp_index >=0 ? wp_index : 0;
  int max_wpindex = wp_index >=0 ? wp_index + 1:p_bop_att->obj_wznum;

  //机动不到的位置值为-1
  for (int row = 0 ; row < MAP_YNUM; row ++)
    for (int col = 0 ; col < MAP_XNUM ; col ++)
      if(p_attWcgMap[row * MAP_XNUM + col] < 0)
        p_atmap_data[row * MAP_XNUM + col] = -1;
      else
        p_atmap_data[row * MAP_XNUM + col] = DEFALUT_ZERO;

  for(int wp_iter = min_wpindex ; wp_iter < max_wpindex ; wp_iter ++){
    const int obj_type = p_bop_obj->obj_type;
    const int *p_attacklevel = getSpecifiedWeaponAttackLevelData(g_mapattr.dic_wpid2attrs, p_bop_att, wp_iter, obj_type);
    if(p_attacklevel == NULL) continue;
    const int aim = getSpecifiedWeaponAttackAim(g_mapattr.dic_wpid2attrs, p_bop_att, wp_iter, obj_type );

    bool flag_isDaodan = false;
    if (p_bop_att->a1 == 1) flag_isDaodan =  checkWeaponIsDaoDan(p_bop_att->p_obj_wpids[wp_iter]);
    if(flag_isDaodan){  //对坦克，如果是导弹，只更新当前位置的攻击等级
      int dis = getDistanceBetweenHexOfOffset(&hex_att_init, &hex_obj);
      if (dis <= aim) {
        int tmp_attacklevelvalue = p_attacklevel[dis];
        if(obj_type == PEOPLE ) // 任何武器对人，都需要考虑携带武器的算子的车/班数
          tmp_attacklevelvalue = p_attacklevel[(p_bop_att->obj_blood- 1) * MAX_AIMRANGE  + dis];
        int tmp_attacklevel_rect = getEleAndDisRectValue(&hex_att_init, &hex_obj, obj_type);
        tmp_attacklevelvalue += tmp_attacklevel_rect;
        tmp_attacklevelvalue = tmp_attacklevelvalue > 0 ? tmp_attacklevelvalue : 0;
        const int cur_loc =hex_att_init.row*MAP_XNUM+hex_att_init.col;
        p_atmap_data[cur_loc] = tmp_attacklevelvalue > p_atmap_data[cur_loc]?tmp_attacklevelvalue:p_atmap_data[cur_loc];
      }
      continue;
    }

    //printf("bop.ID = %d,wp_index = %d,aim = %d\n",p_bop_att->obj_id,wp_iter,aim);
    for (int row = 0 ; row < MAP_YNUM; row ++)
      for (int col = 0 ; col < MAP_XNUM ; col ++){
        if(p_attWcgMap[row*MAP_XNUM+col] < 0) continue;
        struct HexOfOffset hex_att={row, col};
        const int cur_loc = row * MAP_XNUM + col;
        int dis = getDistanceBetweenHexOfOffset(&hex_att, &hex_obj);
        if (dis > aim) continue;
        int tmp_attacklevelvalue = p_attacklevel[dis];
        if(obj_type == PEOPLE ) // 任何武器对人，都需要考虑携带武器的算子的车/班数
          tmp_attacklevelvalue = p_attacklevel[(p_bop_att->obj_blood- 1) * MAX_AIMRANGE  + dis];
        int tmp_attacklevel_rect = getEleAndDisRectValue(&hex_att, &hex_obj, obj_type);
        tmp_attacklevelvalue += tmp_attacklevel_rect;
        tmp_attacklevelvalue = tmp_attacklevelvalue > 0 ? tmp_attacklevelvalue : 0;
        p_atmap_data[cur_loc] = tmp_attacklevelvalue > p_atmap_data[cur_loc]?tmp_attacklevelvalue:p_atmap_data[cur_loc];
      }
  }
  return true;
}

float damagelevelP2P(const struct BasicOperator *p_attacker, const struct BasicOperator *p_obj, const int weapen_index)
{
  // 攻击算子与目标算子的血量>0

  assert(p_obj->obj_blood >= 0 && p_attacker->obj_blood >= 0);
  if(p_attacker->obj_blood == 0 ){ // 攻击算子无剩余血量
    //printf("无剩余血量\n");
    return -1;
  }
  // p_attacker可以观察p_obj
  if(iouIsOk(p_attacker,p_obj) == false){
    //printf("算子之间不通视\n");
    return -1;
  }

  // 检查武器：武器与目标类型，距离与射程，弹药数目
  struct HexOfOffset hex_attacker, hex_obj;
  getLocOfOffsetFromOperator(p_attacker,&(hex_attacker.row),&(hex_attacker.col));
  getLocOfOffsetFromOperator(p_obj,&(hex_obj.row),&(hex_obj.col));
  const int distance = getDistanceBetweenHexOfOffset(&hex_attacker, &hex_obj);
  //printf("------------------*\n");
  const int flg_check = checkSpecifiedWeaponBeforeShooting(g_mapattr.dic_wpid2attrs, p_attacker, p_obj, weapen_index, distance);
  if(flg_check != ERROR_WEAPENCHECK_OK){
    // printf ("flg_check = %d\n", flg_check);
    return -1;
  }

  int attacklevelvalue = attacklevelP2P(p_attacker, p_obj, weapen_index);

  int flag_wz2obj; // 使用哪个战损文件
  const int objective_type = p_obj->obj_type == 1 ? PEOPLE : CAR;
  const bool flag_isltfweapon = getSpecifiedWeaponType(p_attacker, weapen_index) == WEAPENTYPE_LTF; 
  if (objective_type == PEOPLE)
    flag_wz2obj = DAMAGELEVEL_ALLW2PEOPLE;
  else
    flag_wz2obj = flag_isltfweapon ? DAMAGELEVEL_ILW2CAR : DAMAGELEVEL_ZM2CAR;
  
  float real_damage = getDamageLevelP2P(p_attacker, p_obj, flag_wz2obj, attacklevelvalue); 
  return real_damage;

  //return attacklevelvalue;
}

void listdamages(const struct BasicOperator *p_attacker , const struct BasicOperator *p_obj,  const struct dictionary*p_dicwicg
,struct GA *p_gadamagelist)
{
  const int ele_len = 3 + p_attacker->obj_wznum;
  assert(ele_len == p_gadamagelist->ele_len);
  float *p_ele = (float*) malloc (sizeof(float) * ele_len);
  struct BasicOperator attcopy = *p_attacker;
  for (int i = 0; i < p_dicwicg->length; i++){
    if (p_dicwicg->table[i] != 0){
      struct keynode *k = p_dicwicg->table[i];
      while (k){
	struct HexOfOffset hex = {atoi(k->key)/100, atoi(k->key) % 100};
	updateOperatorLoc(&attcopy, hex.row, hex.col);
	bool flg_validweapen = false;
	for(int j = 0 ; j < p_attacker->obj_wznum; j ++){
	  p_ele[3 + j] = damagelevelP2P(&attcopy, p_obj, j);
	  if( !flg_validweapen && p_ele[3+j] > 0 ) // 保证战损的有效性
	    flg_validweapen = true; // 该位置存在有效战损
	}
	if (flg_validweapen){
	  p_ele[0] = hex.row; p_ele[1] = hex.col; p_ele[2]= ((int*)(k->value))[0];
	  ga_appendele(p_gadamagelist, p_ele, ele_len, sizeof(float));
	}
	k = k->next;
      }
    }
  } // 遍历所有可到达的位置
  free(p_ele); 
  p_ele = NULL;
  return ;
}

int optShootingCond(const struct GA *p_gadamagelist, const int len , float *p_ele)
{
  assert(len == 5);
  float maxdamage = -100; // 能够进入p_gadamagelist的战损都有效（>0）
  int maxleftpow = -100;
  int maxindex = -1;
  int weapenindex = -1;
  const int wznum = p_gadamagelist->ele_len-3;
  for (int i = 0 ; i < p_gadamagelist->count; i++){
    const float curleftpow = *((float*)ga_getattr(p_gadamagelist, i, 2));
    for (int j = 0 ; j < wznum ; j ++){
      float curdamage = *((float*)ga_getattr(p_gadamagelist, i, j+3));
      if(curdamage > maxdamage || (maxdamage == curdamage && curleftpow > maxleftpow)) {
	maxdamage = curdamage; maxleftpow = curleftpow; maxindex = i; weapenindex=j;
      }
    }
  }
  assert(maxindex >=0);
  assert(maxdamage > -1);
  float *p_maxele = (float*)ga_getele(p_gadamagelist, maxindex);
  p_ele[0] = p_maxele[0];  p_ele[1] = p_maxele[1];  p_ele[2] = p_maxele[2];
  p_ele[3] = weapenindex;
  p_ele[4] = p_maxele[weapenindex+3];

  return maxindex;
}


bool weaponSelectionForAttacker(const struct BasicOperator *p_attacker, const struct BasicOperator *p_obj, float *p_maxvalue, int *p_maxindex)
{
  float *p_wzdamgelist = (float*) malloc(p_attacker->obj_wznum * sizeof(float));
  for(int aw_i = 0 ; aw_i < p_attacker->obj_wznum; aw_i ++){
    p_wzdamgelist[aw_i] = damagelevelP2P(p_attacker, p_obj,aw_i);
  }

  *p_maxvalue = 0; *p_maxindex = 0;
  if (!findmaxfloat(p_wzdamgelist,p_attacker->obj_wznum, p_maxvalue, p_maxindex)){
    // printf("error in weaponSelectionForAttacker(). p_attacker->wznum = %d\n", p_attacker->obj_wznum);
    free(p_wzdamgelist);
    return false;
  }
  free(p_wzdamgelist);
  bool flag_validweapon = (*p_maxvalue) > 0 ? true:false;
  return flag_validweapon;
}

void  damageMapP2P(const struct  BasicOperator *p_attacker, const struct BasicOperator *p_obj, float * p_damagemap)
{
  assert (p_damagemap != NULL);
  struct BasicOperator objcopy = *p_obj;
  // 计算目标算子的机动范围，在目标算子的机动范围内部查找
  struct GA * p_gawicg = ga_init(0, 3, sizeof(int));
  whereICanGoRangeGA(p_obj, p_gawicg);
  const int map_totalcount = MAP_YNUM * MAP_XNUM;
  for(int i = 0 ; i < map_totalcount ; i ++)  p_damagemap[i] = 0.f;

  // 为攻击算子找到有效的攻击范围: 攻击半径（针对无行射能力的算子） / 可视范围（针对有行射能力的算子）
  if (p_attacker->a1 != 0){ // 算子有行射能力, 按照可观察范围进行遍历
    struct dictionary *p_attdicwicg = dic_new(0,sizeof(int));
    whereICanGoRange(p_attacker, p_attdicwicg);
    for (int i = 0; i < p_gawicg->count; i++){
      const int *p_ele = (int*) ga_getele(p_gawicg, i);
      objcopy.obj_pos = cvtOffsetIntLocToInt6( p_ele[0], p_ele[1]);
      struct GA* p_attgadamagelist = ga_init(0, p_attacker->obj_wznum + 3, sizeof(float));
      listdamages( p_attacker, &objcopy, p_attdicwicg, p_attgadamagelist);
      if (p_attgadamagelist->count>0){ // 存在最大战损
	float p_optele[5] = {0};
	optShootingCond(p_attgadamagelist,5, p_optele);
	p_damagemap[p_ele[0] * MAP_XNUM + p_ele[1]] = p_optele[4];
      }
      ga_delete(p_attgadamagelist);
    }
    dic_delete(p_attdicwicg);
  } else { // 算子无行射能力，按照攻击半径进行遍历
    /*
    int max_aim_dis = -1;
    for (int i = 0 ; i < p_attacker->obj_wznum; i++){
      int tmp_aim_dis = getSpecifiedWeaponAttackAim(g_mapattr.dic_wpid2attrs, p_attacker, i, p_obj->obj_type);
      if (tmp_aim_dis > max_aim_dis)
	max_aim_dis = tmp_aim_dis;
    }
    assert (max_aim_dis > 0);
    struct GA *p_gahexsoffset = ga_init(0,1,sizeof(struct HexOfOffset)); // ele_num ele_len attr_bytenum
    const int centor_int4loc = cvtInt6loc2Int4loc(p_attacker->obj_pos);
    const struct HexOfOffset centorhex =  {centor_int4loc / 100, centor_int4loc % 100};
    getHexsInCircleOfOffset(&centorhex, max_aim_dis, p_gahexsoffset);
    float maxvalue = 0; int maxindex = -1;
    for(int i = 0 ; i < p_gahexsoffset->count; i++)
    {
      struct HexOfOffset *p_tmp_hex = (struct HexOfOffset*)ga_getele(p_gahexsoffset, i);
      if (checkHexIsValid(p_tmp_hex)){
	objcopy.obj_pos = cvtOffsetIntLocToInt6(p_tmp_hex->row, p_tmp_hex->col);
	if (weaponSelectionForAttacker(p_attacker, &objcopy, &maxvalue, &maxindex))
  	p_damagemap[p_tmp_hex->row * MAP_XNUM + p_tmp_hex->col] = maxvalue;
      }
      p_tmp_hex= NULL;
    }
    ga_delete(p_gahexsoffset);
   */
    for(int i = 0 ; i < p_gawicg->count; i ++){
      const int *p_ele = (int*) ga_getele(p_gawicg, i);
      objcopy.obj_pos = cvtOffsetIntLocToInt6( p_ele[0], p_ele[1]);
      float maxvalue = 0; int maxindex = -1;
      if (weaponSelectionForAttacker(p_attacker, &objcopy, &maxvalue, &maxindex))
	p_damagemap[p_ele[0] * MAP_XNUM + p_ele[1]] = maxvalue;
    }
  }
  ga_delete(p_gawicg);
  return;
}


void  separateDamageMap(const struct BasicOperator *p_attacker, const struct BasicOperator *p_obj, const int wp_index, float * p_damagemap)
{
  assert (p_attacker != NULL && p_obj != NULL && p_damagemap != NULL);
  if (!attacklevelMap(p_attacker, p_obj, wp_index, p_damagemap))
    return;

  int flag_wz2obj; // 使用哪个战损文件
  const int objective_type = p_obj->obj_type == 1 ? PEOPLE : CAR;
  const bool flag_isltfweapon = getSpecifiedWeaponType(p_attacker, wp_index) == WEAPENTYPE_LTF; 
  if (objective_type == PEOPLE)
    flag_wz2obj = DAMAGELEVEL_ALLW2PEOPLE;
  else
    flag_wz2obj = flag_isltfweapon ? DAMAGELEVEL_ILW2CAR : DAMAGELEVEL_ZM2CAR;

  struct HexOfOffset hex_att = {0,0};
  getLocOfOffsetFromOperator(p_attacker, &(hex_att.row), &(hex_att.col));
  struct BasicOperator bop_obj_cp = *p_obj;
  for(int row = 0 ; row < MAP_YNUM; row ++)
    for(int col = 0; col < MAP_XNUM; col ++)
    {
      int curloc = row * MAP_XNUM + col;
      if (p_damagemap[curloc] == DEFALUT_ZERO) continue; //无效位置
      bop_obj_cp.obj_pos = cvtOffsetIntLocToInt6(row, col);
      if (!iouIsOk(p_attacker, &bop_obj_cp)){ // 攻击算子不能观察到目标算子
	p_damagemap[curloc] = DEFALUT_ZERO;	
      } else {
	int attacklevelvalue = p_damagemap[curloc];
	p_damagemap[curloc] = getDamageLevelP2P(p_attacker, &bop_obj_cp, flag_wz2obj, attacklevelvalue); 
      }
    }
  return ;
}


bool getCandidateScoutlocs(const struct BasicOperator * p_bop, const int dir, const int mindis, const int maxdis, struct GA *p_gahexs)
{
  bool flag = p_bop != NULL && p_gahexs != NULL;
  if (!flag){
    printf("error in getCandidateScoutlocs(): pointers is NULL\n");
    return flag;
  }
  // 按照maxdis计算机动范围
  struct dictionary *p_dicwicg = dic_new(0,sizeof(int));
  whereICanGoRange(p_bop, p_dicwicg);
  // 按照方向和区间计算候选点范围
  const int int4loc = cvtInt6loc2Int4loc(p_bop->obj_pos);
  struct HexOfOffset hex_o = {int4loc/100, int4loc%100};
  getDirHexSet(&hex_o, dir, mindis, maxdis, p_gahexs);
  // 利用机动范围进一步压缩候选点范围
  char p_chars [5] ={'0'};
  for(int i = 0 ; i < p_gahexs->count; i++){
    int * p_tmp_array = (int*) (ga_getele(p_gahexs, i));
    int int4loc = p_tmp_array[0] * 100 + p_tmp_array[1];
    cvtIntLocTo4StrOffLoc(int4loc, p_chars, 5);
    if(!dic_find(p_dicwicg, p_chars, 5)){
      p_tmp_array[2] = -1;
    }else{
      p_tmp_array[2] = ((int*)(p_dicwicg->p_findvalue))[0];
    }
  }
  // 释放资源
  dic_delete(p_dicwicg);
  return flag;
}

int getBestWeaponIndex(const struct BasicOperator *p_attacker,const int tar_type)
{
  const int loc_s = tar_type == 1 ? LOC_WP_DLDATASTART_PEO + MAX_AIMRANGE : LOC_WP_DLDATASTART_CAR;
  int bestindex = 0,maxlevel = 0;
  for(int i=0;i<p_attacker->obj_wznum;i++){
    int weapon_id = p_attacker->p_obj_wpids[i];
    if(!checkWeaponIDandType(g_mapattr.dic_wpid2attrs,weapon_id,tar_type))
      continue;
    char chars_2wpid[3] = {'\0'};
    if(cvtIntLocTo4StrOffLoc(weapon_id, chars_2wpid, 3))
      if(dic_find(g_mapattr.dic_wpid2attrs, chars_2wpid, 3)){
        int attlel = g_mapattr.dic_wpid2attrs->p_findvalue[loc_s];
        if(attlel > maxlevel){
          maxlevel = attlel;
          bestindex = i;
        }
      }
  }
  return bestindex;
}
