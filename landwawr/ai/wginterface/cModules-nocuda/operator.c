#include "operator.h"



void getLocOfOffsetFromOperator(const struct BasicOperator *py_p_bop, int *p_cur_row , int *p_cur_col)
{
  //assert(py_p_bop->obj_posy == py_p_bop->obj_posx);
  char chars_6_loc[7]={'\0'};
  cvtIntLocTo4StrOffLoc(py_p_bop->obj_pos, chars_6_loc, 7);
  cvtChars6locToOffsetIntLoc(chars_6_loc, p_cur_row, p_cur_col);
  return; 
}

int  checkSpecifiedWeaponBeforeShooting(struct dictionary *p_dic_wptable, const struct BasicOperator *p_attacker, const struct BasicOperator *p_objective, const int weapen_index, const int distance)
{

  if ( weapen_index < 0 || weapen_index >= p_attacker->obj_wznum){
    // printf("error in checkSpecifiedWeaponBeforeShooting(). weapen_index, wznum = (%d,%d)\n", weapen_index, p_attacker->obj_wznum);
    return ERROR_WEAPENCHECK_INDEXOUTOFBOUND;
  }

  // 检查武器类型与目标类型
  assert(p_attacker->p_obj_wpids != NULL);
 
  const int wpid = p_attacker->p_obj_wpids[weapen_index];
  if(!checkWeaponIDandType(p_dic_wptable, wpid , p_objective->obj_type)) // 武器类型与目标类型不匹配
  {
    // printf("wpid = %d, objtype = %d\n", wpid, p_objective->obj_type);
    return ERROR_WEAPENCHECK_TYPEDONOTMATCH;
  }

  // 检查武器射程
  const int valid_shootingrange = getWPAimrange(p_dic_wptable, wpid, p_objective->obj_type);
  if (distance > valid_shootingrange){
    // printf("distance = %d, valid_shootingrange = %d\n", distance, valid_shootingrange);
    return ERROR_WEAPENCHECK_OUTOFSHOOTINGRANGE;
  }

  // 检查子弹，导弹类型的武器检查C3, 非导弹类型的武器使用武器的C2弹药
  if ( (checkWeaponIsDaoDan(wpid) && p_attacker->c3 <= 0) || (!checkWeaponIsDaoDan(wpid) && p_attacker->c2 <= 0) )
    return ERROR_WEAPENCHECK_HAVENOAMMUNITION;

  // 行射能力的算子不能使用导弹？
  if (checkWeaponIsDaoDan(wpid) && p_attacker->a1 != 0){
    return ERROR_WEAPENCHECK_TYPEDONOTMATCH;
  }

  return ERROR_WEAPENCHECK_OK;
}

void updateOperatorLoc(struct BasicOperator *p_bop, const int row, const int col)
{
    int tmpint6locvalue = cvtOffsetIntLocToInt6(row, col);
    p_bop-> obj_pos = tmpint6locvalue;
    return;
}

/*
int getSpecifiedWeaponTartype( struct dictionary *p_dic_wptable, const struct BasicOperator *p_bop, const int i)
{
  assert(i>= 0 && i < p_bop-> obj_wznum);
  const int weapon_id = p_bop->p_obj_wpids[i];
  return getWPObjtype(p_dic_wptable, weapon_id);
}
*/

int getSpecifiedWeaponType(const struct BasicOperator *p_bop, const int i)
{
  assert(p_bop->obj_wznum > i && i >= 0);
  return checkWeaponIsLTF(p_bop->p_obj_wpids[i]) ?  WEAPENTYPE_LTF : WEAPENTYPE_ZM;
}

int getSpecifiedWeaponAttackAim(struct dictionary *p_dic_wptable, const struct BasicOperator *p_bop, const int i, const int tar_type)
{
  assert(i >= 0 && i < p_bop-> obj_wznum);
  assert(tar_type == 1 || tar_type == 2);
  const int weapon_id = p_bop->p_obj_wpids[i];
  if (!checkWeaponIDandType(p_dic_wptable, weapon_id, tar_type))
    return -1;
  return getWPAimrange(p_dic_wptable, weapon_id, tar_type);
}

int* getSpecifiedWeaponAttackLevelData(struct dictionary *p_dic_wptable, const struct BasicOperator *p_bop, const int i, const int tar_type )
{
  assert(i >= 0 && i < p_bop->obj_wznum);
  assert(tar_type == 1 || tar_type == 2);
  const int weapon_id = p_bop->p_obj_wpids[i];
  if (!checkWeaponIDandType(p_dic_wptable, weapon_id, tar_type)){
    return NULL;
  }
  return getDLStartDataPointer(p_dic_wptable, p_bop->obj_blood, weapon_id, tar_type);
}


