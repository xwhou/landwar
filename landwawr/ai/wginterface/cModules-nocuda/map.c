#include "map.h"

/* 全局变量定义 */
struct Map_Attr g_mapattr= {NULL, NULL, NULL, NULL, NULL, NULL, NULL};
struct Map_Stage g_mapstage = {NULL};

void initMapAttr(int *p_geodata, int *p_epdata, int *p_roadnet, int *p_wptable, const int georows, const int geocols, const int eprows, const int epcols, const int rnetrows, const int rnetcols, const int wprows, const int wpcols)
{
  // Map_Attr 部分
  assert(geocols == (COLNUM_GEOMAT + 1)  || geocols == (COLNUM_GEOMAT - 2 + 1));
  assert(epcols == (COLNUM_EPMAT + 1) && rnetcols == (COLNUM_ROADNETMAT + 1) && wpcols == (COLNUM_WPTABLE + 1));

  const int geo_valuebytenum = sizeof(int) * (COLNUM_GEOMAT);
  const int ep_valuebytenum = sizeof(int) * (COLNUM_EPMAT);
  const int rnet_valuebytenum = sizeof(int) * (COLNUM_ROADNETMAT);
  const int wp_valuebytenum = sizeof(int) * (COLNUM_WPTABLE);

  g_mapattr.dic_loc2geodata = dic_new(0, geo_valuebytenum);
  g_mapattr.dic_loc2epdata = dic_new(0, ep_valuebytenum);
  g_mapattr.dic_loc2roadnet = dic_new(0, rnet_valuebytenum);
  g_mapattr.dic_wpid2attrs = dic_new(0, wp_valuebytenum);

  if(g_mapattr.dic_loc2geodata == NULL || g_mapattr.dic_loc2epdata == NULL || g_mapattr.dic_loc2roadnet == NULL || g_mapattr.dic_wpid2attrs == NULL){
    printf("error in initMapAttr() function in c. pointer is null\n");
    freeMapAttr();
    return;
  }
  
  // 地图 
  char chars_4loc[5]= {'\0'};
  for(int i = 0; i < georows; i++){
    const int cur_int4loc = p_geodata[i * geocols];
    if (cvtIntLocTo4StrOffLoc( cur_int4loc, chars_4loc, 5)){
      if (geocols == (COLNUM_GEOMAT + 1)) { // 输入数据完整，有7列（包含像素坐标XY），直接拷贝
	dic_add(g_mapattr.dic_loc2geodata, chars_4loc, p_geodata + i*geocols + 1, 5, geo_valuebytenum);
      }else{ // 输入数据5列，不包含XY，需要自己计算
	int p_fulldarr[COLNUM_GEOMAT] = {0};
	memcpy(p_fulldarr, p_geodata + i*geocols + 1, sizeof(int) * (geocols - 1));
	p_fulldarr[PIXELROWLOC] = HexHalfRowHeight*(floor(cur_int4loc / 100));
	p_fulldarr[PIXELCOLLOC] = HexRowWidth * (cur_int4loc%100) + HexHalfWidth*(((int)floor(cur_int4loc/100)+1)%2==0 ? 1 : 0);
	dic_add(g_mapattr.dic_loc2geodata, chars_4loc, p_fulldarr, 5, geo_valuebytenum);
      }
    }else{
      printf("error in initMapAttr(): fail to cvtIntLocTo4StrOffLoc(). cur_int4loc = %d\n", cur_int4loc);
      freeMapAttr();
      return;
    }
  }

  // 单边机动力消耗
  for (int i = 0 ; i < eprows; i ++)
    if (cvtIntLocTo4StrOffLoc( p_epdata[i * epcols], chars_4loc, 5))
      dic_add(g_mapattr.dic_loc2epdata, chars_4loc, p_epdata + i*epcols + 1, 5, ep_valuebytenum);
    else{
      printf("error in initMapAttr(): fail to cvtIntLocTo4StrOffLoc(). cur_int4loc = %d\n", p_epdata[i * epcols]);
      freeMapAttr();
      return;
    }

  // 道路网
  for (int i = 0 ; i < rnetrows; i++)
    if (cvtIntLocTo4StrOffLoc(p_roadnet[i * rnetcols], chars_4loc, 5))
      dic_add(g_mapattr.dic_loc2roadnet, chars_4loc, p_roadnet + i * rnetcols + 1, 5, rnet_valuebytenum);
    else{
      printf("error in initMapAttr(): fail to cvtIntLocTo4StrOffLoc(). cur_int4loc = %d\n", p_roadnet[i * rnetcols]);
      freeMapAttr();
      return;
    }

  // 武器属性
  char chars_2wpid[3]  = {'\0'};
  for (int i = 0 ; i < wprows; i ++){
    if (cvtIntLocTo4StrOffLoc(p_wptable[i * wpcols], chars_2wpid, 3)){
      dic_add(g_mapattr.dic_wpid2attrs, chars_2wpid, p_wptable + i * wpcols + 1, 3, wp_valuebytenum);
    } else {
      printf("error in initMapAttr(): fail to cvtIntLocTo4StrOffLoc(). cur_int4loc = %d\n", p_wptable[i * wpcols]);
      freeMapAttr();
      return;
    }
  }

  // Map_Stage部分
  g_mapstage.p_sawcount_map = (int*) malloc (MAP_XNUM * MAP_YNUM * sizeof(int));
  memset(g_mapstage.p_sawcount_map, 0, sizeof(int) * MAP_YNUM * MAP_XNUM); // *BUG* （memset 设置数值前N个字节）
  if (g_mapstage.p_sawcount_map == NULL){
    printf("error in initMapAttr() function in c. pointer is null(g_mapstage.p_sawcount_map)\n");
    freeMapAttr();
    return;
  }
  return;
}

void initIcuCacheData(const int * p_1d_icudata, const int len)
{
  if (p_1d_icudata == NULL){
    printf("error in initIcuCacheData():p_1d_icudata == NULL\n");
    freeMapAttr();
    return;
  }
  g_mapattr.dic_pairlocs2icudis = dic_new(0, sizeof(int));
  char chars_4pairlocs[9]= {'\0'};
  for(int i = 0 ; i < len; i++){
    int key = p_1d_icudata[i] / 10;
    int posa_int4loc = key / 10000;
    int posb_int4loc = key % 10000;
    struct HexOfOffset hex_a = {posa_int4loc/100, posa_int4loc%100};
    struct HexOfOffset hex_b = {posb_int4loc/100, posb_int4loc%100};
    int dis = getDistanceBetweenHexOfOffset(&hex_a,&hex_b);
    // key['posa_int4loc*10000 + posb_int4loc'] ==> value [dis]
    if (cvtIntLocTo4StrOffLoc(key, chars_4pairlocs, 9)){
      dic_add(g_mapattr.dic_pairlocs2icudis, chars_4pairlocs, &dis, 9, sizeof(int));
    }else{
      printf("error in initIcuCacheData() function in c: failed to cvtIntLocTo4StrOffLoc\n");
      freeMapAttr();
      return;
    }
  }
}

void initWicgCacheData(const long long *p_1d_wicgdata, const int len)
{
  if(p_1d_wicgdata == NULL){
    printf("error in initWicgCacheData():p_1d_wicgdata == NULL\n");
    freeMapAttr();
    return;
  }

  g_mapattr.dic_pairlocs2pow = dic_new(0, sizeof(int));
  char chars_4pairlocs[9]= {'\0'};
  for(int i = 0 ; i < len; i++){
    int key = p_1d_wicgdata[i] / 100;
    int value = p_1d_wicgdata[i] % 100;
    // key['posa_int4loc*10000 + posb_int4loc'] ==> value [used_power == value]
    if (cvtIntLocTo4StrOffLoc(key, chars_4pairlocs, 9)){
      dic_add(g_mapattr.dic_pairlocs2pow, chars_4pairlocs, &value, 9, sizeof(int));
    }else{
      printf("error in initWicgCacheData() function in c: failed to cvtIntLocTo4StrOffLoc\n");
      freeMapAttr();
      return;
    }
  }

}

void intiDisCacheData(const long long * p_1d_disdata, const int len)
{  

  if(p_1d_disdata == NULL){
    printf("error in intiDisCacheData():p_1d_disdata == NULL\n");
    freeMapAttr();
    return;
  }
 
  g_mapattr.dic_pairlocs2dis = dic_new(0, sizeof(int));
  char chars_4pairlocs[9]= {'\0'};
  for(int i = 0 ; i < len; i++){
    int key = p_1d_disdata[i] / 100;
    int value = p_1d_disdata[i] % 100;
    // key['posa_int4loc*10000 + posb_int4loc'] ==> value [used_power == value]
    if (cvtIntLocTo4StrOffLoc(key, chars_4pairlocs, 9)){
      dic_add(g_mapattr.dic_pairlocs2dis, chars_4pairlocs, &value, 9, sizeof(int));
    }else{
      printf("error in initWicgCacheData() function in c: failed to cvtIntLocTo4StrOffLoc\n");
      freeMapAttr();
      return;
    }
  }
  return;
}

void freeMapAttr()
{
  // 地图数据
  if (g_mapattr.dic_loc2epdata != NULL){
    dic_delete(g_mapattr.dic_loc2epdata);
    g_mapattr.dic_loc2epdata = NULL;
  }

  if (g_mapattr.dic_loc2geodata != NULL){
    dic_delete(g_mapattr.dic_loc2geodata);
    g_mapattr.dic_loc2geodata = NULL;
  }

  if (g_mapattr.dic_loc2roadnet != NULL){
    dic_delete(g_mapattr.dic_loc2roadnet);
    g_mapattr.dic_loc2roadnet = NULL;
  }

  if (g_mapattr.dic_wpid2attrs != NULL){
    dic_delete(g_mapattr.dic_wpid2attrs);
    g_mapattr.dic_wpid2attrs = NULL;
  }

  // 缓存数据：通视信息
  if(g_mapattr.dic_pairlocs2icudis != NULL){
    dic_delete(g_mapattr.dic_pairlocs2icudis);
    g_mapattr.dic_pairlocs2icudis = NULL;
  }
  // 缓存数据：机动范围信息
  if(g_mapattr.dic_pairlocs2pow != NULL){
    dic_delete(g_mapattr.dic_pairlocs2pow);
    g_mapattr.dic_pairlocs2pow = NULL;
  }
  // 缓存数据：距离信息
  if(g_mapattr.dic_pairlocs2dis != NULL){
    dic_delete(g_mapattr.dic_pairlocs2dis);
    g_mapattr.dic_pairlocs2dis = NULL;
  }

  // 被发现地图
  if(g_mapstage.p_sawcount_map != NULL){
    free(g_mapstage.p_sawcount_map);
    g_mapstage.p_sawcount_map = NULL;
  }


  return;
}

int getMySpecifiedColDataFromGMapAttr(const struct HexOfOffset* p_hex, const int col)
{
  if ( col >= COLNUM_GEOMAT || col < 0){//索引的列超过范围
    printf("error in getMySpecifiedColDataFromGMapAttr() in map.c col[0,5] = %d\n", col);
    return -1;
  }

  int tmp_int_loc = p_hex->row * 100 + p_hex->col;
  char chars_loc[5] = {'\0'};
  cvtIntLocTo4StrOffLoc(tmp_int_loc, chars_loc, 5);
  assert(dic_find( g_mapattr.dic_loc2geodata, chars_loc, 5));
  return ((int*)g_mapattr.dic_loc2geodata->p_findvalue)[col];
}

int getMyElevation(const struct HexOfOffset *p_hex)
{ 
  if (!checkHexIsValid(p_hex)){
    printf("error in getMyElevation() in map.c invalid hex (%d,%d)\n", p_hex->row, p_hex->col);
    return -1;
  }
  return getMySpecifiedColDataFromGMapAttr(p_hex, ELEVATIONLOC);
} 

int getMyGridtype(const struct HexOfOffset *p_hex)
{
  if (!checkHexIsValid(p_hex)){
    printf("error in getMyGridtype() in map.c invalid hex (%d,%d)\n", p_hex->row, p_hex->col);
    return -1;
  }
  return getMySpecifiedColDataFromGMapAttr(p_hex, GRIDTYPELOC);
}

int getMyCond(const struct HexOfOffset *p_hex)
{
 if (!checkHexIsValid(p_hex)){
    printf("error in getMyCond() in map.c invalid hex (%d,%d)\n", p_hex->row, p_hex->col);
    return -1;
  }
  return getMySpecifiedColDataFromGMapAttr(p_hex, CONDLOC);
}

int getMyHexNum(const struct HexOfOffset *p_hex)
{

  if (!checkHexIsValid(p_hex)){
    printf("error in getMyHexNum() in map.c invalid hex (%d,%d)\n", p_hex->row, p_hex->col);
    return -1;
  }
  return getMySpecifiedColDataFromGMapAttr(p_hex, GRIDIDLOC);
}

bool getMyPixelLoc(const struct HexOfOffset *p_hex, double *y, double *x)
{
  if (!checkHexIsValid(p_hex)){
    printf("error in getMyPixelLoc() in map.c invalid hex (%d,%d)\n", p_hex->row, p_hex->col);
    *y = 0;
    *x = 0;
    return false;
  }else{
    *y = (double)(getMySpecifiedColDataFromGMapAttr(p_hex, PIXELROWLOC));
    *x = (double)(getMySpecifiedColDataFromGMapAttr(p_hex, PIXELCOLLOC));
    return true;
  }
}

int getDistanceBetweenHexOfOffset(const struct HexOfOffset *p_o_hexa , const struct HexOfOffset *p_o_hexb)
{
    /*
    int dis = -1;
    int posa_int4loc = p_o_hexa->row * 100 + p_o_hexa->col;
    int posb_int4loc = p_o_hexb->row * 100 + p_o_hexb->col;
    char chars_4pairlocs_af[9] = {'\0'};
    char chars_4pairlocs_bf[9] = {'\0'};
    const int key_af = posa_int4loc * 10000 + posb_int4loc;
    const int key_bf = posb_int4loc * 10000 + posa_int4loc;
    assert (cvtIntLocTo4StrOffLoc(key_af, chars_4pairlocs_af, 9) && cvtIntLocTo4StrOffLoc(key_bf, chars_4pairlocs_bf, 9));
    // 先查表
    if (g_mapattr.dic_pairlocs2dis != NULL){
      if ( dic_find(g_mapattr.dic_pairlocs2dis, chars_4pairlocs_af, 9) || dic_find(g_mapattr.dic_pairlocs2dis, chars_4pairlocs_bf, 9) )
	dis = ((int*)g_mapattr.dic_pairlocs2dis->p_findvalue)[0];
    }
    // 计算
    if (dis < 0){
      dis = getDistanceBetweenHexOfOffset_com(p_o_hexa, p_o_hexb);
      if (g_mapattr.dic_pairlocs2dis != NULL) // 存在缓存数据，但是缓存数据中没有该位置对，即时更新
	dic_add(g_mapattr.dic_pairlocs2dis, chars_4pairlocs_af, &dis, 9, sizeof(int));
    }
    assert(dis >= 0);
    */
    int dis = getDistanceBetweenHexOfOffset_com(p_o_hexa, p_o_hexb);
    assert(dis >= 0);
    return dis;
}

int getRoadTypeBetweenHex(const struct HexOfOffset *p_hexa, const struct HexOfOffset *p_hexb)
{ 
  if(getDistanceBetweenHexOfOffset(p_hexa, p_hexb) != 1){
    printf("error in getRoadTypeBetweenHex(), distance for (%d,%d) and (%d,%d)!= 1.\n", \
      p_hexa->row, p_hexa->col, p_hexb->row, p_hexb->col);
    return -1;
  }
  char a_chars4loc[5]={'\0'};
  char b_chars4loc[5]={'\0'};
  int a_int4loc = p_hexa->row * 100 + p_hexa->col;
  int b_int4loc = p_hexb->row * 100 + p_hexb->col;
  cvtIntLocTo4StrOffLoc(a_int4loc, a_chars4loc, 5);
  cvtIntLocTo4StrOffLoc(b_int4loc, b_chars4loc, 5);

  assert(dic_find(g_mapattr.dic_loc2roadnet, a_chars4loc,5));
  int num_edges = ((int*)g_mapattr.dic_loc2roadnet->p_findvalue)[0];
  int type_a = -1;
  for (int i = 0 ; i < num_edges; i++){ // 遍历周围的六角格
    const int tmp_int4loc = ((int*)g_mapattr.dic_loc2roadnet->p_findvalue)[1 + i * 2]; // [2 + i * 2 ]为道路类型，扩展模块
    if (tmp_int4loc == b_int4loc){
      type_a = ((int*)g_mapattr.dic_loc2roadnet->p_findvalue)[1 + i * 2 + 1];
      break;
    }
  }

  assert(dic_find(g_mapattr.dic_loc2roadnet, b_chars4loc,5));
  num_edges = ((int*)g_mapattr.dic_loc2roadnet->p_findvalue)[0];
  int type_b = -1;
  for (int i = 0 ; i < num_edges; i++){ // 遍历周围的六角格
    const int tmp_int4loc = ((int*)g_mapattr.dic_loc2roadnet->p_findvalue)[1 + i * 2]; // [2 + i * 2 ]为道路类型，扩展模块
    if (tmp_int4loc == a_int4loc){
      type_b = ((int*)g_mapattr.dic_loc2roadnet->p_findvalue)[1 + i * 2 + 1];
      break;
    }
  }

  if (type_a == type_b && type_a >= 0) 
    return type_a;
  else {
    printf("hexa(%d,%d) type_a(%d) != hexb(%d,%d) type_b(%d)\n", \
      p_hexa->row, p_hexa->col,type_a, p_hexb->row , p_hexb->col, type_b);
    return -1;
  }
}

bool checkHexIsValid(const struct HexOfOffset *p_hex_o)
{
  if (p_hex_o->row >= MAP_YMIN
      && p_hex_o->row < MAP_YMAX
      && p_hex_o->col >= MAP_XMIN
      && p_hex_o->col < MAP_XMAX)
      return true;
  else
    return false;
}

bool checkHexIsInValidRange(const struct HexOfOffset *p_hex_o)
{
  if (p_hex_o->row >= BOARDER_WIDTH
      && p_hex_o->row < MAP_YMAX - BOARDER_WIDTH
      && p_hex_o->col >= BOARDER_WIDTH
      && p_hex_o->col < MAP_XMAX - BOARDER_WIDTH)
      return true;
  else
    return false;
}

bool checkHexIsInCover(const struct HexOfOffset *p_hex_o)
{
  const int gridtype_ = getMyGridtype(p_hex_o); // 外部判断p_hex_o 是否有效
  if (gridtype_ == 3 || (gridtype_ == 2 && getMyCond(p_hex_o) == 7))
    return true;
  else
    return false;
}

bool checkHexIsRoad(const struct HexOfOffset *p_hex)
{
  assert(checkHexIsValid(p_hex));
  const int gridtype = getMyGridtype(p_hex);
  return 2 == gridtype ? true:false;
}

int getCorrepondingHexFlagCond(const struct HexOfOffset *p_hex)
{ 
  int flag = 0;
  const int gridtype_ = getMyGridtype(p_hex);
  if (gridtype_ == 3) // 遮蔽地形 conver
  {
    const int hexNum = getMyHexNum(p_hex);
    if (hexNum != 51 && hexNum != 52){
      printf("hexNum = %d\n", hexNum);
    }
    // assert(hexNum == 51 || hexNum == 52); // 51居民地==> 1 / 52丛林 ==> 2
    flag = hexNum == 51 ? 1 : 2;
  }
  if (gridtype_ == 2 && getMyCond(p_hex) == 7) // 有道路的居民地类型
    flag = 1;
  return flag;

}

int getEnterHexNeededPower(const int int_loc, const int direction_flag)
{
  char chars_4loc[5];
  cvtIntLocTo4StrOffLoc(int_loc, chars_4loc, 5);
  if (dic_find(g_mapattr.dic_loc2epdata, chars_4loc, 5))
  {
    const int real_direction = g_dir_map[direction_flag]; // 方向映射 012345=>345012
    return ((int*)g_mapattr.dic_loc2epdata->p_findvalue)[real_direction];
  }
  else
    return 1;
}



bool getNeighRoadHex(const struct HexOfOffset *p_objhex, const int dis_threshold, struct HexOfOffset *p_neighhex)
{
  assert(checkHexIsValid(p_objhex));
  assert(dis_threshold >= 0);
  bool flag_findneigh = false;

  for (int radias = 0 ; radias < dis_threshold ; radias ++){
    if(!flag_findneigh){
      struct GA *p_gahexsoffset = ga_init(0,1,sizeof(struct HexOfOffset)); // ele_num ele_len attr_bytenum
      getHexsOnRingOfOffset(p_objhex, radias, p_gahexsoffset);
      for(int i = 0 ; i < p_gahexsoffset->count ; i++){
	struct HexOfOffset *p_tmphex = (struct HexOfOffset*)ga_getele(p_gahexsoffset, i);
	if (checkHexIsRoad(p_tmphex)){
	  flag_findneigh = true;
	  p_neighhex->row = p_tmphex->row;
	  p_neighhex->col = p_tmphex->col;
	  break;
	}
      }
      ga_delete(p_gahexsoffset);
    }
  }
  return flag_findneigh;
}

int getInt4locFromPixelLoc(int pixel_row, int pixel_col)
{
    // printf("prow = %d, pcol = %d\n", pixel_row, pixel_col);
    const int y = pixel_row;
    const int x = pixel_col; 

    int MapID = 0;
    double xxx = x - 3; 
    double yyy = y - 5; 
    double Y = floor(FirstID / 10000); 
    double X = floor(FirstID) - Y * 10000;

    int YID = (y >= 0) ? floor(floor( yyy / HexRowHeight ) + Y) * 10000 : floor(Y - abs(floor(yyy / HexRowHeight)) - 1) * 10000;
    int XID0 = (x >= 0) ? floor(xxx / HexRowWidth) * 2 + X : X - abs(floor(xxx / HexRowWidth) * 2) - 2;
    int XID1 = (x >= 0) ? floor((floor(xxx) + HexHalfWidth) / HexRowWidth) * 2 + X : X - abs(floor((floor(xxx) + HexHalfWidth) /HexRowWidth ) * 2) - 2;

    if (y >= 0) {
      if (FirstID % 2 == 0) {
	if ( (int)floor( yyy / HexHalfRowHeight) % 2 == 0) 
	  MapID = YID + XID0;
	else {
	  MapID = YID + XID1;
	  MapID = floor(MapID - 1);
	}
      } else {
	if ((int) floor(yyy / HexHalfRowHeight) % 2 == 0) {
	  MapID = YID + XID0;
	} else {
	  MapID = YID + XID1;
	  MapID = floor(MapID + 10000 - 1);
	}
      }
    } else {
      if (FirstID % 2 == 0) {
	if ((int)floor( yyy / HexHalfRowHeight) % 2 == 0) {
	  MapID = YID + XID1;
	  MapID = floor(MapID - 1);
	} else { 
	  MapID = YID + XID0;
	}
      } else {
	if ((int)floor(yyy / HexHalfRowHeight) % 2 == 0) {
	  MapID = YID + XID1;
	  MapID = floor(MapID + 10000 - 1);
	} else { 
	  MapID = YID + XID0;
	}
      }
    }

    if (MapID < 0) {
        printf("error in getInt4locFromPixelLoc(). MapID, pixel_row, pixel_col = (%d,%d,%d)\n",
	 MapID, pixel_row, pixel_col);
	return 0;
    }

    const int return_int4loc = cvtInt6loc2Int4loc(MapID);
    const struct HexOfOffset hex = {return_int4loc / 100 , return_int4loc % 100};
    if(!checkHexIsValid(&hex))
      printf("error in getInt4locFromPixelLoc(), (%d,%d)\n", hex.row, hex.col);
    return return_int4loc;
}


bool getDirHexSet(const struct HexOfOffset *p_o_hex, const int dir, const int mindis, const int maxdis, struct GA * p_gahexs)
{
  bool flag = p_o_hex != NULL && dir >= 0 && dir <= 5 && mindis > 0 && mindis <= maxdis && p_gahexs != NULL;
  if (!flag){
    printf("error in getDirHexSet() in hex.c\n");
    return flag;
  }
  // 计算偏移向量（立方坐标下）
  struct GA * p_gaoffvecs = ga_init(0, 3, sizeof(int));
  if (!getDirOffVectorSet(dir, mindis, maxdis, p_gaoffvecs)){
    printf("error in getDirHexSet(): getDirOffVectorSet() return false\n");
    ga_delete(p_gaoffvecs);
    return false;
  }
  // 坐标转换和存储
  struct HexOfCude hex_c = {0,0,0};
  struct HexOfOffset hex_add_o = {0,0};
  cvtHexFromOffsetToCube(p_o_hex, &hex_c);
  for (int i = 0 ; i < p_gaoffvecs->count; i++){
    const int *p_tmp_offvec = (int*)(ga_getele(p_gaoffvecs,i));
    struct HexOfCude hex_add_c = {hex_c.q + p_tmp_offvec[0],
				  hex_c.r + p_tmp_offvec[1],
				  hex_c.s + p_tmp_offvec[2]};
    cvtHexFromCubeToOffset(&hex_add_c, &hex_add_o);
    // 检查当前候选点是否有效
    if (checkHexIsValid(&hex_add_o)){
      int p_tmp_result[3] ={hex_add_o.row, hex_add_o.col, 1};
      ga_appendele(p_gahexs, p_tmp_result, 3 ,sizeof(int));
    }
  }
  ga_delete(p_gaoffvecs);
  return flag;
}
