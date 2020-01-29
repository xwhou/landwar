#include "weapen.h"
// 全局变量，能够攻击指定类型算子的武器ID列表
const  int people_ids[NUM_PEOPLE_WEAPONS] = {29,43,36,37,54, 56};
const  int car_ids[NUM_CAR_WEAPONS] = {35,36,37,54,56,69,71};
const int daodan_ids[NUM_DAODAN_WEAPONS] = {69,71};


int * getSpecifiedDataPointeFromWPTable(struct dictionary *p_dic_wptable, const int int2_wpid, const int index_start, const int index_end)
{
  if( p_dic_wptable == NULL || index_start < 0 || index_end <= index_start || index_end > WIDTH_WPTABLE ){
    printf("error in getSpecifiedDataFromWPTable(). (start, end) =  (%d,%d)\n", index_start, index_end );
    return NULL;
  }

  char chars_2wpid[3] = {'\0'};
  if(cvtIntLocTo4StrOffLoc(int2_wpid, chars_2wpid, 3))
    if(dic_find(p_dic_wptable, chars_2wpid, 3))
      return (int*)(p_dic_wptable->p_findvalue) + index_start;
  
  printf("error in getSpecifiedDataFromWPTable(). wpid = %d\n", int2_wpid );
  return NULL;
}

int getSpecifiedColDataFromWPTable(struct dictionary *p_dic_wptable, const int wpid, const int index_col)
{
  const int *p_data = getSpecifiedDataPointeFromWPTable(p_dic_wptable, wpid, index_col, index_col+1);
  return p_data ? p_data[0] : -1;
}

int getWPObjtype(struct dictionary *p_dic_wptable, const int wpid)
{
  return getSpecifiedColDataFromWPTable(p_dic_wptable, wpid, LOC_WP_OBJTYPE);
}


int getWPAimrange(struct dictionary *p_dic_wptable, const int wpid , const int tar_type)
{
  const int obj_type = getWPObjtype(p_dic_wptable, wpid);
  assert(obj_type == 0 || obj_type == tar_type);
  const int index_col = tar_type == 1 ? LOC_WP_AIMRANGE_PEO : LOC_WP_AIMRANGE_CAR;
  return getSpecifiedColDataFromWPTable(p_dic_wptable, wpid , index_col);
}

int * getDLStartDataPointer(struct dictionary *p_dic_wptable, const int blood_att, const int wpid, const int tar_type)
{ 
  // 验证tar_type 
  const int obj_type = getWPObjtype(p_dic_wptable, wpid);
  assert (obj_type == 0 || obj_type == tar_type);
  // 验证aimrange 
  const int aimrange = getWPAimrange(p_dic_wptable, wpid, tar_type);
  assert(aimrange > 0 && aimrange < MAX_AIMRANGE);

  // 验证血量
  assert (blood_att > 0 && blood_att <= MAX_OBJNUM);
  const int loc_s = tar_type == 1 ? LOC_WP_DLDATASTART_PEO + (blood_att - 1) * MAX_AIMRANGE : LOC_WP_DLDATASTART_CAR;
  const int loc_e = loc_s + MAX_AIMRANGE;
  return getSpecifiedDataPointeFromWPTable(p_dic_wptable, wpid, loc_s, loc_e);
}


bool checkWeaponIDandType(struct dictionary *p_dic_wptable , const int wpid, const int tar_type)
{
  bool flag_valid_0 = false; // 基于武器属性表进行检查
  const int obj_type = getWPObjtype(p_dic_wptable, wpid);
  flag_valid_0 = (obj_type == 0 || obj_type == tar_type); 
  
  bool flag_valid_1 = false;   // 基于全局变量进行检查
  const int* p_type_ids = tar_type == 1 ? people_ids : car_ids;
  const int num_type_ids = tar_type == 1 ? NUM_PEOPLE_WEAPONS : NUM_CAR_WEAPONS;
  for(int i = 0 ; i < num_type_ids; i++){
    if(wpid == p_type_ids[i]){
      flag_valid_1 = true;
      break;
    }
  }
  return (flag_valid_1 && flag_valid_0);
}


bool checkWeaponIsDaoDan(const int weaponid){
  bool flag_isdd = false;
  for (int i = 0 ; i < NUM_DAODAN_WEAPONS; i++){
    if(weaponid == daodan_ids[i]){
      flag_isdd = true;
      break;
    }
  }
  return flag_isdd;
}

bool checkWeaponIsLTF(const int weaponid){
  return weaponid == 29 || weaponid == 43 ? true : false;
}






