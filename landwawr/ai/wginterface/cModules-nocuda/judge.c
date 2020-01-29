#include "judge.h"
// 攻击等级高程修正表（对车）《兵棋推演表3-3》
const int g_zm2car_elerect_table[8][12] = 
{
  {-2,-2,-1,-1,-1,0,0,0,0,0,0,0},
  {-2,-2,-2,-1,-1,-1,-1,0,0,0,0,0},
  {-3,-2,-2,-2,-1,-1,-1,-1,-1,0,0,0},
  {-3,-3,-3,-2,-2,-1,-1,-1,-1,-1,-1,0},
  {-4,-3,-3,-3,-2,-2,-2,-1,-1,-1,-1,-1},
  {-4,-4,-4,-3,-3,-2,-2,-2,-1,-1,-1,-1},
  {-5,-4,-4,-4,-3,-2,-2,-2,-2,-1,-1,-1},
  {-5,-5,-5,-4,-3,-3,-2,-2,-2,-2,-2,-1}
};
// 攻击等级高程修正表（对人）《兵棋推演表3-4》
const int g_zm2soilder_elerect_table[8][10] = 
{
  {-2,-2,-1,-1,-1,0,0,0,0,0},
  {-2,-2,-2,-1,-1,-1,-1,0,0,0},
  {-3,-2,-2,-2,-1,-1,-1,-1,-1,0},
  {-3,-3,-3,-2,-2,-1,-1,-1,-1,-1},
  {-4,-3,-3,-3,-2,-2,-2,-1,-1,-1},
  {-4,-4,-4,-3,-3,-2,-2,-2,-1,-1},
  {-5,-4,-4,-4,-3,-2,-2,-2,-2,-1},
  {-5,-5,-5,-4,-3,-3,-2,-2,-2,-2}
};

// 三张战损毁伤的文件表
float g_p_damagelevel_zm2car[DAMAGELEVEL_DIM_ZM2CAR_HEIGHT * DAMAGELEVEL_DIM_TABLE_SIZE] = {0.0};
float g_p_damagelevel_ltf2car[DAMAGELEVEL_DIM_LTF2CAR_HEIGHT * DAMAGELEVEL_DIM_TABLE_SIZE] = {0.0};
float g_p_damagelevel_allw2people[DAMAGELEVEL_DIM_ALLW2PEOPLE_HEIGHT * DAMAGELEVEL_DIM_TABLE_SIZE] = {0.0};

const int g_int_min = -2147483648;
const int g_int_max = 2147483647;

bool isViewBeInterruptted(const int ele_hexa, const int ele_hexb, const int *p_ele_excluded_onlinehexs , const int len)
{
  int * p_deltaeles = (int *) malloc ( sizeof(int) * len);
  int * p_deltaele_thresholds = (int *) malloc ( sizeof(int) * len);
  assert(p_deltaeles != NULL && p_deltaele_thresholds != NULL);

  bool flag_minmax_order = ele_hexa <= ele_hexb;
  int ele_min = flag_minmax_order ? ele_hexa : ele_hexb;
  int ele_max = flag_minmax_order ? ele_hexb : ele_hexa;
  ele_max += ELEVATION_QUANINTER; // 高高程+1原则
  float ele_diff = ele_max - ele_min;
  const int real_len = len + 2 ;

  // 计算观察线上的高程变化 deletele
  int i = 0 ;
  bool flag_view = false;
  float real_ratio = 0;
  for (i = 0 ; i < len ; i ++)
  {
    real_ratio = flag_minmax_order ? ((float)(i + 1)) / real_len : ((float)(real_len - 1 - i)) / real_len;
    p_deltaeles[i] = p_ele_excluded_onlinehexs[i] -  ele_min;
    p_deltaele_thresholds[i] = ele_diff * real_ratio;
    // if (p_deltaeles[i] > p_deltaele_thresholds[i]) // ***BUG!!!*** 
    if (p_deltaeles[i] >= p_deltaele_thresholds[i])   // 视线刚好被遮挡的情况也许要考虑;
    {
      flag_view = true; // 被遮挡
      break;
    }
  }
  free(p_deltaeles);
  free(p_deltaele_thresholds);
  return flag_view;
}

bool seeStop(const int obj_int4loc, const int tar_int4loc, const int test_int4loc, const int obj_ele, const int tar_ele,  const int test_ele, const int distance) {
  const int EleDiff = abs(obj_ele - tar_ele) / ELEVATION_QUANINTER;
  const int EleLow = (obj_ele > tar_ele) ? tar_ele : obj_ele;

  const struct HexOfOffset test_hex = {test_int4loc/100, test_int4loc%100};
  const struct HexOfOffset tar_hex = {tar_int4loc/100, tar_int4loc%100};
  const int  distanceDiff = getDistanceBetweenHexOfOffset(&test_hex, &tar_hex);

  double h = 15.6; 
  double w = 23.8; 
  double y = h * EleDiff;
  double x = w * distance + 1e-9;
  double hudu = atan(y / x);

  double xx = w * distanceDiff;
  double yy =  abs(round(tan(hudu)*xx)); 
  double yyy = round(((double)(test_ele - EleLow)) / (ELEVATION_QUANINTER) * h);
  return yyy > yy ? false : true;

}

/*
// 原始计算方式
bool icuIsOk(const struct HexOfOffset *p_hexa, const struct HexOfOffset *p_hexb, const int maxdistance)
{

  struct GA *p_gahexsoffset = ga_init(0,1,sizeof(struct HexOfOffset)); // ele_num ele_len attr_bytenum
  getHexsOnLineOfOffset(p_hexa, p_hexb, p_gahexsoffset);
  const int len = p_gahexsoffset->count;
  int ele_hexa = getMyElevation(p_hexa);
  int ele_hexb = getMyElevation(p_hexb);
  // printf("ela = %d, elb = %d, len = %d\n", ele_hexa, ele_hexb, len);
  if (len <= 2 ) // 1为自身,2为相邻
  {
    ga_delete(p_gahexsoffset);
    return true;
  }
  else // 观察线上存在其他六角格
  {
    const int flag_obj_incover = checkHexIsInCover(p_hexb);
    if (flag_obj_incover && (len - 1) > maxdistance / 2)
    {
      ga_delete(p_gahexsoffset);
      return false;
    }
    // 按照遮蔽地形更新观察线上程信息
    int * p_ele_excluded_onlinehexs = (int * ) malloc ((len - 2) * sizeof(int));
    // for (int i = 2  ; i < len - 1; i++) // *!!!BUG!!!* 
    for (int i = 1  ; i < len - 1; i++)    // 修正，i应该从1开始 
    {
      struct HexOfOffset *p_tmp_hex_o = (struct HexOfOffset *)ga_getele(p_gahexsoffset,i);
      p_ele_excluded_onlinehexs[i-1] = getMyElevation(p_tmp_hex_o);
      
      int flag_tmphex_incover = checkHexIsInCover(p_tmp_hex_o);
      if (flag_tmphex_incover) // 此六角格属于遮蔽类型, 在基础高程上+1个高程等级
      {
	p_ele_excluded_onlinehexs[i-1] += ELEVATION_QUANINTER;
	if(flag_obj_incover)	// 遮蔽情形1 : 观察线上与目标均处于遮蔽，不通视
	{
	  ga_delete(p_gahexsoffset);
	  free(p_ele_excluded_onlinehexs);
	  return false;
	}
      }
    //  printf("%d, ",  p_ele_excluded_onlinehexs[i-1]);
    }
    // printf("\n");
    ga_delete(p_gahexsoffset);
    int flag_inter = isViewBeInterruptted(ele_hexa, ele_hexb, p_ele_excluded_onlinehexs, len - 2); //使用高高程+1/比例测量规
    free(p_ele_excluded_onlinehexs);
    return flag_inter? false:true;
  }
}
*/

// 陶伟像素坐标计算方式
bool icuIsOk_com(const struct HexOfOffset *p_hexa, const struct HexOfOffset *p_hexb, const int maxdistance)
{
  const int distance = getDistanceBetweenHexOfOffset(p_hexa, p_hexb);
  if (distance == 0)
    return true;
  // 强制:如果两者之间的距离大于算子的最大可视范围，直接判断为不通视；
  if (distance > maxdistance)
    return false;
  // 如果存在范围地图范围外的六角格，直接不通视
  if (!checkHexIsValid(p_hexb) || !checkHexIsValid(p_hexa)){ 
    // printf("error in icuIsOk(). hexa(%d,%d) or hexb(%d,%d) is invalid\n", p_hexa->row, p_hexa->col, p_hexb->row, p_hexb->col);
    return false;
  }

  //检查是否在地图有效范围内(去除边界)
  if(!checkHexIsInValidRange(p_hexa) || !checkHexIsInValidRange(p_hexb)){
    return false;
  }
  
  int ele_a = getMyElevation(p_hexa);
  int ele_b = getMyElevation(p_hexb);
  int posa_int4loc = p_hexa->row * 100 + p_hexa->col;
  int posb_int4loc = p_hexb->row * 100 + p_hexb->col;
  int obj_int4loc = 0 ;
  int tar_int4loc = 0;
  bool gg = true;
  bool ss = true;
  if(ele_a > ele_b){
    obj_int4loc = posa_int4loc; tar_int4loc = posb_int4loc; gg = true;
  }else if(ele_b > ele_a) {
    obj_int4loc = posb_int4loc; tar_int4loc = posa_int4loc; gg = true;
  }else{
    obj_int4loc = posa_int4loc > posb_int4loc ? posa_int4loc:posb_int4loc;
    tar_int4loc = posa_int4loc > posb_int4loc ? posb_int4loc:posa_int4loc;
    gg = false;
  }

  const struct HexOfOffset obj_hex = {obj_int4loc / 100, obj_int4loc % 100};
  const struct HexOfOffset tar_hex = {tar_int4loc / 100, tar_int4loc % 100};
  int obj_ele = getMyElevation(&obj_hex);
  int tar_ele = getMyElevation(&tar_hex);
  if (gg)
    obj_ele += ELEVATION_QUANINTER;

  double x1 = 0; double y1 = 0;
  double x2 = 0; double y2 = 0;
  assert( getMyPixelLoc(&obj_hex, &y1, &x1));
  assert( getMyPixelLoc(&tar_hex, &y2, &x2));
  double angle = 0;
  const double offset = 0;
  if (x1 >= x2 && y1 < y2){
    angle = round(atan((y1 - y2) / (x1 - x2 + offset)) * 180 / PI + 360);
  }else if (x1 >= x2) {
    angle = round(atan((y1 - y2) / (x1 - x2 + offset)) * 180 / PI);
  } else {
    angle = round(atan((y1 - y2) / (x1 - x2 + offset)) * 180 / PI + 180);
  }

  ss = (angle == 0 || angle == 60 || angle == 120 || angle == 180 || angle == 240 || angle == 300) ? true : false;
  // ss = ((int)(angle)) % 60 == 0 ? true : false;

  int b = y1 + (HEXPIC_HEIGHT / 2);
  int a = x1 + (HEXPIC_WEIGHT / 2);
  float rot = angle - 90;
  float hudu = (2 * PI / 360) * rot;
  int dotnum = ss ? distance : distance * 3;
  int mapid = 0; int mapid2 = 0;  
  // int seestopid = 0;
  for(int i = 1 ; i <= dotnum; i ++){
    int r = 52 * i;
    int rr = ss ? r : round(r * 0.33);
    int X = round(a + sin(hudu) * rr);
    int Y = round(b - cos(hudu) * rr);
    mapid2 = mapid; 
    //printf("Y=%d, X=%d, posa_int4loc = %d, posb_int4loc = %d, distance=%d:", Y,X, posa_int4loc, posb_int4loc, distance);
    mapid = getInt4locFromPixelLoc(Y,X);
    //printf("Y=%d,X=%d,mapid=%d\n",Y,X,mapid);
    int row = mapid / 100; int col = mapid % 100;
    if (mapid != mapid2){
      struct HexOfOffset cur_hex = {row, col};
      if(!checkHexIsValid(&cur_hex)){ // 计算出来的六角格无效,判断为不通视
	 // printf("error in icuIsOk(). hexa(%d,%d) ==> curhex(%d,%d) ==> hexb(%d,%d)\n", p_hexa->row, p_hexa->col, cur_hex.row, cur_hex.col, p_hexb->row, p_hexb->col);
	return false;
      }
      double cur_ele = getMyElevation(&cur_hex);
      if(getMyGridtype(&cur_hex) == 3 || getMyCond(&cur_hex) == 7){
	cur_ele += ELEVATION_QUANINTER;
      }
      if (mapid != obj_int4loc && mapid != tar_int4loc){
	if (seeStop( obj_int4loc, tar_int4loc, mapid, obj_ele, tar_ele, cur_ele, distance) == false){ // 函数seeStop
	  // seestopid = mapid;
	  return false;
	}
      }
      if (mapid == tar_int4loc){
	return true;
      }
    }
  }
  return true;
}


// 查表方式判断通视
bool icuIsOk_cache(const struct HexOfOffset *p_hexa, const struct HexOfOffset *p_hexb, const int maxdistance)
{
  assert(g_mapattr.dic_pairlocs2icudis != NULL);
  const int posa_int4loc = p_hexa->row * 100 + p_hexa->col;
  const int posb_int4loc = p_hexb->row * 100 + p_hexb->col;
  char chars_4pairlocs_af[9] = {'\0'};
  char chars_4pairlocs_bf[9] = {'\0'};
  const int key_af = posa_int4loc * 10000 + posb_int4loc;
  const int key_bf = posb_int4loc * 10000 + posa_int4loc;
  assert (cvtIntLocTo4StrOffLoc(key_af, chars_4pairlocs_af, 9) && cvtIntLocTo4StrOffLoc(key_bf, chars_4pairlocs_bf, 9));
  int dis = maxdistance + 1;
  if ( dic_find(g_mapattr.dic_pairlocs2icudis, chars_4pairlocs_af, 9) || dic_find(g_mapattr.dic_pairlocs2icudis, chars_4pairlocs_bf, 9) )
    dis = ((int*)g_mapattr.dic_pairlocs2icudis->p_findvalue)[0];
  return dis <= maxdistance ? true : false;
  
}

bool icuIsOk(const struct HexOfOffset *p_hexa, const struct HexOfOffset *p_hexb, const int maxdistance)
{
  return g_mapattr.dic_pairlocs2icudis != NULL ? icuIsOk_cache(p_hexa, p_hexb, maxdistance) : icuIsOk_com(p_hexa, p_hexb, maxdistance);
}


bool iouIsOk(const struct BasicOperator *p_bopa, const struct BasicOperator *p_bopb )
{

  struct HexOfOffset hexa = {0,0};
  struct HexOfOffset hexb = {0,0};
  getLocOfOffsetFromOperator(p_bopa, &(hexa.row), &(hexa.col));
  getLocOfOffsetFromOperator(p_bopb, &(hexb.row), &(hexb.col));

  if(!checkHexIsValid(&hexa) || !(checkHexIsValid(&hexb))){
   // printf("error in iouIsOk(). hexa(%d,%d) hexb(%d,%d)\n",hexa.row, hexa.col, hexb.row, hexb.col );
    return false;
  }
  const int maxdistance = p_bopb->obj_type ==  PEOPLE ? MAXIOUDIS_PEOPLE : MAXIOUDIS_CAR;
  const int distance = getDistanceBetweenHexOfOffset(&hexa, &hexb);
  if( icuIsOk(&hexa, &hexb, maxdistance)) // 通视的基础上判断可观察
  { 

    // 目标处于遮蔽地形，观察能力减半
    int distance_threshold = maxdistance; 
    distance_threshold = checkHexIsInCover(&hexb) ? floor(distance_threshold / 2) : distance_threshold;

    // 目标处于掩蔽状态，观察能力减半
    bool flag_inmask = p_bopb->obj_hide > 0 ? true:false; //是否处于掩蔽状态
    if(flag_inmask && p_bopb->obj_type == CAR ){ 
      const int a_ele = getMyElevation(&hexa);
      const int b_ele = getMyElevation(&hexb);
      // 观察者观察目标（车辆），高差大于一个单位高程，掩蔽无效
      flag_inmask = a_ele - b_ele >= ELEVATION_QUANINTER ? false : flag_inmask; 
    }
    distance_threshold = flag_inmask ? floor(distance_threshold / 2) : distance_threshold;

    // 比较实际距离与观察能力
    return distance <= distance_threshold ? true:false; 
  }
  return false;
}

int  getEleAndDisRectValue(const struct HexOfOffset *p_o_hexa, const struct HexOfOffset*p_o_hexb, const int object_type)
{

  if(!checkHexIsValid(p_o_hexa) || !checkHexIsValid(p_o_hexb)){// 如果无效六角格，不进行修正，避免索引错误的数值
    printf("error in getEleAndDisRectValue(). hexa(%d,%d), hexb(%d,%d)\n",
      p_o_hexa->row, p_o_hexa->col, p_o_hexb->row, p_o_hexb->col);
    return 0;
  }
  assert(object_type == CAR || object_type == PEOPLE);

  const int ele_hexa = getMyElevation(p_o_hexa);
  const int ele_hexb = getMyElevation(p_o_hexb);
  if (ele_hexa >= ele_hexb)// 最小高程保证在1个高程等级以及以上
    return 0;
  else
  {
    int ele_diff_level = (ele_hexb - ele_hexa) / ELEVATION_QUANINTER;
    assert(ele_diff_level >= 1);
    ele_diff_level = ele_diff_level > ZM_ELVATIONRECT_ROW ? ZM_ELVATIONRECT_ROW : ele_diff_level;

    int dis_level = getDistanceBetweenHexOfOffset(p_o_hexa, p_o_hexb);
    if (dis_level <= 0)
      return 0; // 最小距离保证在1格以及1格以上
    if(object_type == PEOPLE){
      dis_level = dis_level > ZM_ELVATIONRECT_COL_PEOPLE ? ZM_ELVATIONRECT_COL_PEOPLE : dis_level;
      return g_zm2soilder_elerect_table[ele_diff_level - 1][dis_level - 1];
    } else{ 
      dis_level = dis_level > ZM_ELVATIONRECT_COL_CAR ? ZM_ELVATIONRECT_COL_CAR : dis_level;
      return g_zm2car_elerect_table[ele_diff_level - 1][dis_level - 1];
    }
  }
}


float getDamageLevelP2P( const struct BasicOperator *p_attacker, const struct BasicOperator *p_obj, const int flag_wz2obj,const int attacklevelvalue )
{
  
  if(attacklevelvalue == 0){ // 攻击等级==0时候，战损直接为0
    // printf("攻击等级=0\n");
    return -1;
  }
  else if (attacklevelvalue < 0  || attacklevelvalue > 10) { // 逻辑错误 
    // printf("error in getDamageLevelP2P(), attacklevelvalue = %d\n", attacklevelvalue);
    return -1;
  }

  const int src_blood = p_attacker->obj_blood - 1; 
  const int des_blood = p_obj->obj_blood - 1; 
  const int des_arm_level = p_obj->b0;  // 0 - 4 分别为无装甲、轻、中、重、复合装甲
  if (src_blood < 0 || src_blood >= SRC_MAXBLOOD 
    || des_blood < 0 || des_blood >= DES_MAXBLOOD \
    || des_arm_level < 0 || des_arm_level >= DES_MAXARMLEVEL){
    // printf("error in getDamageLevelP2P(). src_blood, des_blood, des_arm_level = (%d,%d,%d)\n",src_blood, des_blood, des_arm_level);
    return -1;
  }


  float *p_damagetable_data = getCorrepondingDamageLevelTable(flag_wz2obj, src_blood, des_blood, des_arm_level);
  int rectvalue_withoutcond = getRectValueWithoutCond(p_attacker, p_obj);
  assert(rectvalue_withoutcond <= 6 && rectvalue_withoutcond >= -4); 
  rectvalue_withoutcond = rectvalue_withoutcond > 4 ? 4 :  rectvalue_withoutcond; // 保证rectvalue_withoutcond范围[-4,4]

  int rectvalue_final = rectvalue_withoutcond;
  struct HexOfOffset hex = {0,0};
  getLocOfOffsetFromOperator(p_obj, &(hex.row), &(hex.col));
  int flag_cond = getCorrepondingHexFlagCond(&hex);
  assert(flag_cond < 3);
  switch (flag_cond)
  {
    case 0: break;
    case 1: {rectvalue_final = rectvalue_withoutcond - 1; break;} // 居民地-1
    case 2: {rectvalue_final = rectvalue_withoutcond - 2; break;} // 丛林地-2
    //case 3: {rectvalue_final = rectvalue_withoutcond - 1; break;} // 工事六角格-1
  }
  int index_row =  rectvalue_final  + 6; // [-6:4] + 6 = [0:10] 
  int index_col =  attacklevelvalue - 1; // [1-10] - 1 = [0-9] 
  assert (index_row >= 0 && index_row < DAMAGELEVEL_DIM_TABLE_ROW);
  assert (index_col >= 0 && index_col < DAMAGELEVEL_DIM_TABLE_COL);
  return p_damagetable_data[index_row * DAMAGELEVEL_DIM_TABLE_COL + index_col];
}

float*  getCorrepondingDamageLevelTable(const int flag_wz2obj, const int src_blood, const int des_blood, const int des_arm_level)
{
  // 根据flag_wz2obj确定使用哪个战损体以及使用其中的哪张战损表格
  float * p_damagetable_data = NULL;
  switch (flag_wz2obj){
    case DAMAGELEVEL_ZM2CAR:{
      int index_table = src_blood * DES_MAXBLOOD * DES_MAXARMLEVEL + des_blood * DES_MAXARMLEVEL + des_arm_level ;
      assert(index_table < DAMAGELEVEL_DIM_ZM2CAR_HEIGHT && index_table >= 0);
      p_damagetable_data = g_p_damagelevel_zm2car + index_table * DAMAGELEVEL_DIM_TABLE_SIZE;
      break;
    }
    case DAMAGELEVEL_ILW2CAR:{
      int index_table = des_blood * DES_MAXARMLEVEL + des_arm_level;
      assert(index_table < DAMAGELEVEL_DIM_LTF2CAR_HEIGHT && index_table >=0);
      p_damagetable_data = g_p_damagelevel_ltf2car + index_table * DAMAGELEVEL_DIM_TABLE_SIZE;
      break;
    }
    case DAMAGELEVEL_ALLW2PEOPLE:{
      int index_table = des_blood;
      assert( index_table < DAMAGELEVEL_DIM_ALLW2PEOPLE_HEIGHT && index_table >=0);
      p_damagetable_data = g_p_damagelevel_allw2people + index_table * DAMAGELEVEL_DIM_TABLE_SIZE;
      break;
    }
    default: return NULL;
  }
  assert(p_damagetable_data != NULL);
  return p_damagetable_data;
}

int getRectValueWithoutCond(const struct BasicOperator *py_p_bopa, const struct BasicOperator *py_p_bopb)
{
  int rect_value = 0;
  // 射击算子状态
  if (py_p_bopa->obj_keep) //射击算子被压制 -1 
    rect_value -= 1;

  if (py_p_bopa->obj_round){ // 已经机动
    rect_value -= 1;
  }

  // 目标处于堆叠状态，直接+2
  if (py_p_bopa->obj_stack)
    rect_value += 2;

  // 目标算子状态
  if(py_p_bopb->obj_hide) // 目标隐蔽 -2， 如果目标处于掩蔽中，不需要在考虑目标的机动状态
  {
    rect_value -= 2;
    return rect_value;
  }

  if (py_p_bopb->obj_round){
    if (py_p_bopb->obj_type == 2 && py_p_bopb->obj_pass == 1){ // 行军
      rect_value += 4;
    }
    else{
      rect_value -= 2;
    }
  }
  return rect_value; 
}

//int getUsedPower(const struct HexOfOffset * p_hexa, const struct HexOfOffset* p_hexb)
//{
//  const int default_value = -1;
//  if (g_mapattr.dic_pairlocs2pow == NULL){
//    printf("error in getUsedPower(): g_mapattr.dic_pairlocs2pow has not been initized!\n");
//    return default_value;
//  }
//  const int s_int4loc = p_hexa->row * 100 + p_hexa->col;
//  const int e_int4loc = p_hexb->row * 100 + p_hexb->col;
//  char chars_4pairlocs[9]={'\0'};
//  int key = s_int4loc * 10000 + e_int4loc;
//  assert(cvtIntLocTo4StrOffLoc(key, chars_4pairlocs, 9));
//  if (dic_find(g_mapattr.dic_pairlocs2pow, chars_4pairlocs,9)){
//    const int used_power = ((int*)g_mapattr.dic_pairlocs2pow->p_findvalue)[0];
//    return used_power;
//  } else {
//    return default_value;
//  }
//}
