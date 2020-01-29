#include "strategy.h"


void getFFBTRoutes1010(const struct BasicOperator *p_attacker,const struct BasicOperator *p_obj,const float * p_uniondamage_map,  struct GA *p_gaffbtroutes)
{  
  if (p_uniondamage_map == NULL || p_attacker->a1 == 0 || p_obj->a1 == 0){ 
    printf("error in getFFBTRoutes1010()\n");
    return;
  } 
  struct BasicOperator attcopy = *p_attacker;
  struct BasicOperator objcopy = *p_obj;
  objcopy.obj_step = objcopy.obj_stepmax; // 对方算子是下阶段攻击，因此机动力需要置满

  struct GA *p_attgawicg = ga_init(0,3,sizeof(int));
  whereICanGoRangeGA(p_attacker, p_attgawicg);
  struct dictionary *p_objdicwicg = dic_new(0,sizeof(int));
  whereICanGoRange(&objcopy, p_objdicwicg);
  struct dictionary *p_x2dict = dic_new(0, sizeof(int));// .h中的注意事项
  char chars_4loc_blood[6]={'\0'};
  float p_ffbtroute[FFBTMODE_ELELEN]={0};
  int init_row = 0;
  int init_col = 0;
  getLocOfOffsetFromOperator(p_attacker, &init_row, &init_col);
  p_ffbtroute[FFBTMODE_INITLOC_ROW_A] = init_row;
  p_ffbtroute[FFBTMODE_INITLOC_COL_A] = init_col;

  float maxvalue = 0; int maxindex = 0;
  for(int xstar_i = 0 ; xstar_i < p_attgawicg->count ; xstar_i++){
    int shooting_a = 0; 
    int *p_attele = (int*) ga_getele(p_attgawicg, xstar_i);
    p_ffbtroute[FFBTMODE_SHOOTING_ROW_A] = p_attele[0];
    p_ffbtroute[FFBTMODE_SHOOTING_COL_A] = p_attele[1];
    p_ffbtroute[FFBTMODE_SHOOTING_LEFTPOWER_A] = p_attele[2];
    p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_A] = 0;
    p_ffbtroute[FFBTMODE_WEAPENINDEX_A] = -1;
    updateOperatorLoc(&attcopy, p_attele[0], p_attele[1]);
    if (weaponSelectionForAttacker(&attcopy, p_obj, &maxvalue, &maxindex)){
      shooting_a = 1; //攻击算子有战损
      p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_A] = maxvalue * p_obj->obj_value;
      p_ffbtroute[FFBTMODE_WEAPENINDEX_A] = maxindex;
      objcopy.obj_blood = p_obj->obj_blood; // 重置血量为初始状态
      objcopy.obj_blood = objcopy.obj_blood - maxvalue > 0 ? round(objcopy.obj_blood - maxvalue) : 0; // 更新目标状态的血量
    } else { // 攻击算子无战损，重置目标算子的血量
      objcopy.obj_blood = p_obj->obj_blood;
    }
    
    // 计算躲避位置
    attcopy.obj_step = p_attele[2];
    struct GA *p_defgawicg = ga_init(0,3,sizeof(int));
    whereICanGoRangeGA(&attcopy, p_defgawicg);
    for (int x2_i = 0 ; x2_i < p_defgawicg->count ; x2_i ++){ 
      int shooting_b = 0;
      int *p_defele = (int*)ga_getele(p_defgawicg, x2_i);
      p_ffbtroute[FFBTMODE_DEFENSELOC_ROW_A] = p_defele[0]; 
      p_ffbtroute[FFBTMODE_DEFENSELOC_COL_A] = p_defele[1];
      p_ffbtroute[FFBTMODE_DEFENSELOC_LEFTPOWER_A] = p_defele[2];
      int int_4loc_blood = p_defele[0] * 1000 + p_defele[1] * 10 + objcopy.obj_blood; // 唯一标记还要加上自身的血量 obj_blood;
      cvtIntLocTo4StrOffLoc(int_4loc_blood, chars_4loc_blood, 6);

      if(dic_find(p_x2dict, chars_4loc_blood, 6)==0){ // 当前x2没有记录在案
	int curcount = p_gaffbtroutes->count;
	dic_add(p_x2dict, chars_4loc_blood, &curcount, 6, sizeof(int));
	updateOperatorLoc(&attcopy, p_defele[0], p_defele[1]);
	struct GA* p_objgadamagelist = ga_init(0, p_obj->obj_wznum + 3, sizeof(float));
	listdamages( &objcopy, &attcopy, p_objdicwicg, p_objgadamagelist);
	if (p_objgadamagelist->count>0){
	  shooting_b = 1;
	  float p_optele[5] = {0};
	  optShootingCond(p_objgadamagelist,5, p_optele);
	  p_ffbtroute[FFBTMODE_SHOOTING_ROW_O]=p_optele[0];
	  p_ffbtroute[FFBTMODE_SHOOTING_COL_O]=p_optele[1];
	  p_ffbtroute[FFBTMODE_SHOOTING_LEFTPOWER_O]=p_optele[2];
	  p_ffbtroute[FFBTMODE_WEAPENINDEX_O] = p_optele[3];
	  // 以矩阵的形式引入敌方其他算子对在防御位置的我方算子的威胁数值,如果目标算子在该位置能射击，取最大数值
	  float ori_damage_o = p_optele[4];
	  float union_damage_o = p_uniondamage_map[p_defele[0] * MAP_XNUM + p_defele[1]];
	  p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_O]= ori_damage_o >= union_damage_o ? ori_damage_o : union_damage_o;
	  p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_O] *= p_attacker->obj_value;
	}else{
	  // 如果目标算子在该位置不能射击，取p_uniondamage_map中的战损数值
	  shooting_b = 0;
	  p_ffbtroute[FFBTMODE_SHOOTING_ROW_O] = -1;
	  p_ffbtroute[FFBTMODE_SHOOTING_COL_O] = -1;
	  p_ffbtroute[FFBTMODE_SHOOTING_LEFTPOWER_O] = p_obj->obj_stepmax; // 不进行机动力满格
	  p_ffbtroute[FFBTMODE_WEAPENINDEX_O] = -1;
	  p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_O] = p_uniondamage_map[p_defele[0] * MAP_XNUM + p_defele[1]] * p_attacker->obj_value;
	}
	int routetype = shooting_a * 10 + shooting_b;
	p_ffbtroute[FFBTMODE_STRATEGYTYPE] = routetype;
	ga_delete(p_objgadamagelist);
      }else{ // 之前计算过x2
	int route_index = ((int*)p_x2dict->p_findvalue)[0];
	p_ffbtroute[FFBTMODE_SHOOTING_ROW_O] = *(float*)ga_getattr(p_gaffbtroutes, route_index, FFBTMODE_SHOOTING_ROW_O);
	p_ffbtroute[FFBTMODE_SHOOTING_COL_O] =*(float*)ga_getattr(p_gaffbtroutes, route_index, FFBTMODE_SHOOTING_COL_O);
	p_ffbtroute[FFBTMODE_SHOOTING_LEFTPOWER_O]=*(float*)ga_getattr(p_gaffbtroutes, route_index, FFBTMODE_SHOOTING_LEFTPOWER_O);
	p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_O]=*(float*)ga_getattr(p_gaffbtroutes, route_index, FFBTMODE_SHOOTING_DAMAGELEVEL_O);
	p_ffbtroute[FFBTMODE_WEAPENINDEX_O] =*(float*)ga_getattr(p_gaffbtroutes, route_index, FFBTMODE_WEAPENINDEX_O);
	shooting_b = ((int)(*(float*)ga_getattr(p_gaffbtroutes, route_index, FFBTMODE_STRATEGYTYPE))) % 10;
      }
      p_ffbtroute[FFBTMODE_REWARD] = p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_A] - p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_O];
      p_ffbtroute[FFBTMODE_STRATEGYTYPE] = shooting_a * 10 + shooting_b;
      ga_appendele(p_gaffbtroutes,p_ffbtroute, FFBTMODE_ELELEN, sizeof(float));
    }
    ga_delete(p_defgawicg);
  }
  ga_delete(p_attgawicg);
  dic_delete(p_x2dict);
  dic_delete(p_objdicwicg);
  return;
}

void getFFBTRoutes1000(const struct BasicOperator *p_attacker, const struct BasicOperator *p_obj, const float * p_uniondamage_map, struct GA *p_gaffbtroutes)
{  
  // 坦克射击人员/战车：对方算子不能攻击我方的标志（对方无行射能力，已经机动过/ 对方已经射击过 / 人员算子处于压制状态）
  bool flag_objis_invalid = (p_obj->obj_step != p_obj->obj_stepmax) || (p_obj->obj_attack != 0) || (p_obj->obj_type == 1 && p_obj->obj_keep == 1);
  // assert(p_attacker->a1 != 0 && p_obj->a1 == 0);
  struct BasicOperator attcopy = *p_attacker;
  struct BasicOperator objcopy = *p_obj;
  objcopy.obj_step = objcopy.obj_stepmax;

  struct GA *p_attgawicg = ga_init(0,3,sizeof(int));
  whereICanGoRangeGA(p_attacker, p_attgawicg);
  struct dictionary *p_x2dict = dic_new(0, sizeof(int));// value 记录在p_gaffbtroutes中具有相同x2的条目位置
  char chars_4loc_blood[6]={'\0'};
  float maxvalue = 0; int maxindex = 0;
  const int att_int4_initloc = cvtInt6loc2Int4loc(p_attacker->obj_pos);
  for(int xstar_i = 0 ; xstar_i < p_attgawicg->count ; xstar_i++){
    float p_ffbtroute[FFBTMODE_ELELEN]={0};
    p_ffbtroute[FFBTMODE_INITLOC_ROW_A] = att_int4_initloc / 100;
    p_ffbtroute[FFBTMODE_INITLOC_COL_A] = att_int4_initloc % 100;

    int shooting_a = 0; 
    int *p_attele = (int*) (ga_getele(p_attgawicg, xstar_i));
    p_ffbtroute[FFBTMODE_SHOOTING_ROW_A] = p_attele[0];
    p_ffbtroute[FFBTMODE_SHOOTING_COL_A] = p_attele[1];
    p_ffbtroute[FFBTMODE_SHOOTING_LEFTPOWER_A] = p_attele[2];

    p_ffbtroute[FFBTMODE_WEAPENINDEX_A] = -1; 
    p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_A] = 0;
    attcopy.obj_pos = cvtOffsetIntLocToInt6(p_attele[0], p_attele[1]);
    if(weaponSelectionForAttacker(&attcopy, p_obj, &maxvalue, &maxindex)){
      shooting_a = 1;
      p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_A] = maxvalue * p_obj->obj_value;
      p_ffbtroute[FFBTMODE_WEAPENINDEX_A] = maxindex;
      objcopy.obj_blood = p_obj->obj_blood; // 重置血量为初始状态
      objcopy.obj_blood = objcopy.obj_blood - maxvalue > 0 ? round(objcopy.obj_blood - maxvalue) : 0; // 更新目标状态的血量  
    } else {
      objcopy.obj_blood = p_obj->obj_blood; // 重置血量为初始状态
    }
    // 计算躲避位置
    attcopy.obj_step = (int)(p_attele[2]);
    struct GA *p_defgawicg = ga_init(0,3,sizeof(int));
    whereICanGoRangeGA(&attcopy, p_defgawicg);
    for (int x2_i = 0 ; x2_i < p_defgawicg->count ; x2_i ++){ 
      int shooting_b = 0;
      int *p_defele = (int*)ga_getele(p_defgawicg, x2_i);
      p_ffbtroute[FFBTMODE_DEFENSELOC_ROW_A] = p_defele[0];
      p_ffbtroute[FFBTMODE_DEFENSELOC_COL_A] = p_defele[1];
      p_ffbtroute[FFBTMODE_DEFENSELOC_LEFTPOWER_A] = p_defele[2];
      int int_4loc_blood = p_defele[0]* 1000 + p_defele[1] * 10 + objcopy.obj_blood;
      cvtIntLocTo4StrOffLoc(int_4loc_blood, chars_4loc_blood, 6);
      if(dic_find(p_x2dict, chars_4loc_blood, 6)==0){ // 当前x2没有记录在案
	int curcount = p_gaffbtroutes->count;
	dic_add(p_x2dict, chars_4loc_blood, &curcount, 6, sizeof(int));
	attcopy.obj_pos = cvtOffsetIntLocToInt6(p_defele[0], p_defele[1]);
	if (weaponSelectionForAttacker(&objcopy, &attcopy, &maxvalue, &maxindex)){
	  shooting_b = 1;
	  int tmp_row = 0; int tmp_col = 0;
	  getLocOfOffsetFromOperator(p_obj, &tmp_row,&tmp_col);
	  p_ffbtroute[FFBTMODE_SHOOTING_ROW_O] = tmp_row;
	  p_ffbtroute[FFBTMODE_SHOOTING_COL_O] = tmp_col;
	  p_ffbtroute[FFBTMODE_SHOOTING_LEFTPOWER_O]= p_obj->obj_stepmax;
	  p_ffbtroute[FFBTMODE_WEAPENINDEX_O] = maxindex;
	  float ori_damage_o = flag_objis_invalid ? 0.f :  maxvalue ;
	  float union_damage_o = p_uniondamage_map[p_defele[0] * MAP_XNUM + p_defele[1]];
	  p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_O] = ori_damage_o >= union_damage_o ? ori_damage_o : union_damage_o;
	  p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_O] *= p_attacker->obj_value;
	}else{
	  shooting_b = 0;
	  p_ffbtroute[FFBTMODE_SHOOTING_ROW_O] = -1;
	  p_ffbtroute[FFBTMODE_SHOOTING_COL_O] = -1;
	  p_ffbtroute[FFBTMODE_SHOOTING_LEFTPOWER_O] = p_obj->obj_stepmax;
	  p_ffbtroute[FFBTMODE_WEAPENINDEX_O] = -1;
	  p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_O] = p_uniondamage_map[p_defele[0] * MAP_XNUM + p_defele[1]] * p_attacker->obj_value;
	}
      }else{ // 之前计算过x2
	int route_index = ((int*)p_x2dict->p_findvalue)[0];
	p_ffbtroute[FFBTMODE_SHOOTING_ROW_O] = *(float*)ga_getattr(p_gaffbtroutes, route_index, FFBTMODE_SHOOTING_ROW_O);
	p_ffbtroute[FFBTMODE_SHOOTING_COL_O] =*(float*)ga_getattr(p_gaffbtroutes, route_index, FFBTMODE_SHOOTING_COL_O);
	p_ffbtroute[FFBTMODE_SHOOTING_LEFTPOWER_O]=*(float*)ga_getattr(p_gaffbtroutes, route_index, FFBTMODE_SHOOTING_LEFTPOWER_O);
	p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_O]=*(float*)ga_getattr(p_gaffbtroutes, route_index, FFBTMODE_SHOOTING_DAMAGELEVEL_O);
	p_ffbtroute[FFBTMODE_WEAPENINDEX_O] =*(float*)ga_getattr(p_gaffbtroutes, route_index, FFBTMODE_WEAPENINDEX_O);
	shooting_b = ((int)(*(float*)ga_getattr(p_gaffbtroutes, route_index, FFBTMODE_STRATEGYTYPE))) % 10;
      }
      p_ffbtroute[FFBTMODE_REWARD] = p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_A] - p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_O];
      p_ffbtroute[FFBTMODE_STRATEGYTYPE] = shooting_a * 10 + shooting_b;
      ga_appendele(p_gaffbtroutes, p_ffbtroute, FFBTMODE_ELELEN, sizeof(float));
      // printf("\t\t\t strategy = %d, final_reward =  %f\n",(int) (p_ffbtroute[FFBTMODE_STRATEGYTYPE]), p_ffbtroute[FFBTMODE_REWARD]);
    }
    ga_delete(p_defgawicg);
  }
  ga_delete(p_attgawicg);
  dic_delete(p_x2dict);
  return;
}


void getALLFFBTRoutes(const struct BasicOperator * p_att, const struct BasicOperator *p_obj, struct GA* p_gaffbtroutes)
{
  // 坦克射击人员/战车：对方算子不能攻击我方的标志（对方无行射能力，已经机动过/ 对方已经射击过 / 人员算子处于压制状态）
  // bool flag_objis_invalid = (p_obj->obj_step != p_obj->obj_stepmax) || (p_obj->obj_attack != 0) || (p_obj->obj_type == 1 && p_obj->obj_keep == 1);
  // 输入数据的检查
  if (p_att == NULL || p_obj == NULL || p_att->a1 ==0){
    printf("error in getALLFFBTRoutes()\n");
    return ;
  }
  struct BasicOperator attcopy = *p_att;
  struct BasicOperator objcopy = *p_obj;
  struct GA *p_attgawicg = ga_init(0,3,sizeof(int));
  whereICanGoRangeGA(p_att, p_attgawicg);
  struct dictionary *p_x2dict = dic_new(0, sizeof(int));// value 记录在p_gaffbtroutes中具有相同x2的条目位置
  char chars_4loc_blood[6]={'\0'};
  float maxvalue = 0; int maxindex = 0;
  const int att_int4_initloc = cvtInt6loc2Int4loc(p_att->obj_pos);
  for(int xstar_i = 0 ; xstar_i < p_attgawicg->count ; xstar_i++){
    float p_ffbtroute[FFBTMODE_ELELEN]={0};
    p_ffbtroute[FFBTMODE_INITLOC_ROW_A] = att_int4_initloc / 100;
    p_ffbtroute[FFBTMODE_INITLOC_COL_A] = att_int4_initloc % 100;

    int shooting_a = 0; 
    int *p_attele = (int*) (ga_getele(p_attgawicg, xstar_i));
    p_ffbtroute[FFBTMODE_SHOOTING_ROW_A] = p_attele[0];
    p_ffbtroute[FFBTMODE_SHOOTING_COL_A] = p_attele[1];
    p_ffbtroute[FFBTMODE_SHOOTING_LEFTPOWER_A] = p_attele[2];

    p_ffbtroute[FFBTMODE_WEAPENINDEX_A] = -1; 
    p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_A] = 0;
    attcopy.obj_pos = cvtOffsetIntLocToInt6(p_attele[0], p_attele[1]);
    /*
    if(weaponSelectionForAttacker(&attcopy, p_obj, &maxvalue, &maxindex)){
      shooting_a = 1;
      p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_A] = maxvalue * p_obj->obj_value;
      p_ffbtroute[FFBTMODE_WEAPENINDEX_A] = maxindex;
      objcopy.obj_blood = p_obj->obj_blood; // 重置血量为初始状态
      objcopy.obj_blood = objcopy.obj_blood - maxvalue > 0 ? round(objcopy.obj_blood - maxvalue) : 0; // 更新目标状态的血量  
    } else {
      objcopy.obj_blood = p_obj->obj_blood; // 重置血量为初始状态
    }
    */
    if(weaponSelectionForAttacker(&attcopy, p_obj, &maxvalue, &maxindex)){
      shooting_a = 1;
      // 此处返回的maxvalue是攻击等级，不是真实战损！
      p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_A] = maxvalue;
      p_ffbtroute[FFBTMODE_WEAPENINDEX_A] = maxindex;
      objcopy.obj_blood = p_obj->obj_blood; // 重置血量为初始状态（表明我方算子攻击对方算子无效，也就是对方算子以最强战力(真实)反击）
      objcopy.obj_blood = maxvalue >= 11 ? objcopy.obj_blood - 1 : objcopy.obj_blood; // 更新目标状态的血量（如果攻击等级>=5,血量-1）
    } else {
      objcopy.obj_blood = p_obj->obj_blood; // 重置血量为初始状态
    }
    // 计算躲避位置
    attcopy.obj_step = (int)(p_attele[2]);
    struct GA *p_defgawicg = ga_init(0,3,sizeof(int));
    whereICanGoRangeGA(&attcopy, p_defgawicg);
    for (int x2_i = 0 ; x2_i < p_defgawicg->count ; x2_i ++){ 
      int shooting_b = 0;
      int *p_defele = (int*)ga_getele(p_defgawicg, x2_i);
      p_ffbtroute[FFBTMODE_DEFENSELOC_ROW_A] = p_defele[0];
      p_ffbtroute[FFBTMODE_DEFENSELOC_COL_A] = p_defele[1];
      p_ffbtroute[FFBTMODE_DEFENSELOC_LEFTPOWER_A] = p_defele[2];
      int int_4loc_blood = p_defele[0]* 1000 + p_defele[1] * 10 + objcopy.obj_blood;
      cvtIntLocTo4StrOffLoc(int_4loc_blood, chars_4loc_blood, 6);
      if(dic_find(p_x2dict, chars_4loc_blood, 6)==0){ // 当前x2没有记录在案
	int curcount = p_gaffbtroutes->count;
	dic_add(p_x2dict, chars_4loc_blood, &curcount, 6, sizeof(int));
	attcopy.obj_pos = cvtOffsetIntLocToInt6(p_defele[0], p_defele[1]);
	/*
	if (weaponSelectionForAttacker(&objcopy, &attcopy, &maxvalue, &maxindex)){
	  shooting_b = 1;
	  int tmp_row = 0; int tmp_col = 0;
	  getLocOfOffsetFromOperator(p_obj, &tmp_row,&tmp_col);
	  p_ffbtroute[FFBTMODE_SHOOTING_ROW_O] = tmp_row;
	  p_ffbtroute[FFBTMODE_SHOOTING_COL_O] = tmp_col;
	  p_ffbtroute[FFBTMODE_SHOOTING_LEFTPOWER_O]= p_obj->obj_stepmax;
	  p_ffbtroute[FFBTMODE_WEAPENINDEX_O] = maxindex;
	  float ori_damage_o = flag_objis_invalid ? 0.f :  maxvalue ;
	  float union_damage_o = p_uniondamage_map[p_defele[0] * MAP_XNUM + p_defele[1]];
	  p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_O] = ori_damage_o >= union_damage_o ? ori_damage_o : union_damage_o;
	  p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_O] *= p_att->obj_value;
	}
	*/
	if (weaponSelectionForAttacker(&objcopy, &attcopy, &maxvalue, &maxindex)){
	  shooting_b = 1;
	  int tmp_row = 0; int tmp_col = 0;
	  getLocOfOffsetFromOperator(p_obj, &tmp_row,&tmp_col);
	  p_ffbtroute[FFBTMODE_SHOOTING_ROW_O] = tmp_row;
	  p_ffbtroute[FFBTMODE_SHOOTING_COL_O] = tmp_col;
	  p_ffbtroute[FFBTMODE_SHOOTING_LEFTPOWER_O]= p_obj->obj_step; //实际用不到
	  p_ffbtroute[FFBTMODE_WEAPENINDEX_O] = maxindex;
	  p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_O] = maxvalue;// 记录对方算子对我方算子的攻击等级
	}
	else{
	  shooting_b = 0;
	  p_ffbtroute[FFBTMODE_SHOOTING_ROW_O] = -1;
	  p_ffbtroute[FFBTMODE_SHOOTING_COL_O] = -1;
	  p_ffbtroute[FFBTMODE_SHOOTING_LEFTPOWER_O] = p_obj->obj_step;
	  p_ffbtroute[FFBTMODE_WEAPENINDEX_O] = -1;
	  p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_O] = 0.f;
	  // p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_O] = p_uniondamage_map[p_defele[0] * MAP_XNUM + p_defele[1]] * p_att->obj_value;
	}
      }else{ // 之前计算过x2
	int route_index = ((int*)p_x2dict->p_findvalue)[0];
	p_ffbtroute[FFBTMODE_SHOOTING_ROW_O] = *(float*)ga_getattr(p_gaffbtroutes, route_index, FFBTMODE_SHOOTING_ROW_O);
	p_ffbtroute[FFBTMODE_SHOOTING_COL_O] =*(float*)ga_getattr(p_gaffbtroutes, route_index, FFBTMODE_SHOOTING_COL_O);
	p_ffbtroute[FFBTMODE_SHOOTING_LEFTPOWER_O]=*(float*)ga_getattr(p_gaffbtroutes, route_index, FFBTMODE_SHOOTING_LEFTPOWER_O);
	p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_O]=*(float*)ga_getattr(p_gaffbtroutes, route_index, FFBTMODE_SHOOTING_DAMAGELEVEL_O);
	p_ffbtroute[FFBTMODE_WEAPENINDEX_O] =*(float*)ga_getattr(p_gaffbtroutes, route_index, FFBTMODE_WEAPENINDEX_O);
	shooting_b = ((int)(*(float*)ga_getattr(p_gaffbtroutes, route_index, FFBTMODE_STRATEGYTYPE))) % 10;
      }
      p_ffbtroute[FFBTMODE_REWARD] = p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_A] - p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_O];
      p_ffbtroute[FFBTMODE_STRATEGYTYPE] = shooting_a * 10 + shooting_b;
      ga_appendele(p_gaffbtroutes, p_ffbtroute, FFBTMODE_ELELEN, sizeof(float));
      // printf("\t\t\t strategy = %d, final_reward =  %f\n",(int) (p_ffbtroute[FFBTMODE_STRATEGYTYPE]), p_ffbtroute[FFBTMODE_REWARD]);
    }
    ga_delete(p_defgawicg);
  }
  ga_delete(p_attgawicg);
  dic_delete(p_x2dict);
  return;
}

bool getBestFFBTRoutes(const struct GA* p_gaffbtroutes, const int ele_len, const int* p_totalblind_map, float * p_route)
{
  assert(ele_len == FFBTMODE_ELELEN && p_route != NULL);
  
  // 检查集合为空/集合数据无效
  int num_invalid = 0;
  for (int route_i = 0 ; route_i < p_gaffbtroutes->count; route_i ++){
    float *p_ele = (float*) ga_getele(p_gaffbtroutes, route_i);
    if (p_ele[FFBTMODE_SHOOTING_DAMAGELEVEL_A] == 0 && p_ele[FFBTMODE_SHOOTING_DAMAGELEVEL_O] == 0)
      num_invalid ++;  
  }
  if (num_invalid == p_gaffbtroutes->count) { 
    // printf("\t\tFFBT中数据无效\n");
    return false;
  }

  // 初始化p_route,
  for (int i = 0 ; i < ele_len; i++)
    p_route[i] = 0;

  int min_dis_s_e = 1000;
  float max_reward = -1000;
  int  min_blindlevel = 1000;
  bool max_flag_incover = false;
  float min_leftpow = 10000; 
  int max_index = -1;
  const float max_error_reward = 0.5;

  // 计算最大战损，然后在误差允许范围内比较其他条件
  for(int route_i = 0 ; route_i < p_gaffbtroutes->count; route_i ++){
    float *p_ele = (float*) ga_getele(p_gaffbtroutes, route_i);
    float cur_reward = p_ele[FFBTMODE_REWARD];
    if (cur_reward > max_reward) {
      max_reward = cur_reward;
    }
  }
  // 最大战损>0才进行攻击
  if (max_reward <= -3){
    // printf("\t\tFFBT max_reward = %f , total count = %d\n", max_reward, p_gaffbtroutes->count);
    return false;
  }
  
  //存在(符合要求的)最大战损，在此基础上，筛选其他候选
  for(int route_i = 0 ; route_i < p_gaffbtroutes->count; route_i ++)
  {
    float *p_ele = (float*) ga_getele(p_gaffbtroutes, route_i);
    struct HexOfOffset cur_hex = {(int)(p_ele[FFBTMODE_DEFENSELOC_ROW_A]), (int)(p_ele[FFBTMODE_DEFENSELOC_COL_A])};
    float cur_reward = p_ele[FFBTMODE_REWARD];
    int cur_blindlevel =  p_totalblind_map[cur_hex.row * MAP_XNUM + cur_hex.col];
    bool cur_flag_incover = checkHexIsInCover(&cur_hex);
    int cur_leftpow = p_ele[FFBTMODE_DEFENSELOC_LEFTPOWER_A];
    //寻找该路径的出发点和落脚点
    const struct HexOfOffset hex_e = {p_ele[FFBTMODE_DEFENSELOC_ROW_A], p_ele[FFBTMODE_DEFENSELOC_COL_A]};
    const struct HexOfOffset hex_s = {p_ele[FFBTMODE_INITLOC_ROW_A], p_ele[FFBTMODE_INITLOC_COL_A]};
    assert (checkHexIsValid(&hex_s) && checkHexIsValid(&hex_e) );
    int cur_dis_s_e = getDistanceBetweenHexOfOffset(&hex_s, &hex_e);

    if( (fabs(cur_reward - max_reward) <= max_error_reward && cur_blindlevel < min_blindlevel) ||
    (fabs(cur_reward - max_reward) <= max_error_reward && cur_blindlevel == min_blindlevel && min_dis_s_e >= cur_dis_s_e) ||
	(fabs(cur_reward - max_reward) <= max_error_reward && cur_blindlevel == min_blindlevel && min_dis_s_e == cur_dis_s_e && cur_flag_incover == true && max_flag_incover == false)  ||
	(fabs(cur_reward - max_reward) <= max_error_reward && cur_blindlevel == min_blindlevel && min_dis_s_e == cur_dis_s_e && cur_flag_incover == max_flag_incover && cur_leftpow < min_leftpow) ) {
	// printf("落脚点位置：%d,%d,我方战损= %f, 敌方战损 = %f,  此刻战损：%f\n", cur_hex.row, cur_hex.col, p_ele[FFBTMODE_SHOOTING_DAMAGELEVEL_A], p_ele[FFBTMODE_SHOOTING_DAMAGELEVEL_O], cur_reward);
	// max_reward = cur_reward;
	min_dis_s_e = cur_dis_s_e;
	min_blindlevel = cur_blindlevel;
	max_flag_incover = cur_flag_incover;
	min_leftpow = cur_leftpow;
	max_index = route_i;
    }
  }
  
  // assert (max_index >= 0);
  if (max_index < 0) return false;
  const float *p_ele = (float*) ga_getele(p_gaffbtroutes, max_index);
  memcpy(p_route, p_ele, FFBTMODE_ELELEN * sizeof(float));
  if(p_ele[FFBTMODE_REWARD] <= 0) return false;
  return true;
}

// 计算给定躲避点的最佳行射动作(攻击等级最大)
bool getSpecHideBestFFBTRoutes(const struct GA* p_gaffbtroutes, const int ele_len, const int goal_hidenloc4, float * p_route)
{
  assert(ele_len == FFBTMODE_ELELEN && p_route != NULL);

  // 检查集合为空/集合数据无效
  if (0 == p_gaffbtroutes->count) {
    // printf("\t\tFFBT中数据无效\n");
    return false;
  }

  // 初始化p_route,
  for (int i = 0 ; i < ele_len; i++)
    p_route[i] = 0;

  float max_damage = -1000;
  int max_index = -1;


  // 计算满足落脚点的最大战损，然后在误差允许范围内比较其他条件
  for(int route_i = 0 ; route_i < p_gaffbtroutes->count; route_i ++){
    float *p_ele = (float*) ga_getele(p_gaffbtroutes, route_i);
    float cur_damage = p_ele[FFBTMODE_SHOOTING_DAMAGELEVEL_A];
    int cur_hideloc4 = (int)(p_ele[FFBTMODE_DEFENSELOC_ROW_A])*100+(int)(p_ele[FFBTMODE_DEFENSELOC_COL_A]);
    if (cur_hideloc4 == goal_hidenloc4 && cur_damage > max_damage) {
      max_damage = cur_damage;
      max_index = route_i;
    }
  }

  if (max_index < 0) return false;
  const float *p_ele = (float*) ga_getele(p_gaffbtroutes, max_index);
  memcpy(p_route, p_ele, FFBTMODE_ELELEN * sizeof(float));
  if(p_ele[FFBTMODE_REWARD] <= 0) return false;
  return true;
}

void cvtFFBTRoute2AIAction( const struct BasicOperator * p_bopattacker, const struct BasicOperator *p_bopobj,const int ffbtroute_len, const float *p_ffbtroute, const int aiaction_len, float *p_aiaction)
{
  assert(ffbtroute_len == FFBTMODE_ELELEN && aiaction_len == AIACTION_ELELEN);
  assert(p_ffbtroute != NULL && p_aiaction != NULL);
  // 算子是否进行射击前移动
  bool flag_move_0 = p_bopattacker->obj_pos != cvtOffsetIntLocToInt6((int)(p_ffbtroute[FFBTMODE_SHOOTING_ROW_A]), (int)(p_ffbtroute[FFBTMODE_SHOOTING_COL_A]));
  int hexnum_inpath_0 = 0;
  struct GA *p_gafullpath_0 = ga_init(0,3,sizeof(int));
  struct GA *p_gapartpath_0 = ga_init(0,3,sizeof(int));
  if(flag_move_0){
    struct HexOfOffset move_objhex = {(int)(p_ffbtroute[FFBTMODE_SHOOTING_ROW_A]), (int)(p_ffbtroute[FFBTMODE_SHOOTING_COL_A])};
    trendpathP2P(p_bopattacker, &move_objhex, p_gafullpath_0, p_gapartpath_0);
    hexnum_inpath_0 = p_gapartpath_0->count - 1 ;
    //assert(hexnum_inpath_0 <= 7 && hexnum_inpath_0 > 0);
    if(!(hexnum_inpath_0 <= 7 && hexnum_inpath_0 > 0)){
      ga_delete(p_gafullpath_0);  ga_delete(p_gapartpath_0);
      p_aiaction[0] = AIACTION_INVALID; 
      return;
    }
  }
  // 算子是否进行射击后移动
  int hexnum_inpath_1 = 0; 
  struct GA *p_gafullpath_1 = ga_init(0,3,sizeof(int));
  struct GA *p_gapartpath_1 = ga_init(0,3,sizeof(int));
  bool flag_move_1 = (p_ffbtroute[FFBTMODE_SHOOTING_ROW_A] != p_ffbtroute[FFBTMODE_DEFENSELOC_ROW_A]) 
		    || (p_ffbtroute[FFBTMODE_SHOOTING_COL_A] != p_ffbtroute[FFBTMODE_DEFENSELOC_COL_A]);
  if (flag_move_1){
    struct HexOfOffset move_objhex = {(int)(p_ffbtroute[FFBTMODE_DEFENSELOC_ROW_A]),(int)(p_ffbtroute[FFBTMODE_DEFENSELOC_COL_A])};
    struct BasicOperator attackercopy = *p_bopattacker;
    attackercopy.obj_step = (int)(p_ffbtroute[FFBTMODE_SHOOTING_LEFTPOWER_A]);
    updateOperatorLoc(&attackercopy, (int)(p_ffbtroute[FFBTMODE_SHOOTING_ROW_A]),(int)(p_ffbtroute[FFBTMODE_SHOOTING_COL_A]));
    trendpathP2P(&attackercopy, &move_objhex, p_gafullpath_1, p_gapartpath_1);
    hexnum_inpath_1 = p_gapartpath_1->count - 1 ;
    if(!(hexnum_inpath_1 <= 7 && hexnum_inpath_1 > 0)){// 防止内存泄漏
      ga_delete(p_gafullpath_0);  ga_delete(p_gapartpath_0);
      ga_delete(p_gafullpath_1);  ga_delete(p_gapartpath_1);
      p_aiaction[0] = AIACTION_INVALID; 
      return;
    }
  }

  int hexnum_inpath_2 = 0; // 从初始位置到躲避位置（不射击条件下）
  struct GA *p_gafullpath_2 = ga_init(0,3,sizeof(int));
  struct GA *p_gapartpath_2 = ga_init(0,3,sizeof(int));
  bool flag_move_2 = p_bopattacker->obj_pos != cvtOffsetIntLocToInt6((int)(p_ffbtroute[FFBTMODE_DEFENSELOC_ROW_A]),
    (int)(p_ffbtroute[FFBTMODE_DEFENSELOC_COL_A]));
  if (flag_move_2){
    struct HexOfOffset move_objhex = {(int)(p_ffbtroute[FFBTMODE_DEFENSELOC_ROW_A]),(int)(p_ffbtroute[FFBTMODE_DEFENSELOC_COL_A])};
    trendpathP2P(p_bopattacker, &move_objhex, p_gafullpath_2, p_gapartpath_2);
    hexnum_inpath_2 = p_gapartpath_2->count - 1 ;
    if(!(hexnum_inpath_2 <= 7 && hexnum_inpath_2 > 0)){// 防止内存泄漏
      ga_delete(p_gafullpath_0);  ga_delete(p_gapartpath_0);
      ga_delete(p_gafullpath_1);  ga_delete(p_gapartpath_1);
      ga_delete(p_gafullpath_2);  ga_delete(p_gapartpath_2);
      p_aiaction[0] = AIACTION_INVALID; 
      return;
    }
  }

  // 算子是否进行了射击
  bool flag_shoot = ( (int)(p_ffbtroute[FFBTMODE_STRATEGYTYPE]) ) / 10 == 1;

  if (flag_shoot){ // 发生射击
      p_aiaction[1] = p_bopattacker->obj_id;
    if (flag_move_0 == false){ //射击前不移动： 原地射击 或者 射击移动
      if(flag_move_1 == false){ // 原地射击（仅射击）
	p_aiaction[0] = AIACTION_SHOOTONLY;
	p_aiaction[2] = p_bopobj->obj_id;
	// p_aiaction[3] = (p_bopattacker-> p_obj_wzs)[(int)(p_ffbtroute[FFBTMODE_WEAPENINDEX_A])].weapon_id;
	p_aiaction[3] = p_bopattacker->p_obj_wpids[(int)(p_ffbtroute[FFBTMODE_WEAPENINDEX_A])];
	p_aiaction[4] = p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_A];
      } else { // 射击移动
	p_aiaction[0] = AIACTION_SHOOTMOVE;
	p_aiaction[2] = p_bopobj->obj_id;
	// p_aiaction[3] = (p_bopattacker-> p_obj_wzs)[(int)p_ffbtroute[FFBTMODE_WEAPENINDEX_A]].weapon_id;
	p_aiaction[3] = p_bopattacker->p_obj_wpids[(int)(p_ffbtroute[FFBTMODE_WEAPENINDEX_A])];
	// p_aiaction[4] = p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_A];
	p_aiaction[4] = p_ffbtroute[FFBTMODE_REWARD];
	p_aiaction[5] = hexnum_inpath_1;
	for (int i = 6 ; i < 6 + hexnum_inpath_1; i ++){
	  int *p_ele = ga_getele(p_gapartpath_1, i - 6 + 1);
	  p_aiaction[i] = cvtOffsetIntLocToInt6((int)(p_ele[0]), (int)(p_ele[1]));
	}
      }
    } else if(flag_move_1 == false ){ // 射击前移动,射击后不移动：移动射击
      p_aiaction[0] = AIACTION_MOVESHOOT;
      p_aiaction[2] = hexnum_inpath_0;
      for (int i = 3; i < 3 + hexnum_inpath_0; i++){
	int *p_ele = ga_getele(p_gapartpath_0, i-3 + 1); // 从第一个开始：第0个标识算子的起始位置或者当前位置
	p_aiaction[i] = cvtOffsetIntLocToInt6((int)(p_ele[0]), (int)(p_ele[1]));
      }
      p_aiaction[3 + hexnum_inpath_0] = p_bopobj->obj_id;
      // p_aiaction[4 + hexnum_inpath_0] = (p_bopattacker-> p_obj_wzs)[(int)(p_ffbtroute[FFBTMODE_WEAPENINDEX_A])].weapon_id;
      p_aiaction[4 + hexnum_inpath_0] = p_bopattacker->p_obj_wpids[(int)(p_ffbtroute[FFBTMODE_WEAPENINDEX_A])];
      //p_aiaction[5 + hexnum_inpath_0] = p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_A];
      p_aiaction[5 + hexnum_inpath_0] = p_ffbtroute[FFBTMODE_REWARD];
    } else { // 射击前后都移动
      p_aiaction[0] = AIACTION_MOVESHOOTMOVE;
      p_aiaction[2] = hexnum_inpath_0;
      for (int i = 3; i < 3 + hexnum_inpath_0; i++){
	int *p_ele = ga_getele(p_gapartpath_0, i-3 + 1); // 从第一个开始：第0个标识算子的起始位置或者当前位置
	p_aiaction[i] = cvtOffsetIntLocToInt6((int)(p_ele[0]), (int)(p_ele[1]));
      }
      p_aiaction[3 + hexnum_inpath_0] = p_bopobj->obj_id;
      // p_aiaction[4 + hexnum_inpath_0] = (p_bopattacker-> p_obj_wzs)[(int)(p_ffbtroute[FFBTMODE_WEAPENINDEX_A])].weapon_id;
      p_aiaction[4 + hexnum_inpath_0] = p_bopattacker->p_obj_wpids[(int)(p_ffbtroute[FFBTMODE_WEAPENINDEX_A])];
      // p_aiaction[5 + hexnum_inpath_0] = p_ffbtroute[FFBTMODE_SHOOTING_DAMAGELEVEL_A];
      p_aiaction[5 + hexnum_inpath_0] = p_ffbtroute[FFBTMODE_REWARD];
      p_aiaction[6 + hexnum_inpath_0] = hexnum_inpath_1;
      for (int i = 7 + hexnum_inpath_0 ; i < 7 + hexnum_inpath_0 + hexnum_inpath_1; i ++){
	int * p_ele = ga_getele(p_gapartpath_1, i - 7 - hexnum_inpath_0 + 1);
	p_aiaction[i] = cvtOffsetIntLocToInt6((int)(p_ele[0]), (int)(p_ele[1]));
      }
    }
  } else { // 不发生射击：不移动（无效路径动作）或者 仅移动 
    if(flag_move_2){ // 仅移动
      p_aiaction[0] = AIACTION_MOVEONLY; 
      p_aiaction[1] = p_bopattacker->obj_id;
      p_aiaction[2] = hexnum_inpath_2;
      for (int i = 3;  i < 3 + hexnum_inpath_2; i ++ ){
	int *p_ele = ga_getele(p_gapartpath_2, i - 3 + 1);
	p_aiaction[i] = cvtOffsetIntLocToInt6((int)(p_ele[0]), (int)(p_ele[1]));
      } 
      p_aiaction[18] = p_ffbtroute[FFBTMODE_REWARD];

    } else { // 不射击+不移动 ： 无效动作
      p_aiaction[0] = AIACTION_INVALID;
    }
  }
  ga_delete(p_gafullpath_0);  ga_delete(p_gapartpath_0);
  ga_delete(p_gafullpath_1);  ga_delete(p_gapartpath_1);
  ga_delete(p_gafullpath_2);  ga_delete(p_gapartpath_2);
  return;
}

bool checkStaticShooting(const struct BasicOperator *p_attacker, const struct BasicOperator *p_obj, float *p_static_reward)
{
  assert(p_attacker->a1 == 0);
  *p_static_reward = 0; 
  float maxvalue_1 = 0; int maxindex_1 = 0 ;
  float maxvalue_2 = 0; int maxindex_2 = 0;
  float reward_1 = 0;
  if (weaponSelectionForAttacker(p_attacker, p_obj, &maxvalue_1, &maxindex_1)){
    reward_1 = maxvalue_1 * p_obj->obj_value;
  };
  
  struct BasicOperator objcopy = *p_obj;
  objcopy.obj_blood = objcopy.obj_blood - maxvalue_1 > 0 ? round(objcopy.obj_blood - maxvalue_1) : 0;
  if (objcopy.obj_blood <= 0){
    printf("\t\t首次射击直接消灭对方\n");
    return true;
  }

  float reward = 0;
  if(p_obj->a1 == 0 ) {	// 对方无行射能力
    if (weaponSelectionForAttacker(&objcopy, p_attacker, &maxvalue_2, &maxindex_2)){
      reward = reward_1 - maxvalue_2 * p_attacker->obj_value;
    } else {
      reward = reward_1;
    }
  }else{ // 对方有行射能力
    struct GA *p_gaffbtroutes = ga_init(0, FFBTMODE_ELELEN, sizeof(float));
    float * p_bestroute = (float *) malloc( FFBTMODE_ELELEN * sizeof(float));
    const int map_totalcount = MAP_YNUM * MAP_XNUM;
    float *p_uniondamage_map = (float*) malloc(map_totalcount * sizeof(float));
    int *p_totalblind_map = (int*) malloc(map_totalcount * sizeof(int));
    for(int i = 0 ; i < map_totalcount; i++){
      p_uniondamage_map[i] = 0;
      p_totalblind_map[i] = 0;
    }

    objcopy.obj_step = objcopy.obj_stepmax; 
    getFFBTRoutes1000( &objcopy, p_attacker, p_uniondamage_map, p_gaffbtroutes); // 计算用战损图
    if (getBestFFBTRoutes(p_gaffbtroutes, FFBTMODE_ELELEN, p_totalblind_map, p_bestroute)) // 选择再加上危险点图
      reward = reward_1 - p_bestroute[FFBTMODE_REWARD]; 
    else 
      reward = reward_1;

    ga_delete(p_gaffbtroutes);
    free(p_bestroute);
    free(p_uniondamage_map);
    free(p_totalblind_map);
  }

  *p_static_reward = reward;

  // printf("我方先射击的战损:%f\n", reward_1);
  // printf("原地不动射击的最终战损:%f\n", reward);
  return reward > 0 ? true : false;
}

void getDARoutes0110(const struct BasicOperator *p_ocar, const struct BasicOperator *p_opeo, const struct BasicOperator *p_ucar, const float *p_uniondamage_map, struct GA *p_gadaroutes)
{
  assert(p_uniondamage_map != NULL);
  if (!(p_ocar->a1 == 0 && p_ocar->obj_type == 2 && p_opeo->obj_type == 1 && p_ucar->a1 != 0)){
    printf("error in getDARoutes0110(). ocar_a1, ocar_type, opeo_type, ucar_a1 = (%d,%d,%d,%d)\n",p_ocar->a1 ,p_ocar->obj_type, p_opeo->obj_type, p_ucar->a1);
    return;
  }
  assert(p_ocar->obj_sonnum == 1 /* && p_ocar->obj_sonid == p_opeo->obj_id && p_ocar->obj_pos == p_opeo->obj_pos*/);
  struct BasicOperator ocarcopy = *p_ocar;
  struct BasicOperator peocopy = *p_opeo;
  struct BasicOperator ucarcopy = *p_ucar;

  struct GA *p_gaattwicg = ga_init(0,3,sizeof(int));
  // printf("\t\tin getDARoutes0110_0\n");
  whereICanGoRangeGA(p_ocar, p_gaattwicg);
  // printf("\t\tin getDARoutes0110_1\n");
  const int peopleoff_needpower = (int)(p_ocar->obj_stepmax / 2.0);

  float* p_tmp_uniondamage_map = (float*) malloc (MAP_XNUM * MAP_YNUM * sizeof(float));
  int* p_totalblind_map = (int*) malloc (MAP_XNUM * MAP_YNUM * sizeof(int));
  for (int i = 0 ; i < MAP_XNUM * MAP_YNUM; i++){
    p_tmp_uniondamage_map[i] = 0.0f;
    p_totalblind_map[i] = 0;
  }
 
  for(int peooff_i = 0; peooff_i < p_gaattwicg->count; peooff_i++){
    float p_daroute[DAMODE_1_ELELEN]={0};
    int *p_attele = ga_getele(p_gaattwicg, peooff_i);
    if(p_attele[2] < peopleoff_needpower)  continue;
    p_daroute[DAMODE_1_FLAG_PEOPLEOFF] = 1;
    peocopy.obj_pos =  cvtOffsetIntLocToInt6(p_attele[0], p_attele[1]);

    peocopy.obj_step = 0;
    ocarcopy.obj_pos = peocopy.obj_pos;
    ocarcopy.obj_step = (int)(p_attele[2] - peopleoff_needpower);
    p_daroute[DAMODE_1_LOC_PEOPLEOFF] = ocarcopy.obj_pos;
    p_daroute[DAMODE_1_LEFTPOWER_PEOPLEOFF] = ocarcopy.obj_step;

    struct GA *p_gaattwicg_car = ga_init(0,3,sizeof(int));
    whereICanGoRangeGA(&ocarcopy, p_gaattwicg_car);
    for (int attcardef_i = 0 ; attcardef_i < p_gaattwicg_car->count ; attcardef_i++){
      const int* p_attele_car = ga_getele(p_gaattwicg_car, attcardef_i);
      ocarcopy.obj_pos = cvtOffsetIntLocToInt6(p_attele_car[0], p_attele_car[1]);
      // 更新信息
      ocarcopy.obj_step = p_attele_car[2];
      ocarcopy.obj_blood = p_ocar->obj_blood;
      peocopy.obj_blood = p_opeo->obj_blood;
      ucarcopy.obj_pos = p_ucar->obj_pos;
      ucarcopy.obj_step = ucarcopy.obj_stepmax;
      p_daroute[DAMODE_1_LOC_DEFENCE_A] = ocarcopy.obj_pos;
      // 坦克反击人/反击车分别考虑
      struct GA *p_u_gaffbtroutes_peo = ga_init(0, FFBTMODE_ELELEN, sizeof(float));
      struct GA *p_u_gaffbtroutes_car = ga_init(0, FFBTMODE_ELELEN, sizeof(float));
      float * p_u_bestroute_peo = (float *) malloc( FFBTMODE_ELELEN * sizeof(float));
      float * p_u_bestroute_car = (float *) malloc( FFBTMODE_ELELEN * sizeof(float));
      getFFBTRoutes1000(&ucarcopy , &peocopy, p_tmp_uniondamage_map, p_u_gaffbtroutes_peo);
      bool flag_validbestroute_peo = getBestFFBTRoutes(p_u_gaffbtroutes_peo, FFBTMODE_ELELEN, p_totalblind_map, p_u_bestroute_peo);
      getFFBTRoutes1000(&ucarcopy , &ocarcopy, p_tmp_uniondamage_map, p_u_gaffbtroutes_car);
      bool flag_validbestroute_car = getBestFFBTRoutes(p_u_gaffbtroutes_car, FFBTMODE_ELELEN, p_totalblind_map, p_u_bestroute_car );

      if ( flag_validbestroute_car || flag_validbestroute_peo){ // 对方存在有效攻击:此处存在BUG(对仁任意一方攻击成功都将比较两方的战损（实际上参与比较的另一方战损可能无效）)
	bool flag_attackpeople = false; // 需要将三种情况都进行考虑，避免出现无效数据
	if(flag_validbestroute_car && flag_validbestroute_peo){
	  flag_attackpeople = p_u_bestroute_car[FFBTMODE_SHOOTING_DAMAGELEVEL_A] > p_u_bestroute_peo[FFBTMODE_SHOOTING_DAMAGELEVEL_A] ? false: true;
	} else if (flag_validbestroute_car){
	  flag_attackpeople = false;
	} else if (flag_validbestroute_peo){
	  flag_attackpeople = true;
	}
	const float *p_u_bestroute =  flag_attackpeople ? p_u_bestroute_peo : p_u_bestroute_car;
	p_daroute[DAMODE_1_FLAG_SHOOTING_O] = flag_attackpeople ? 1 : 2;
	p_daroute[DAMODE_1_LOC_SHOOTING_O] =  cvtOffsetIntLocToInt6(p_u_bestroute[FFBTMODE_SHOOTING_ROW_A], p_u_bestroute[FFBTMODE_SHOOTING_COL_A]);
	p_daroute[DAMODE_1_LEFTPOWER_SHOOTING_O] = p_u_bestroute[FFBTMODE_SHOOTING_LEFTPOWER_A];
	p_daroute[DAMODE_1_WEAPONINDEX_O] = p_u_bestroute[FFBTMODE_WEAPENINDEX_A];
	p_daroute[DAMODE_1_DAMAGERESULT_O] = p_u_bestroute[FFBTMODE_SHOOTING_DAMAGELEVEL_A];
	p_daroute[DAMODE_1_LOC_DEFENCEN_O] = cvtOffsetIntLocToInt6(p_u_bestroute[FFBTMODE_DEFENSELOC_ROW_A], p_u_bestroute[FFBTMODE_DEFENSELOC_COL_A]);

	// 更新我方算子的血量
	float real_damage =  flag_attackpeople ? p_daroute[DAMODE_1_DAMAGERESULT_O] / peocopy.obj_value : p_daroute[DAMODE_1_DAMAGERESULT_O] / ocarcopy.obj_value;
	if (flag_attackpeople){
	  peocopy.obj_blood = p_opeo->obj_blood;
	  peocopy.obj_blood = peocopy.obj_blood > real_damage ? round(peocopy.obj_blood - real_damage) : 0;
	} else {
	  // 计算对车的战损的时候，考虑综合战损
	  ocarcopy.obj_blood = p_ocar->obj_blood;
	  real_damage =  max(real_damage, p_uniondamage_map[p_attele_car[0] * MAP_XNUM + p_attele_car[1]]);
	  ocarcopy.obj_blood = p_ocar->obj_blood > real_damage ? round(p_ocar->obj_blood - real_damage) : 0;
	}
	ucarcopy.obj_pos = p_daroute[DAMODE_1_LOC_DEFENCEN_O];
      }else{
	p_daroute[DAMODE_1_FLAG_SHOOTING_O] = 0;
	p_daroute[DAMODE_1_LOC_SHOOTING_O] = -1;
	p_daroute[DAMODE_1_LEFTPOWER_SHOOTING_O] = -1;
	p_daroute[DAMODE_1_WEAPONINDEX_O] = -1;
	p_daroute[DAMODE_1_DAMAGERESULT_O] = 0;
	// p_daroute[DAMODE_1_LOC_DEFENCEN_O] = -1;
      }
      free(p_u_bestroute_peo);
      free(p_u_bestroute_car);
      ga_delete(p_u_gaffbtroutes_car);
      ga_delete(p_u_gaffbtroutes_peo);

      // 我方人车peocopy ocarcopy  攻击对方 ucarcopy 
      float maxvalue_peo = -1; float  maxvalue_car = -1;
      int maxindex_peo = -1; int  maxindex_car = -1;
      if( weaponSelectionForAttacker(&peocopy, &ucarcopy, &maxvalue_peo, &maxindex_peo) || weaponSelectionForAttacker(&ocarcopy, &ucarcopy, &maxvalue_car, &maxindex_car)) {
	p_daroute[DAMODE_1_FLAG_SHOOTING_A] = maxvalue_peo >= maxvalue_car ? 1:2;
	p_daroute[DAMODE_1_WEAPONINDEX_A] = maxvalue_peo >= maxvalue_car ? maxindex_peo : maxindex_car;
	p_daroute[DAMODE_1_DAMAGERESULT_A] = max(maxvalue_car, maxvalue_peo) * ucarcopy.obj_value;
      }else{
	p_daroute[DAMODE_1_FLAG_SHOOTING_A] = 0;
	p_daroute[DAMODE_1_WEAPONINDEX_A] = -1;
	p_daroute[DAMODE_1_DAMAGERESULT_A] = 0;
      }
      p_daroute[DAMODE_1_DAMAGERESULT_FINAL] = p_daroute[DAMODE_1_DAMAGERESULT_A] - p_daroute[DAMODE_1_DAMAGERESULT_O];
      ga_appendele(p_gadaroutes, p_daroute, DAMODE_1_ELELEN, sizeof(float));
    }
    ga_delete(p_gaattwicg_car);
  }
  ga_delete(p_gaattwicg);
  free(p_tmp_uniondamage_map);
  free(p_totalblind_map);
  return;
}

void getDARoutes0100(const struct BasicOperator *p_ocar, const struct BasicOperator *p_opeo, const struct BasicOperator *p_ucar,  const float * p_uniondamage_map, struct GA *p_gadaroutes){
  assert(p_ocar->a1 == 0 && p_ocar->obj_type == 2 && p_opeo->obj_type == 1 && p_ucar->a1 == 0);
  assert(p_ocar->obj_sonnum == 1 /*&& p_ocar->obj_sonid == p_opeo->obj_id  && p_ocar->obj_pos == p_opeo->obj_pos*/ );
  struct BasicOperator ocarcopy = *p_ocar;
  struct BasicOperator peocopy = *p_opeo;
  struct GA *p_gaattwicg = ga_init(0,3,sizeof(int));
  whereICanGoRangeGA(p_ocar, p_gaattwicg);
  float p_daroute[DAMODE_1_ELELEN]={0};
  const int peopleoff_needpower = (int)(p_ocar->obj_stepmax / 2.0);
  for(int peooff_i = 0 ; peooff_i < p_gaattwicg->count; peooff_i ++){
    int *p_attele = ga_getele(p_gaattwicg, peooff_i);
    if(p_attele[2] < peopleoff_needpower)  continue;
    p_daroute[DAMODE_1_FLAG_PEOPLEOFF] = 1;
    peocopy.obj_pos =  cvtOffsetIntLocToInt6(p_attele[0], p_attele[1]);
    ocarcopy.obj_pos = peocopy.obj_pos;
    ocarcopy.obj_step = p_attele[2] - peopleoff_needpower;
    p_daroute[DAMODE_1_LOC_PEOPLEOFF] = peocopy.obj_pos;
    p_daroute[DAMODE_1_LEFTPOWER_PEOPLEOFF] = ocarcopy.obj_step;
    struct GA *p_gaattwicg_car = ga_init(0,3,sizeof(int));
    whereICanGoRangeGA(&ocarcopy, p_gaattwicg_car);
    for (int attcardef_i = 0 ; attcardef_i < p_gaattwicg_car->count ; attcardef_i++){
      const int* p_attele_car = ga_getele(p_gaattwicg_car, attcardef_i);
      ocarcopy.obj_pos = cvtOffsetIntLocToInt6(p_attele_car[0], p_attele_car[1]);
      p_daroute[DAMODE_1_LOC_DEFENCE_A] = ocarcopy.obj_pos;
      // 重置我方算子的血量
      peocopy.obj_blood = p_opeo ->obj_blood;
      ocarcopy.obj_blood = p_ocar->obj_blood;
      // 对方车辆攻击我方人或者车
      float maxvalue_peo, maxvalue_car;
      int maxindex_peo, maxindex_car;
      if ( weaponSelectionForAttacker(p_ucar, &peocopy, &maxvalue_peo, &maxindex_peo) || weaponSelectionForAttacker(p_ucar, &ocarcopy, &maxvalue_car, &maxindex_car)){
  	p_daroute[DAMODE_1_FLAG_SHOOTING_O] = maxvalue_peo > maxvalue_car ? 1 : 2;
	p_daroute[DAMODE_1_LOC_SHOOTING_O] = p_ucar->obj_pos;
	p_daroute[DAMODE_1_LEFTPOWER_SHOOTING_O] = p_ucar->obj_step;
	p_daroute[DAMODE_1_WEAPONINDEX_O] = maxvalue_peo > maxvalue_car ? maxindex_peo: maxindex_car;
	p_daroute[DAMODE_1_DAMAGERESULT_O] = maxvalue_peo > maxvalue_car ? maxvalue_peo * peocopy.obj_value : maxvalue_car * ocarcopy.obj_value;
	if(maxvalue_peo > maxvalue_car){ 
	  peocopy.obj_blood = p_opeo ->obj_blood;
	  peocopy.obj_blood = peocopy.obj_blood > maxvalue_peo ? round(peocopy.obj_blood - maxvalue_peo) : 0;
	} else{
	  // 攻击车时，需要考虑综合战损
	  ocarcopy.obj_blood = p_ocar->obj_blood;
	  maxvalue_car = max(maxvalue_car, p_uniondamage_map[p_attele_car[0] * MAP_XNUM + p_attele_car[1]]);
	  ocarcopy.obj_blood = ocarcopy.obj_blood > maxvalue_car ? round(ocarcopy.obj_blood - maxvalue_car) : 0;
	}
      } else {
      	p_daroute[DAMODE_1_FLAG_SHOOTING_O] = 0;
	p_daroute[DAMODE_1_LOC_SHOOTING_O] = -1;
	p_daroute[DAMODE_1_LEFTPOWER_SHOOTING_O] = -1;
	p_daroute[DAMODE_1_WEAPONINDEX_O] = -1;
	p_daroute[DAMODE_1_DAMAGERESULT_O] = 0;
      }
      // 我方人或车辆攻击对方算子
      if( weaponSelectionForAttacker(&peocopy, p_ucar, &maxvalue_peo, &maxindex_peo) 
	|| weaponSelectionForAttacker(&ocarcopy, p_ucar, &maxvalue_car, &maxindex_car)) {
	p_daroute[DAMODE_1_FLAG_SHOOTING_A] = maxvalue_peo > maxvalue_car ? 1:2;
	p_daroute[DAMODE_1_WEAPONINDEX_A] = maxvalue_peo > maxvalue_car ? maxindex_peo : maxindex_car;
	p_daroute[DAMODE_1_DAMAGERESULT_A] = max(maxvalue_car, maxvalue_peo) * p_ucar->obj_value;
      }else{
	p_daroute[DAMODE_1_FLAG_SHOOTING_A] = 0;
	p_daroute[DAMODE_1_WEAPONINDEX_A] = -1;
	p_daroute[DAMODE_1_DAMAGERESULT_A] = 0;
      }
      p_daroute[DAMODE_1_DAMAGERESULT_FINAL] = p_daroute[DAMODE_1_DAMAGERESULT_A] - p_daroute[DAMODE_1_DAMAGERESULT_O];
      ga_appendele(p_gadaroutes, p_daroute, DAMODE_1_ELELEN, sizeof(float) );
    }
    ga_delete(p_gaattwicg_car);
  }
  ga_delete(p_gaattwicg);
  return;
}

void getDARoutes0010(const struct BasicOperator *p_ocar, const struct BasicOperator *p_ucar, const float * p_uniondamage_map, struct GA * p_gadaroutes)
{  
  assert(p_ocar->obj_sonnum == 0 && p_ocar->a1 == 0 && p_ucar->a1 != 0 && p_uniondamage_map != NULL);
  struct BasicOperator ocarcopy = *p_ocar;
  struct GA *p_attgawicg = ga_init(0,3,sizeof(int));
  whereICanGoRangeGA(p_ocar, p_attgawicg);
  struct BasicOperator ucarcopy = *p_ucar;
  float maxvalue; int maxindex;

  // 暂时不考虑我方所有算子对对方算子的联合战损图
  float* p_tmp_uniondamage_map = (float*) malloc (MAP_XNUM * MAP_YNUM * sizeof(float));
  int* p_totalblind_map = (int*) malloc (MAP_XNUM * MAP_YNUM * sizeof(int));
  for (int i = 0 ; i < MAP_XNUM * MAP_YNUM; i++){
    p_totalblind_map[i] = 0;
    p_tmp_uniondamage_map[i] = 0;
  }

  for (int atts_i = 0 ; atts_i < p_attgawicg->count ; atts_i ++){
    float p_daroute[DAMODE_0_ELELEN] = {0};
    int *p_ele = (int *)ga_getele(p_attgawicg, atts_i);
    ocarcopy.obj_pos = cvtOffsetIntLocToInt6(p_ele[0], p_ele[1]);
    ocarcopy.obj_step = p_ele[2];
    ocarcopy.obj_blood = p_ocar->obj_blood;
    ucarcopy.obj_pos = p_ucar->obj_pos;
    ucarcopy.obj_step = ucarcopy.obj_stepmax;
    ucarcopy.obj_blood = p_ucar->obj_blood;

    // 为对方坦克算子找到最优的攻击位置与躲避位置: 找出对方造成的战损和躲避位置
    float u_damage = 0;
    ucarcopy.obj_pos = p_ucar->obj_pos;
    ucarcopy.obj_step = ucarcopy.obj_stepmax;
    struct GA *p_u_gaffbtroutes = ga_init(0, FFBTMODE_ELELEN, sizeof(float));
    float * p_u_bestroute = (float *) malloc( FFBTMODE_ELELEN * sizeof(float));
    getFFBTRoutes1000(&ucarcopy , &ocarcopy, p_tmp_uniondamage_map, p_u_gaffbtroutes);
    if(getBestFFBTRoutes(p_u_gaffbtroutes, FFBTMODE_ELELEN, p_totalblind_map, p_u_bestroute)){ // 能够为对方找到最优射击点
      u_damage = p_u_bestroute[FFBTMODE_SHOOTING_DAMAGELEVEL_A];
      // 记录对方算子的射击信息
      p_daroute[DAMODE_0_FLAG_SHOOTING_O] = u_damage == 0 ? 0 : 1;
      p_daroute[DAMODE_0_LOC_SHOOTING_O] =cvtOffsetIntLocToInt6(p_u_bestroute[FFBTMODE_SHOOTING_ROW_A],p_u_bestroute[FFBTMODE_SHOOTING_COL_A]);
      p_daroute[DAMODE_0_LEFTPOWER_SHOOTING_O] = p_u_bestroute[FFBTMODE_SHOOTING_LEFTPOWER_A];
      p_daroute[DAMODE_0_WEAPONINDEX_O] = p_u_bestroute[FFBTMODE_WEAPENINDEX_A];
      p_daroute[DAMODE_0_DAMAGERESULT_O] = u_damage;

      // 更新我方算子的血量和对方算子的位置
      float max_real_damage = max(u_damage / ocarcopy.obj_value, p_uniondamage_map[p_ele[0] * MAP_XNUM + p_ele[1]]);
      ocarcopy.obj_blood = ocarcopy.obj_blood > max_real_damage ? round(ocarcopy.obj_blood - max_real_damage) : 0;
      ucarcopy.obj_pos = cvtOffsetIntLocToInt6(p_u_bestroute[FFBTMODE_DEFENSELOC_ROW_A], p_u_bestroute[FFBTMODE_DEFENSELOC_COL_A]);
    } else{
      p_daroute[DAMODE_0_FLAG_SHOOTING_O] = 0;
      p_daroute[DAMODE_0_LOC_SHOOTING_O] = -1;
      p_daroute[DAMODE_0_LEFTPOWER_SHOOTING_O] = ucarcopy.obj_stepmax;
      p_daroute[DAMODE_0_WEAPONINDEX_O] = -1;
      p_daroute[DAMODE_0_DAMAGERESULT_O] = 0;
    }
    ga_delete(p_u_gaffbtroutes);
    free(p_u_bestroute);

    // 计算我方算子射击对方躲避位置的战损
    if(weaponSelectionForAttacker(&ocarcopy, &ucarcopy, &maxvalue, &maxindex)){
      p_daroute[DAMODE_0_FLAG_SHOOTING_A] = 2; // 机动后进行射击（下下阶段射击）
      p_daroute[DAMODE_0_LOC_SHOOTING_A_NEXT] = ocarcopy.obj_pos;
      p_daroute[DAMODE_0_LEFTPOWER_SHOOTING_A_NEXT] = ocarcopy.obj_step;
      p_daroute[DAMODE_0_WEAPONINDEX_A_NEXT] = maxindex;
      p_daroute[DAMODE_0_DAMAGERESULT_A_NEXT] = maxvalue * ucarcopy.obj_value;
    }else{
      p_daroute[DAMODE_0_FLAG_SHOOTING_A] = 0;// 下下阶段也无法进行射击
      p_daroute[DAMODE_0_LOC_SHOOTING_A_NEXT] = ocarcopy.obj_pos;
      p_daroute[DAMODE_0_LEFTPOWER_SHOOTING_A_NEXT] = ocarcopy.obj_step;
      p_daroute[DAMODE_0_WEAPONINDEX_A_NEXT] = -1;  
      p_daroute[DAMODE_0_DAMAGERESULT_A_NEXT] = 0;
    }
    p_daroute[DAMODE_0_DAMAGERESULT_FINAL] = p_daroute[DAMODE_0_DAMAGERESULT_A_NEXT]-p_daroute[DAMODE_0_DAMAGERESULT_O];
    ga_appendele(p_gadaroutes, p_daroute, DAMODE_0_ELELEN, sizeof(float));

    /*显示信息*/
    // printf("战车对坦克的攻击战损 = %f, 战车对坦克的最终战损 = %f\n", p_daroute[DAMODE_0_DAMAGERESULT_A_NEXT], p_daroute[DAMODE_0_DAMAGERESULT_FINAL]);
    // printf("\n");
  }
  ga_delete(p_attgawicg);
  free(p_tmp_uniondamage_map);
  free(p_totalblind_map);
  return;
}


void getDARoutes0000(const struct BasicOperator *p_ocar, const struct BasicOperator *p_ucar, const float * p_uniondamage_map, struct GA * p_gadaroutes)
{
  assert(p_ocar->obj_sonnum == 0 && p_ocar->a1 == 0 && p_ucar->a1 == 0 && p_uniondamage_map != NULL);
  struct BasicOperator ocarcopy = *p_ocar;
  struct GA *p_attgawicg = ga_init(0,3,sizeof(int));
  whereICanGoRangeGA(p_ocar, p_attgawicg);
  float p_daroute[DAMODE_0_ELELEN] = {0};
  float maxvalue; int maxindex;
  // 实现DA模型 
  for (int atts_i = 0 ; atts_i < p_attgawicg->count ; atts_i ++){
    int *p_ele = (int *)ga_getele(p_attgawicg, atts_i);
    ocarcopy.obj_pos = cvtOffsetIntLocToInt6(p_ele[0], p_ele[1]);
    ocarcopy.obj_step = p_ele[2];
    ocarcopy.obj_blood = p_ocar->obj_blood;

    // 敌方算子攻击我方算子
    if (weaponSelectionForAttacker(p_ucar, &ocarcopy, &maxvalue, &maxindex)){
      p_daroute[DAMODE_0_FLAG_SHOOTING_O] = 1;
      p_daroute[DAMODE_0_LOC_SHOOTING_O] = p_ucar->obj_pos;
      p_daroute[DAMODE_0_LEFTPOWER_SHOOTING_O] = p_ucar->obj_stepmax;
      p_daroute[DAMODE_0_WEAPONINDEX_O] = maxindex;
      if (p_ucar->obj_round == 0 && p_ucar->obj_attack == 0 &&( (p_ucar->obj_type == 1 && p_ucar->obj_keep == 0) || (p_ucar->obj_type == 2))) // 未机动/未射击/（如果是人，未压制）：对方可以对我方进行两次射击
	maxvalue *= 2.0;

      // 对方射击我方算子，更新我方算子的血量
      ocarcopy.obj_blood = p_ocar->obj_blood;
      maxvalue = max(maxvalue, p_uniondamage_map[p_ele[0] * MAP_XNUM + p_ele[1]]);
      ocarcopy.obj_blood = ocarcopy.obj_blood > maxvalue ? round(ocarcopy.obj_blood - maxvalue) : 0;
    }else{
      p_daroute[DAMODE_0_FLAG_SHOOTING_O] = 0;
      p_daroute[DAMODE_0_LOC_SHOOTING_O] = -1; p_daroute[DAMODE_0_LEFTPOWER_SHOOTING_O] = -1;
      p_daroute[DAMODE_0_WEAPONINDEX_O] = -1;  p_daroute[DAMODE_0_DAMAGERESULT_O] = 0;      
    }

    // 我方算子攻击敌方算子 
    if (weaponSelectionForAttacker(&ocarcopy, p_ucar, &maxvalue, &maxindex)){
      p_daroute[DAMODE_0_FLAG_SHOOTING_A] = 2;
      p_daroute[DAMODE_0_LOC_SHOOTING_A_NEXT] = ocarcopy.obj_pos;
      p_daroute[DAMODE_0_LEFTPOWER_SHOOTING_A_NEXT] = ocarcopy.obj_step;
      p_daroute[DAMODE_0_WEAPONINDEX_A_NEXT] = maxindex;
      p_daroute[DAMODE_0_DAMAGERESULT_A_NEXT] = maxvalue * p_ucar->obj_value * 1; // 射击对方战车为对方战车的战损*2
    }else{
      p_daroute[DAMODE_0_FLAG_SHOOTING_A] = 0;// 我方算子不射击,即使不射击，也可能导致最优,也需要记录位置
      p_daroute[DAMODE_0_LOC_SHOOTING_A_NEXT] = ocarcopy.obj_pos;
      p_daroute[DAMODE_0_LEFTPOWER_SHOOTING_A_NEXT] = ocarcopy.obj_step;
      p_daroute[DAMODE_0_WEAPONINDEX_A_NEXT] = -1;  p_daroute[DAMODE_0_DAMAGERESULT_A_NEXT] = 0;
    }
    p_daroute[DAMODE_0_DAMAGERESULT_FINAL] = p_daroute[DAMODE_0_DAMAGERESULT_A_NEXT]-p_daroute[DAMODE_0_DAMAGERESULT_O];
    ga_appendele(p_gadaroutes, p_daroute, DAMODE_0_ELELEN, sizeof(float));
  }
  ga_delete(p_attgawicg);
  return;
}

bool getBestDAroute(const struct GA * p_gadaroutes, const int flag_withpeople, const int ele_len, const int *p_totalblind_map, const int flag_task , float *p_route)
{
  assert(p_gadaroutes != NULL && p_route != NULL && p_totalblind_map != NULL);
  assert((flag_withpeople == 0 && ele_len == DAMODE_0_ELELEN) || (flag_withpeople == 1 && ele_len == DAMODE_1_ELELEN));
  assert(p_totalblind_map!= NULL ); 
  // assert(flag_task >= 0 && flag_task <= 2); // 0 进攻/ 1防守 / 撤退2

  float max_reward = 1;
  int min_blindlevel = 10000;
  bool max_flag_incover = false;
  int max_leftpow = -1;
  int max_routeindex = -100;
  float max_error_reward = 0.5; // 给定一个战损(乘以分值之后的)容错率（当两条路径的战损相差不多时候，给以其他标准一定的选择机会）
  // 初始化
  for (int i = 0 ; i < ele_len ; i++)
    p_route[i] = 0;

  switch (flag_withpeople){
    case 0:{ // 处理DA中不载人的最优路径选择
      int num_invalid = 0;
      for(int route_i = 0 ; route_i < p_gadaroutes->count; route_i ++){
	float *p_ele= (float*) ga_getele(p_gadaroutes, route_i);
	if (p_ele[DAMODE_0_DAMAGERESULT_A_NEXT] == 0 && p_ele[DAMODE_0_DAMAGERESULT_O] == 0)
	  num_invalid ++;
      }
      float ratio_samereward = (float)(num_invalid) /(p_gadaroutes->count + 0.0001);
      bool flag_iou_ok = ratio_samereward  >= 0.95 ? false: true;
      if (flag_iou_ok == false){
	//printf("\t\tgetBestDAroute： 攻击算子与目标算子互相不可见(ratio_samereward = %f)\n", ratio_samereward);
	return false;
      }

      // 先求出一个最大max_reward以及其对应的max_routeindex; 然后以一定的容错考虑其他最优条件
      for(int route_i = 0 ; route_i < p_gadaroutes->count; route_i ++){
      	float *p_ele= (float*) ga_getele(p_gadaroutes, route_i);
	float cur_reward = p_ele[DAMODE_0_DAMAGERESULT_FINAL];
	if (cur_reward > max_reward){
	  max_reward = cur_reward;
	  max_routeindex = route_i;
	}
      }
      // 保证最大战损合格
      if (max_reward <= max_error_reward){
	return false;
      }

      for(int route_i = 0 ; route_i < p_gadaroutes->count; route_i ++){
	float *p_ele= (float*) ga_getele(p_gadaroutes, route_i);
	float cur_reward = p_ele[DAMODE_0_DAMAGERESULT_FINAL];
	const int tmp_int4loc =cvtInt6loc2Int4loc((int) p_ele[DAMODE_0_LOC_SHOOTING_A_NEXT]);
	const struct HexOfOffset tmploc_hex = {tmp_int4loc/100, tmp_int4loc%100};
	int cur_blindlevel = p_totalblind_map[tmploc_hex.row * MAP_XNUM + tmploc_hex.col];
	bool cur_flag_incover = checkHexIsInCover(&tmploc_hex) == 1? true: false;
	int cur_leftpow = p_ele[DAMODE_0_LEFTPOWER_SHOOTING_A_NEXT];
	if( (fabs(cur_reward - max_reward) <= max_error_reward && cur_blindlevel < min_blindlevel) ||
	    (fabs(cur_reward - max_reward) <= max_error_reward && cur_blindlevel == min_blindlevel && cur_flag_incover == true && max_flag_incover == false) || 
	    (fabs(cur_reward - max_reward) <= max_error_reward && cur_blindlevel == min_blindlevel && cur_flag_incover == max_flag_incover && cur_leftpow > max_leftpow) ){
	  min_blindlevel = cur_blindlevel;
	  max_flag_incover = cur_flag_incover;
	  max_leftpow = cur_leftpow;
	  max_routeindex = route_i;
	}
      }
      // assert(max_routeindex >=0);
      if (max_routeindex < 0){return false;}
      const float *p_ele = (float*) ga_getele(p_gadaroutes, max_routeindex);
      memcpy(p_route, p_ele, DAMODE_0_ELELEN * sizeof(float));
      break;
    }

    case 1:{ 
      
      bool max_flag_incover_car = false;
      bool max_flag_incover_peo = false;
      int count_samereward = 0;
      for(int route_i = 0 ;  route_i < p_gadaroutes->count ; route_i ++){
	const float a_reward = ((float *) ga_getele(p_gadaroutes, route_i))[DAMODE_1_DAMAGERESULT_A];
        const float o_reward = ((float *) ga_getele(p_gadaroutes, route_i))[DAMODE_1_DAMAGERESULT_O];
	if (a_reward == o_reward && a_reward == 0)
	  count_samereward++;
      }
      float ratio_samereward = ((float)count_samereward) / (p_gadaroutes->count + 1);
      bool flag_iou_ok = ratio_samereward >= 0.99 ? false : true;
      if ( flag_iou_ok == false ) { // 候选路径几乎无效（攻击算子与目标算子之间距离较远）
	return false;
      }

      // 找出最大战损max_reward以及对应的max_routeindex
      for(int route_i = 0; route_i < p_gadaroutes->count; route_i ++){
	float *p_ele = (float *) ga_getele(p_gadaroutes, route_i);
	float cur_reward =  p_ele[DAMODE_1_DAMAGERESULT_FINAL];
	if (cur_reward > max_reward){
	  max_reward = cur_reward;
	  max_routeindex = route_i;
	}
      }
      if(max_reward <= max_error_reward){ // 保证我方占优势(综合战损要>0)
	return false;
      }

      for(int route_i = 0; route_i < p_gadaroutes->count; route_i ++){
	float *p_ele = (float *) ga_getele(p_gadaroutes, route_i);
	float cur_reward =  p_ele[DAMODE_1_DAMAGERESULT_FINAL];
	const int tmp_int4loc_peo = cvtInt6loc2Int4loc((int) p_ele[DAMODE_1_LOC_PEOPLEOFF]);
	const struct HexOfOffset tmploc_hex_peo = {tmp_int4loc_peo/100, tmp_int4loc_peo%100};
	const int tmp_int4loc_car = cvtInt6loc2Int4loc((int)p_ele[DAMODE_1_LOC_DEFENCE_A]);
	const struct HexOfOffset tmploc_hex_car = {tmp_int4loc_car/100, tmp_int4loc_car%100};
	const int cur_blindlevel = p_totalblind_map[tmploc_hex_car.row * MAP_XNUM + tmploc_hex_car.col];
	bool cur_flag_incover_car = checkHexIsInCover(&tmploc_hex_car);
	bool cur_flag_incover_peo = checkHexIsInCover(&tmploc_hex_peo);
	
	if( (fabs(cur_reward - max_reward) <= max_error_reward && cur_blindlevel < min_blindlevel ) ||
	    (fabs(cur_reward - max_reward) <= max_error_reward && cur_blindlevel == min_blindlevel && max_flag_incover_car == false && cur_flag_incover_car == true) || 
	    (fabs(cur_reward - max_reward) <= max_error_reward && cur_blindlevel == min_blindlevel && max_flag_incover_car == cur_flag_incover_car && max_flag_incover_peo == false && cur_flag_incover_peo == true) ){
	  min_blindlevel = cur_blindlevel;
	  max_flag_incover_car = cur_flag_incover_car;
	  max_flag_incover_peo = cur_flag_incover_peo;
	  max_routeindex = route_i;
	}
      }
      // assert(max_routeindex >= 0);
      if(max_routeindex < 0){return false;}
      float *p_ele = (float*) ga_getele(p_gadaroutes, max_routeindex);
      memcpy(p_route, p_ele, DAMODE_1_ELELEN * sizeof(float));
      break;
    }
    default:{
      break;
    }
  } 
  return true;
}


void cvtDARoute2AIAction(const struct BasicOperator *p_bopattacker,  const struct BasicOperator *p_bopobj,  const int flag_withpeople, const int daroute_ele,  const float * p_daroute, const int aiaction_len, float * p_aiaction )
{
  //注意p_bestroute已经是选择出来最优动作
  assert(p_daroute != NULL && p_aiaction != NULL);
  if (flag_withpeople != 1 && flag_withpeople != 0){
    printf("flag_withpeople = %d\n", flag_withpeople);
    while(1){;}
  }
  assert( (flag_withpeople == 0 && daroute_ele == DAMODE_0_ELELEN) || (flag_withpeople == 1 && daroute_ele == DAMODE_1_ELELEN));
  assert(aiaction_len == AIACTION_ELELEN);
  switch(flag_withpeople) {
    case 0:{ // 不载人DA路径
      bool flag_move =  p_bopattacker->obj_pos != (int)(p_daroute[DAMODE_0_LOC_SHOOTING_A_NEXT]);
      if (flag_move == false ){ // 原地不动
	p_aiaction[0] = AIACTION_DONOTHING;
	p_aiaction[1] = p_bopattacker->obj_id;
	p_aiaction[2] = p_daroute[DAMODE_0_DAMAGERESULT_FINAL];
      } else { // 仅移动动作
	struct GA *p_gapartpath = ga_init(0,3,sizeof(int));
	struct GA *p_gafullpath = ga_init(0,3,sizeof(int));
	struct HexOfOffset move_objhex = {0,0};
	char chars_6_loc[7];
	cvtIntLocTo4StrOffLoc( (int)(p_daroute[DAMODE_0_LOC_SHOOTING_A_NEXT]) , chars_6_loc, 7);
	cvtChars6locToOffsetIntLoc(chars_6_loc, &(move_objhex.row) , &(move_objhex.col));
	trendpathP2P(p_bopattacker, &move_objhex, p_gafullpath, p_gapartpath);
	int hexnum_inpath = p_gapartpath->count - 1 ;
	if(!(hexnum_inpath <= 7 && hexnum_inpath >0)){
	  ga_delete(p_gapartpath); ga_delete(p_gafullpath);
	  p_aiaction[0] = AIACTION_INVALID;
	  return;
	}
	p_aiaction[0] = AIACTION_MOVEONLY;
	p_aiaction[1] = p_bopattacker->obj_id;
	p_aiaction[2] = hexnum_inpath;

	for(int i = 3; i < 3 + hexnum_inpath ; i++){
	  const int *p_ele = ga_getele(p_gapartpath, i - 3 + 1);
	  p_aiaction[i] = cvtOffsetIntLocToInt6(p_ele[0], p_ele[1]);
	}
	p_aiaction[18] = p_daroute[DAMODE_0_DAMAGERESULT_FINAL];
	ga_delete(p_gapartpath); ga_delete(p_gafullpath);
      }
      break;
    }
    case 1:{ // 处理载人DA路径
      // 下车前半段
      bool flag_move_0 = p_bopattacker->obj_pos != p_daroute[DAMODE_1_LOC_PEOPLEOFF] ? true:false;
      struct GA *p_gapartpath_0 = ga_init(0,3,sizeof(int));
      struct GA *p_gafullpath_0 = ga_init(0,3,sizeof(int));
      struct HexOfOffset move_objhex = {0,0};
      int hexnum_inpath_0 = 0;
      char chars_6_loc[7];
      if (flag_move_0 ){
	cvtIntLocTo4StrOffLoc( (int)(p_daroute[DAMODE_1_LOC_PEOPLEOFF]) , chars_6_loc, 7);
	cvtChars6locToOffsetIntLoc(chars_6_loc, &(move_objhex.row) , &(move_objhex.col));
	if (!trendpathP2P(p_bopattacker, &move_objhex, p_gafullpath_0, p_gapartpath_0)){
	  ga_delete(p_gapartpath_0); ga_delete(p_gafullpath_0);
	  p_aiaction[0] = AIACTION_INVALID;
	  return;
	}
	hexnum_inpath_0 = p_gapartpath_0->count - 1 ;
      } 
      // 下车后半段
      bool flag_move_1 = (int)(p_daroute[DAMODE_1_LOC_DEFENCE_A]) != (int)(p_daroute[DAMODE_1_LOC_PEOPLEOFF]) ? true:false;
      struct GA *p_gapartpath_1 = ga_init(0,3,sizeof(int));
      struct GA *p_gafullpath_1 = ga_init(0,3,sizeof(int));
      int hexnum_inpath_1 = 0;
      if (flag_move_1){
	struct BasicOperator attackercopy = *p_bopattacker;
	cvtIntLocTo4StrOffLoc( (int)(p_daroute[DAMODE_1_LOC_DEFENCE_A]) , chars_6_loc, 7);
	cvtChars6locToOffsetIntLoc(chars_6_loc, &(move_objhex.row) , &(move_objhex.col));
	attackercopy.obj_pos = (int)(p_daroute[DAMODE_1_LOC_PEOPLEOFF]);
	attackercopy.obj_step = (int)(p_daroute[DAMODE_1_LEFTPOWER_PEOPLEOFF]);
	if (!trendpathP2P(&attackercopy, &move_objhex, p_gafullpath_1, p_gapartpath_1)){
	  ga_delete(p_gapartpath_0); ga_delete(p_gafullpath_0);
	  ga_delete(p_gapartpath_1); ga_delete(p_gafullpath_1);
	  p_aiaction[0] = AIACTION_INVALID;
	  return;
	}
	hexnum_inpath_1 = p_gapartpath_1->count - 1 ;
      } 

      if(p_daroute[DAMODE_1_FLAG_PEOPLEOFF] == 0){
	p_aiaction[0] = AIACTION_INVALID;
      } else { // 人下车：机动下车/ 下车机动 / 机动下车机动 / 仅下车
	p_aiaction[1] = p_bopattacker->obj_id;
	if (flag_move_0 == true){  // 首先机动
	  if(flag_move_1 == false ){ // 机动下车
	    p_aiaction[0] = AIACTION_MOVEGETOFF;
	    p_aiaction[2] = hexnum_inpath_0;
	    for (int i = 3 ; i < hexnum_inpath_0 + 3 ; i ++){
	      const int *p_ele = ga_getele(p_gapartpath_0, i - 3 + 1);
	      p_aiaction[i] = cvtOffsetIntLocToInt6(p_ele[0],p_ele[1]);
	    }
	    p_aiaction[3 + hexnum_inpath_0] = p_bopattacker->obj_sonid;
	    //p_aiaction[3 + hexnum_inpath_0] = p_bopattacker->obj_id;

	    p_aiaction[18] = p_daroute[DAMODE_1_DAMAGERESULT_FINAL];

	  } else{ // 机动下车机动
	    p_aiaction[0] = AIACTION_MOVEGETOFFMOVE;
	    p_aiaction[2] = hexnum_inpath_0;
	    for (int i = 3 ; i < hexnum_inpath_0 + 3 ; i ++){
	      const int *p_ele = ga_getele(p_gapartpath_0, i - 3 + 1);
	      p_aiaction[i] = cvtOffsetIntLocToInt6(p_ele[0],p_ele[1]);
	    }
	    p_aiaction[3 + hexnum_inpath_0] = p_bopattacker->obj_sonid;
	    // p_aiaction[3 + hexnum_inpath_0] = p_bopattacker->obj_id;
	    // 继续移动
	    p_aiaction[4 + hexnum_inpath_0] = hexnum_inpath_1;
	    for(int i = 5  + hexnum_inpath_0 ; i < 5 + hexnum_inpath_0 + hexnum_inpath_1; i++ ){
	      const int *p_ele = ga_getele(p_gapartpath_1, i - 5 - hexnum_inpath_0 + 1);
	      p_aiaction[i] = cvtOffsetIntLocToInt6(p_ele[0],p_ele[1]);
	    }
	    p_aiaction[18] = p_daroute[DAMODE_1_DAMAGERESULT_FINAL];
	  }
	} else { // 首先下车： 仅下车 或者 下车机动
	  if (flag_move_1 == false ){ // 仅仅下车
	    p_aiaction[0] = AIACTION_GETOFFONLY;
	    p_aiaction[2] = p_bopattacker->obj_sonid;
	    //p_aiaction[2] = p_bopattacker->obj_id;
	    p_aiaction[18] = p_daroute[DAMODE_1_DAMAGERESULT_FINAL];
	  } else { // 原地下车后机动
	    p_aiaction[0] = AIACTION_GETOFFMOVE;
	    p_aiaction[2] = p_bopattacker->obj_sonid;
	    p_aiaction[3] = hexnum_inpath_1;
	    for(int i = 4 ; i < 4 + hexnum_inpath_1; i++){
	      const int *p_ele = ga_getele(p_gapartpath_1, i - 4 + 1);
	      p_aiaction[i] = cvtOffsetIntLocToInt6(p_ele[0],p_ele[1]);
	    }
	    p_aiaction[18] = p_daroute[DAMODE_1_DAMAGERESULT_FINAL];
	  }
	}
      }
      ga_delete(p_gapartpath_0);      ga_delete(p_gapartpath_1);
      ga_delete(p_gafullpath_0);      ga_delete(p_gafullpath_1);
      break;
    }
    default:{
      break;
    }
  }
  return;
}

void cvtStaticShooting2AIAction(const struct BasicOperator *p_attacker,const struct BasicOperator *p_obj, const int len, float *p_aiaction )
{
   assert(len == AIACTION_ELELEN && p_aiaction != NULL);
   float maxvalue = -1;
   int maxindex =-1;
   if (weaponSelectionForAttacker(p_attacker, p_obj, &maxvalue, &maxindex)){
      p_aiaction[0] = AIACTION_SHOOTONLY;
      p_aiaction[1] = p_attacker->obj_id;
      p_aiaction[2] = p_obj->obj_id;
      p_aiaction[3] = p_attacker->p_obj_wpids[maxindex];
      p_aiaction[4] = maxvalue * p_obj->obj_value;
    } else { // 无效动作
      // printf("%d 不能攻击 %d\n", p_attacker->obj_id, p_obj->obj_id);
      p_aiaction[0] = AIACTION_INVALID;
    }
    return;
}

void cvtRushMoving2AIAction(const struct BasicOperator *p_attacker, const int obj_int6loc,  const int len , float * p_aiaction )
{
  assert(len == AIACTION_ELELEN && p_aiaction != NULL);
  assert(p_attacker->obj_step > 0);

  const int src_int4loc = cvtInt6loc2Int4loc(p_attacker->obj_pos);
  const struct HexOfOffset src_hex = {src_int4loc / 100, src_int4loc % 100};
  const int obj_int4loc = cvtInt6loc2Int4loc(obj_int6loc);
  struct HexOfOffset obj_hex = {obj_int4loc / 100, obj_int4loc % 100};
  assert(checkHexIsValid(&obj_hex) && checkHexIsValid(&src_hex));

  // 选择机动方式：flag_choosestage == 0 机动 、 1 行军、 -1 不能机动与行军（直接返回无效动作）、2 机动行军都可以
  int flag_choosestage = -1;
  if(p_attacker->obj_type == 1){ // 人员算子
    if (p_attacker->obj_pass < 0 || p_attacker->obj_pass > 2){
      printf("人员算子的obj_pass = %d\n", p_attacker->obj_pass);
    }
    flag_choosestage = p_attacker->obj_pass <= 1 ? 0 : -1 ; // 人员算子在未行军/1级疲劳的状态下可以进行机动；2级疲劳不能机动
  } else if (p_attacker->obj_type == 2){ //车辆算子
    assert(p_attacker->obj_pass == 0 || p_attacker->obj_pass == 1);
    bool flag_initIsPass = p_attacker->obj_pass; // 初始阶段是否是行军(1) / 未行军（0）
    bool flag_swtichstage = p_attacker->obj_step == p_attacker->obj_stepmax ? true : false; // 是否允许切换状态
    flag_choosestage = flag_swtichstage ? 2 : flag_initIsPass; 
    flag_choosestage = checkHexIsRoad(&src_hex) ? flag_choosestage : 0; 
    if (flag_choosestage == 2)
      flag_choosestage = stateSelectionForRushMoving(p_attacker, obj_int6loc) ? 0 : 1;
  } 
  // printf("flag_choosestage = %d\n", flag_choosestage);
  // 规划路径
  if (flag_choosestage == -1 ){
    p_aiaction[0] = AIACTION_INVALID;
    return;
  }
  struct GA *p_gafullpath = ga_init(0,3,sizeof(int));
  struct GA *p_gapartpath = ga_init(0,3,sizeof(int));
  bool flag_pathexist = false;
  if (flag_choosestage == 0){
    flag_pathexist = trendpathP2P(p_attacker, &obj_hex, p_gafullpath, p_gapartpath);
  } else {
    flag_pathexist = trendpathP2P4Pass(p_attacker, &obj_hex, p_gafullpath, p_gapartpath);
    if (!flag_pathexist){
      flag_choosestage = 0;
      flag_choosestage = trendpathP2P(p_attacker, &obj_hex, p_gafullpath, p_gapartpath);
    }
  }
  if(!flag_pathexist){
    p_aiaction[0] = AIACTION_INVALID;
    ga_delete(p_gapartpath); ga_delete(p_gafullpath);
    return;
  }

  // 转换成AI可识别的指令字段
  p_aiaction[0] =  flag_choosestage == 0 ? AIACTION_MOVEONLY : AIACTION_PASSONLY;
  p_aiaction[1] = p_attacker->obj_id;
  const int hexnum_inpath = p_gapartpath->count - 1;
  p_aiaction[2] =  hexnum_inpath;
  for (int i = 3 ; i < 3 + hexnum_inpath; i++){
    const int *p_ele = ga_getele(p_gapartpath, i - 3 + 1  );
    p_aiaction[i] = cvtOffsetIntLocToInt6(p_ele[0],p_ele[1]);
  }
  ga_delete(p_gapartpath); ga_delete(p_gafullpath);
  return;
}

bool stateSelectionForRushMoving(const struct BasicOperator *p_attacker, const int obj_int6loc)
{
  const int src_int4loc = cvtInt6loc2Int4loc(p_attacker->obj_pos);
  const struct HexOfOffset src_hex = {src_int4loc / 100, src_int4loc % 100};
  if (!checkHexIsRoad(&src_hex) || p_attacker->obj_type == 1){ // 算子初始位置不在道路上 或者 算子本身是人员算子
    return true; 
  }
  int diff_go = getErrorForSpecifiedMovingForm(p_attacker, obj_int6loc, true);
  int diff_pass = getErrorForSpecifiedMovingForm(p_attacker, obj_int6loc, false);
  return diff_go <= diff_pass ? true : false;
}

int getErrorForSpecifiedMovingForm(const struct BasicOperator *p_attacker , const int obj_int6loc, const bool flag_go)
{
  int min_distance = 1000;
  const int src_int4loc = cvtInt6loc2Int4loc(p_attacker->obj_pos);
  const struct HexOfOffset src_hex = {src_int4loc / 100, src_int4loc % 100};
  if (!checkHexIsRoad(&src_hex) && (!flag_go) ){ // 算子不在道路上，行军误差=无穷大
    return min_distance;
  }

  // 误差计算
  const int obj_int4loc = cvtInt6loc2Int4loc(obj_int6loc);
  struct HexOfOffset obj_hex = {obj_int4loc / 100, obj_int4loc % 100};
  struct dictionary *p_dicwicg = dic_new(0, sizeof(int));
  if (flag_go)
    whereICanGoRange(p_attacker, p_dicwicg);
  else 
    whereICanPassRange(p_attacker, p_dicwicg);
  for (int i = 0; i < p_dicwicg->length; i++) {
    if (p_dicwicg->table[i] != 0) {
      struct keynode *k = p_dicwicg->table[i];
      while (k) {
	int tmp_4loc = atoi(k->key);
	const struct HexOfOffset tmp_hex = {tmp_4loc / 100, tmp_4loc % 100};
	int tmp_distance = getDistanceBetweenHexOfOffset(&tmp_hex, &obj_hex);
	if (min_distance > tmp_distance){
	  min_distance = tmp_distance;
	}
	k = k->next;
      }
    }
  }

  dic_delete(p_dicwicg);
  return min_distance;
}

void rushAiDamageLevelP2P(const struct BasicOperator *p_attacker, const struct BasicOperator *p_obj, const int shootingtype,
			  const float * p_comicumap, float *p_shootingarray)
{
  //  bool flag_fill = false;
  assert(shootingtype >=1 && shootingtype < 5);
  struct HexOfOffset objhex, atthex;
  getLocOfOffsetFromOperator(p_attacker, &atthex.row, &atthex.col);
  getLocOfOffsetFromOperator(p_obj, &objhex.row, &objhex.col);
  int distance = getDistanceBetweenHexOfOffset(&objhex, &atthex);
  p_shootingarray[RUSHMODE_SHOOTING_DISTANCE] = (float) distance;
  p_shootingarray[RUSHMODE_SHOOTING_ELEDIFF] = getMyElevation(&atthex) - getMyElevation(&objhex);

  p_shootingarray[RUSHMODE_SHOOTING_TYPE] = 0;
  if(shootingtype >=2 && shootingtype <= 4){ // 静态射击 2 3 4 
    p_shootingarray[RUSHMODE_SHOOTING_MOVEHEXNUM] = 0;
    p_shootingarray[RUSHMODE_SHOOTING_ROW] = atthex.row;
    p_shootingarray[RUSHMODE_SHOOTING_COL] = atthex.col;
    p_shootingarray[RUSHMODE_SHOOTING_LEFTPOWER] = p_attacker->obj_step;
    float max_damagelevel = -1;
    int max_weapenindex =-1;
    for(int weapenindex = 0; weapenindex < p_attacker->obj_wznum ; weapenindex ++){
      float tmp_damagelevel = damagelevelP2P(p_attacker, p_obj, weapenindex );
      if(tmp_damagelevel > max_damagelevel){
	max_weapenindex = weapenindex; max_damagelevel = tmp_damagelevel;
      }
    }
    if(max_damagelevel>-1){ // 此攻击为有效攻击,设置p_shootingarray并返回
      //  flag_fill = true;
      p_shootingarray[RUSHMODE_SHOOTING_TYPE] = shootingtype;
      p_shootingarray[RUSHMODE_SHOOTING_WZINDEX] = max_weapenindex;
      p_shootingarray[RUSHMODE_SHOOTING_DAMAGELEVEL] = max_damagelevel;
      p_shootingarray[RUSHMODE_SHOOTING_ATTACKLEVEL] =attacklevelP2P(p_attacker, p_obj, max_weapenindex);
    }
  }
  else{ // 动态射击 1
    // printf("验证是否可以进行动态射击？\n");
    struct GA *p_gawicg = ga_init(0, 3, sizeof(int));
    struct BasicOperator attcopy = *p_attacker;
    float max_damagelevel = -1;
    int max_weapenindex =-1;
    int max_locindex = -1;
    whereICanGoRangeGA(&attcopy,p_gawicg);
    for(int locindex = 0 ; locindex < p_gawicg->count ; locindex ++){
      int* p_ele = (int*)ga_getele(p_gawicg, locindex);
      updateOperatorLoc(&attcopy,p_ele[0], p_ele[1]);
      for (int weapenindex= 0 ; weapenindex < p_attacker->obj_wznum; weapenindex++ ){
	float tmp_damagelevel = damagelevelP2P(&attcopy, p_obj, weapenindex);
	if(tmp_damagelevel > max_damagelevel){
	  max_weapenindex = weapenindex; max_damagelevel = tmp_damagelevel; max_locindex = locindex;
	}
      }
    }
    if(max_damagelevel>-1){
      //   flag_fill = true;
      const int * max_p_ele =(int*) ga_getele(p_gawicg, max_locindex);
      p_shootingarray[RUSHMODE_SHOOTING_ROW] = max_p_ele[0];
      p_shootingarray[RUSHMODE_SHOOTING_COL] = max_p_ele[1];
      p_shootingarray[RUSHMODE_SHOOTING_LEFTPOWER] = max_p_ele[2];
      p_shootingarray[RUSHMODE_SHOOTING_TYPE] = shootingtype;
      p_shootingarray[RUSHMODE_SHOOTING_WZINDEX] = max_weapenindex;
      p_shootingarray[RUSHMODE_SHOOTING_DAMAGELEVEL] = max_damagelevel;
      updateOperatorLoc(&attcopy,max_p_ele[0], max_p_ele[1]);
      p_shootingarray[RUSHMODE_SHOOTING_ATTACKLEVEL] = attacklevelP2P(&attcopy, p_obj, max_weapenindex);
      
      // 记录（中间路径六角格6位数坐标，剩余机动力）
      struct GA *p_gafullpath = ga_init(0,3,sizeof(int));
      struct GA *p_gapartpath = ga_init(0,3,sizeof(int));
      struct HexOfOffset shootinghex = {max_p_ele[0], max_p_ele[1]};
      trendpathP2P(p_attacker, &shootinghex, p_gafullpath, p_gapartpath);
      int hexnum_inpath = p_gapartpath->count - 1 ;
      assert(hexnum_inpath <= 7);
      p_shootingarray[RUSHMODE_SHOOTING_MOVEHEXNUM] = hexnum_inpath;
      for (int i = 1 ; i <= hexnum_inpath ; i ++ ){
	const int *p_ele = (int*) ga_getele(p_gapartpath, i);
	p_shootingarray[RUSHMODE_SHOOTING_MOVEHEXNUM + 1 + (i-1) * 2 + 0] = cvtOffsetIntLocToInt6(p_ele[0], p_ele[1]);
	p_shootingarray[RUSHMODE_SHOOTING_MOVEHEXNUM + 1 + (i-1) * 2 + 1] = p_ele[2];
      }
      
      ga_delete(p_gafullpath);
      ga_delete(p_gapartpath);
    }
    ga_delete(p_gawicg);
  }
  //  if (flag_fill == true)
  //	printf("shootin infos in c :%f, %f, %f\n", p_shootingarray[RUSHMODE_SHOOTING_TYPE],p_shootingarray[RUSHMODE_SHOOTING_ROW], p_shootingarray[RUSHMODE_SHOOTING_COL]);
  return;
}			    


void rushAiOptNextRoute(const struct BasicOperator *p_bop, const struct HexOfOffset *p_objhex, float *p_moveroutearray)
{
 
  struct GA *p_gafullpath = ga_init(0,3,sizeof(int));
  struct GA *p_gapartpath = ga_init(0,3,sizeof(int));
  trendpathP2P(p_bop, p_objhex, p_gafullpath, p_gapartpath);
  // printf("part count = %d\n", p_gapartpath->count);
  p_moveroutearray[RUSHMODE_MOVEROUTE_FLAG] = 0;
  if(p_gapartpath->count >= 2)
  {
    p_moveroutearray[RUSHMODE_MOVEROUTE_FLAG] = 1; // 能够机动，设置机动标志位
    //const int lastindex = p_gapartpath->count - 1;
    const int lastindex =  1;
    const int *p_ele = (int*) ga_getele(p_gapartpath, lastindex); // 最后一个位置的信息
    p_moveroutearray[RUSHMODE_MOVEROUTE_ROW] = p_ele[0];
    p_moveroutearray[RUSHMODE_MOVEROUTE_COL] = p_ele[1];
    p_moveroutearray[RUSHMODE_MOVEROUTE_LEFTPOWER] = p_ele[2];
  }
  ga_delete(p_gafullpath);
  ga_delete(p_gapartpath);
  return;
}

bool getOccupyingRoutes(const struct BasicOperator* p_bop, const int int_cityloc6, const float * p_totaldamage_map, struct GA * p_ga_occupyingroutes)
{
  // 检查
  bool flag_validpointer = p_bop != NULL && p_totaldamage_map != NULL && p_ga_occupyingroutes != NULL;
  struct HexOfOffset hex_bop = {0,0};
  getLocOfOffsetFromOperator(p_bop, &(hex_bop.row), &(hex_bop.col));
  int int_cityloc4 = cvtInt6loc2Int4loc(int_cityloc6);
  struct HexOfOffset hex_city = {int_cityloc4 / 100, int_cityloc4 % 100};
  bool flag_validcityloc = checkHexIsValid(&hex_bop) && checkHexIsValid(&hex_city);
  if (!(flag_validcityloc && flag_validpointer)){
    printf("error in getOccupyingRoutes() - flag_validpointer or flag_validcityloc is False\n");
    return false;
  }

  // p_bop是否能够达到城市点（剩余机动力>=0）
  bool flag_validroutes = false;
  struct dictionary *p_attdicwicg = dic_new(0,sizeof(int));
  whereICanGoRange(p_bop, p_attdicwicg);
  char chars_cityloc4[5] = {'0'};
  cvtIntLocTo4StrOffLoc(int_cityloc4, chars_cityloc4, 5);
  if (!dic_find(p_attdicwicg, chars_cityloc4, 5)){ // 当前算子的机动力不能达到夺控点
     //printf("int_cityloc4 == %d , int_cityloc6 = %d \n", int_cityloc4, int_cityloc6);
    flag_validroutes = false;
  }else{
    flag_validroutes = true;
    int leftpow_city = *((int*)(p_attdicwicg->p_findvalue));
    assert(leftpow_city >= 0);
    float damage_city = p_totaldamage_map[hex_city.row * MAP_XNUM + hex_city.col];

    // 遍历躲避位置
    struct BasicOperator bop_copy = *p_bop;
    bop_copy.obj_step = leftpow_city;
    bop_copy.obj_pos = cvtOffsetIntLocToInt6(hex_city.row, hex_city.col);

    struct GA * p_gawicg = ga_init(0, 3, sizeof(int));
    whereICanGoRangeGA(&bop_copy, p_gawicg);
    float p_cur_route[OCCUMODE_ELELEN] = {0.f};
    p_cur_route[OCCUMODE_LOC_CITY] = int_cityloc4; // 使用4位坐标
    p_cur_route[OCCUMODE_LEFTPOWER_CITY] = leftpow_city;
    p_cur_route[OCCUMODE_DAMAGE_CITY] = damage_city;
    for (int i = 0 ; i < p_gawicg->count; i++){
      int *p_ele = (int*)ga_getele(p_gawicg, i);
      p_cur_route[OCCUMODE_LOC_HIDEN] = p_ele[0] * 100 + p_ele[1];
      p_cur_route[OCCUMODE_LEFTPOWER_HIDEN] = p_ele[2];
      p_cur_route[OCCUMODE_DAMAGE_HIDEN] = p_totaldamage_map[p_ele[0] * MAP_XNUM + p_ele[1]];
      ga_appendele(p_ga_occupyingroutes, p_cur_route, OCCUMODE_ELELEN, sizeof(float) );
    }
    ga_delete(p_gawicg);
  }
  dic_delete(p_attdicwicg);
  return flag_validroutes;
}


bool getBestOccupyingRoute(const struct GA *p_ga_occupyingroutes, float *p_best_route)
{
  // 检查
  bool flag_validpointers = p_ga_occupyingroutes != NULL && p_best_route != NULL;
  bool flag_validroutes = p_ga_occupyingroutes->count > 0;
  if (!flag_validpointers){
    printf("error in getBestOccupyingRoute() - flag_validpointers  or flag_validroutes is false\n");
    return false;
  }
  if (!flag_validroutes){ // 没有候选路径
    return false;
  }
  
  // 按照标准筛选最优
  float min_damage_hiden = 1000.0f;
  for(int i = 0 ; i < p_ga_occupyingroutes->count ; i++){
    float p_damage_hiden = *((float*)ga_getattr(p_ga_occupyingroutes, i , OCCUMODE_DAMAGE_HIDEN));
    if (p_damage_hiden < min_damage_hiden)
      min_damage_hiden = p_damage_hiden;
  }
  // 筛选
  float error = 0.05;
  int best_index = -1;
  int max_leftpower_hiden = -1;
  bool flag_hidenloc_state = false;
  for (int i = 0 ; i < p_ga_occupyingroutes->count; i ++){
    float* p_cur_route = (float*) ga_getele(p_ga_occupyingroutes, i);
    float damage_hiden = p_cur_route[OCCUMODE_DAMAGE_HIDEN];
    float leftpower_hiden = p_cur_route[OCCUMODE_LEFTPOWER_HIDEN];
    int int_hidenloc4 = (int) (p_cur_route[OCCUMODE_LOC_HIDEN]);
    struct HexOfOffset hex_hiden = {int_hidenloc4/100, int_hidenloc4%100};
    bool flag_hidenInCover = checkHexIsInCover(&hex_hiden);
    if ( (fabs(damage_hiden - min_damage_hiden) <= error  && leftpower_hiden > max_leftpower_hiden) ||
	 (fabs(damage_hiden - min_damage_hiden) <= error  && leftpower_hiden ==  max_leftpower_hiden &&  flag_hidenloc_state == false && flag_hidenInCover == true))
    {
      best_index = i;
      max_leftpower_hiden = leftpower_hiden;
      flag_hidenloc_state = flag_hidenInCover;
    }
  }

  if (best_index < 0){
    printf("error in getBestOccupyingRoute() - best_index < 0\n");
    return false;
  }

  //拷贝最优路径到目标参数
  float * p_best_ele = (float *) ga_getele(p_ga_occupyingroutes, best_index);
  memcpy(p_best_route, p_best_ele, sizeof(float) * OCCUMODE_ELELEN);
  return true;
}

bool cvtOccupyRoute2AIAction(const struct BasicOperator *p_bop, const float * p_best_route,  const float value_city, float * p_aiaction)
{
  // 检查
  bool flag_validpointers = p_bop != NULL && p_best_route != NULL && p_aiaction != NULL;
  if (!flag_validpointers){
    printf("error in cvtOccupyRoute2AIAction() - flag_validpointers is false\n");
    return false;
  }
  
  // 计算最终的reward
  float max_damage = max(p_best_route[OCCUMODE_DAMAGE_CITY], p_best_route[OCCUMODE_DAMAGE_HIDEN]);
  float reward = value_city;
  if (max_damage >= p_bop->obj_blood * 0.8){ // 算子会死掉
      p_aiaction[0] = AIACTION_INVALID; 
      return true;
  }else{
    reward -= (max_damage*p_bop->obj_value);
  }

  // 机动类型
  const int loc_bop_int4 = cvtInt6loc2Int4loc(p_bop->obj_pos);
  const int loc_city_int4 = p_best_route[OCCUMODE_LOC_CITY];
  const int loc_hiden_int4 = p_best_route[OCCUMODE_LOC_HIDEN];
  bool flag_moving_before = loc_bop_int4 != loc_city_int4; // 夺控前是否需要机动
  bool flag_moving_after = loc_city_int4 != loc_hiden_int4; // 夺控后是否需要机动
  
  int hexnum_inpath_0 = 0;
  int hexnum_inpath_1 = 0;
  struct GA *p_gafullpath_0 = ga_init(0,3,sizeof(int));
  struct GA *p_gapartpath_0 = ga_init(0,3,sizeof(int));
  if(flag_moving_before){
    struct HexOfOffset move_objhex = {loc_city_int4/100, loc_city_int4%100};
    trendpathP2P(p_bop, &move_objhex, p_gafullpath_0, p_gapartpath_0);
    hexnum_inpath_0 = p_gapartpath_0->count - 1 ;
    if(!(hexnum_inpath_0 <= 7 && hexnum_inpath_0 > 0)){
      ga_delete(p_gafullpath_0);  ga_delete(p_gapartpath_0);
      p_aiaction[0] = AIACTION_INVALID; 
      return true;
    }
  }
  struct GA *p_gafullpath_1 = ga_init(0,3,sizeof(int));
  struct GA *p_gapartpath_1 = ga_init(0,3,sizeof(int));
  if(flag_moving_after){
    struct HexOfOffset move_objhex = {loc_hiden_int4/100, loc_hiden_int4%100};
    struct BasicOperator bopcopy = * p_bop;
    bopcopy.obj_pos = cvtOffsetIntLocToInt6(loc_city_int4/100, loc_city_int4%100);
    bopcopy.obj_step = (int)(p_best_route[OCCUMODE_LEFTPOWER_CITY]);
    trendpathP2P(&bopcopy, &move_objhex, p_gafullpath_1, p_gapartpath_1);
    hexnum_inpath_1 = p_gapartpath_1->count - 1 ;
    if(!(hexnum_inpath_1 <= 7 && hexnum_inpath_1 > 0)){
      ga_delete(p_gafullpath_0);  ga_delete(p_gapartpath_0);
      ga_delete(p_gafullpath_1);  ga_delete(p_gapartpath_1);
      p_aiaction[0] = AIACTION_INVALID; 
      return true;
    }
  }

  // 区分各种情况
  p_aiaction[1] = p_bop->obj_id;
  if (flag_moving_before == false && flag_moving_after == false){// 仅仅夺控
    p_aiaction[0] = AIACTION_OCCUPY;
    p_aiaction[2] = reward;
  } 
  if (flag_moving_before == true && flag_moving_after == false ){// 机动夺控
    p_aiaction[0] = AIACTION_MOVEOCCUPY;
    p_aiaction[2] = hexnum_inpath_0;
    for (int i = 3; i < 3 + hexnum_inpath_0; i ++){
      int *p_ele = ga_getele(p_gapartpath_0, i - 3 + 1);
      p_aiaction[i] = cvtOffsetIntLocToInt6((int)(p_ele[0]), (int)(p_ele[1]));
    }
    p_aiaction[3 + hexnum_inpath_0] = reward;
  }
  if (flag_moving_before == false && flag_moving_after == true ){// 夺控机动
    p_aiaction[0] = AIACTION_OCCUPYMOVE;
    p_aiaction[2] = hexnum_inpath_1;
    for (int i = 3; i < 3 + hexnum_inpath_1; i ++){
      int *p_ele = ga_getele(p_gapartpath_1, i - 3 + 1);
      p_aiaction[i] = cvtOffsetIntLocToInt6((int)(p_ele[0]), (int)(p_ele[1]));
    }
    p_aiaction[3 + hexnum_inpath_1] = reward;
  }
  if (flag_moving_before == true && flag_moving_after == true){// 机动夺控机动
    p_aiaction[0] = AIACTION_MOVEOCCUPYMOVE;
    p_aiaction[2] = hexnum_inpath_0;
    for (int i = 3; i < 3 + hexnum_inpath_0; i ++){
      int *p_ele = ga_getele(p_gapartpath_0, i - 3 + 1);
      p_aiaction[i] = cvtOffsetIntLocToInt6((int)(p_ele[0]), (int)(p_ele[1]));
    }
    p_aiaction[3+hexnum_inpath_0] = hexnum_inpath_1; 
    for (int i = 4 + hexnum_inpath_0  ; i < 4 + hexnum_inpath_0 + hexnum_inpath_1; i ++){
      int *p_ele = ga_getele(p_gapartpath_1, i - 4 - hexnum_inpath_0 + 1);
      p_aiaction[i] = cvtOffsetIntLocToInt6((int)(p_ele[0]), (int)(p_ele[1]));
    }
    p_aiaction[4 + hexnum_inpath_0 + hexnum_inpath_1] = reward;
  }

  ga_delete(p_gafullpath_0);  ga_delete(p_gapartpath_0);
  ga_delete(p_gafullpath_1);  ga_delete(p_gapartpath_1);
  return true;
}

bool getDC00Routes(const struct BasicOperator *p_bop, const int city_loc6, const float city_value, const float * p_totaldamage_map, struct GA * p_ga_dcroutes)
{
  // 检查
  const int city_loc4 = cvtInt6loc2Int4loc(city_loc6);
  const struct HexOfOffset hex_city = {city_loc4/100, city_loc4%100};
  bool flag_validpointers = p_bop != NULL && p_totaldamage_map != NULL && p_ga_dcroutes != NULL;
  bool flag_boptype = p_bop->obj_type == 1 || (p_bop->obj_type == 2 && p_bop->obj_sonnum == 0);
  bool flag_validcity = checkHexIsValid(&hex_city);
  if(!(flag_validpointers && flag_boptype && flag_validcity)){
    printf("error in getDC00Routes() - flag_validpointers or flag_boptype is false\n");
    return false;
  }

  // 算子最多有8种机动路线（原地不动/机动到目标城市/机动到目标城市周围1格 = 1 + 1 + 6）
  // 候选目标位置
  float p_dcroute[DCMODE_0_ELELEN] = {0.0};
  struct GA * p_gahexsoffset = ga_init(0, 1, sizeof(struct HexOfOffset));
  getHexsInCircleOfOffset(&hex_city, 1 , p_gahexsoffset);
  struct dictionary *p_dicwicg = dic_new(0,sizeof(int));
  whereICanGoRange(p_bop, p_dicwicg);

  for (int defence_loc_index = 0 ; defence_loc_index < p_gahexsoffset->count ; defence_loc_index ++){
    const struct HexOfOffset * p_tmp_hex = (struct HexOfOffset *)(ga_getele(p_gahexsoffset, defence_loc_index));
    const int tmp_loc4 = p_tmp_hex->row * 100 + p_tmp_hex->col;
    char chars_4loc[5] = {'0'};
    cvtIntLocTo4StrOffLoc(tmp_loc4, chars_4loc, 5);
    if (dic_find(p_dicwicg, chars_4loc, 5)){ // 算子有足够的机动力达到此地
      p_dcroute[DCMODE_0_LOC_CITY] = city_loc6;
      p_dcroute[DCMODE_0_LOC_FINAL] = cvtOffsetIntLocToInt6(p_tmp_hex->row, p_tmp_hex->col);
      p_dcroute[DCMODE_0_LEFTPOW_FINAL] = *((int*)p_dicwicg->p_findvalue);
      p_dcroute[DCMODE_0_DAMAGE_FINAL] = p_totaldamage_map[p_tmp_hex->row * MAP_XNUM + p_tmp_hex->col];
      if (p_dcroute[DCMODE_0_DAMAGE_FINAL] >= p_bop->obj_blood * 0.9 ) { // 战损很高
	p_dcroute[DCMODE_0_REWARD] = -1 * p_dcroute[DCMODE_0_DAMAGE_FINAL] * p_bop->obj_value;
      }else{
	p_dcroute[DCMODE_0_REWARD] = city_value - p_dcroute[DCMODE_0_DAMAGE_FINAL] * p_bop->obj_value;
      }
      ga_appendele(p_ga_dcroutes, p_dcroute, DCMODE_0_ELELEN, sizeof(float));
    }
  }

  dic_delete(p_dicwicg);
  ga_delete(p_gahexsoffset);
  return p_ga_dcroutes->count > 0;
}

bool getBestDCRoute(const struct GA * p_ga_dcroutes, const int flag_withpeople, float * p_best_dcroute )
{
  // 检查
  bool flag_validpointers = p_ga_dcroutes != NULL && p_best_dcroute != NULL;
  bool flag_people = flag_withpeople == 0 || flag_withpeople == 1;
  if (!(flag_people && flag_validpointers)){
    printf("error in getBestDCRoute() - flag_people or flag_validpointers is false\n");
    return false;
  }
  switch(flag_withpeople){
    case 0:{
	  // 筛选标准： 战损最小/剩余机动力最大/落脚点为隐蔽点
	  float min_damage = 100.f;
	  for(int i = 0 ; i < p_ga_dcroutes->count; i ++){
	    const float * p_ele = (float *) (ga_getele(p_ga_dcroutes, i));
	    float cur_damage = p_ele[DCMODE_0_DAMAGE_FINAL];
	    if (cur_damage < min_damage){
	      min_damage = cur_damage;
	    }
	  }
	  if (min_damage >= 100){
	    return false;
	  }
	  const float damage_error = 0.25;
	  bool flag_finalloc_state = false;
	  int max_leftpow = -1;
	  int best_index = -1;

	  for (int i = 0 ; i < p_ga_dcroutes->count; i++)
	  {
	    const float * p_ele = (float *) (ga_getele(p_ga_dcroutes, i));
	    const float cur_damage = p_ele[DCMODE_0_DAMAGE_FINAL];
	    const int leftpower = p_ele[DCMODE_0_LEFTPOW_FINAL];
	    const int final_loc4 = cvtInt6loc2Int4loc((int)(p_ele[DCMODE_0_LOC_FINAL]));
	    const struct HexOfOffset hex_final = {final_loc4/100, final_loc4%100};
	    const bool flag_finalloc_incover = checkHexIsInCover(&hex_final);
	    if ((fabs(cur_damage -min_damage)<= damage_error && leftpower > max_leftpow) ||
		(fabs(cur_damage -min_damage)<=damage_error && leftpower==max_leftpow && flag_finalloc_state==false && flag_finalloc_incover==true)){
	      max_leftpow = leftpower;
	      flag_finalloc_state = flag_finalloc_incover;
	      best_index = i;
	    }
	  }
	  if (best_index < 0){
	    printf("error in getBestDCRoute() - best_index < 0 \n");
	    return false;
	  }
	  const float * p_ele = (float *) (ga_getele(p_ga_dcroutes, best_index));
	  memcpy(p_best_dcroute, p_ele, DCMODE_0_ELELEN * sizeof(float));
	  return true;
    }
    case 1:{
	     return false;
    }
    default:{
	      return false;
    }
  }
  
}


void cvtDCRoute2Aiaction(const struct BasicOperator * p_bop, const float * p_best_dcroute , const int flag_withpeople, const int aiaction_len, float * p_aiaction)
{
  //检查
  bool flag_validpointers = p_bop != NULL && p_best_dcroute != NULL && p_aiaction != NULL;
  bool flag_people = flag_withpeople == 0 || flag_withpeople == 1;
  bool flag_codelength = aiaction_len == 20;
  if (!(flag_validpointers && flag_people && flag_codelength)){
    printf("error in cvtDCRoute2Aiaction() - flag_codelength or flag_people or flag_validpointers is false\n");
    p_aiaction[0] = AIACTION_INVALID;
    return ;
  }
  
  switch (flag_withpeople){
    case 0:{
	      // 检查reward
	      const float reward = p_best_dcroute[DCMODE_0_REWARD];
	      if (reward <= 0){
		p_aiaction[0] = AIACTION_INVALID;
		return;
	      }

	      p_aiaction[1] = p_bop->obj_id;
	      const int cur_loc4 = cvtInt6loc2Int4loc((int)p_bop->obj_pos);
	      const int obj_loc4 = cvtInt6loc2Int4loc((int)(p_best_dcroute[DCMODE_0_LOC_FINAL]));
	      if (cur_loc4 == obj_loc4){ // 原地不动
		p_aiaction[0] = AIACTION_DONOTHING;
		p_aiaction[2] = reward;
		return ;
	      } else { // 生成机动动作
		p_aiaction[0] = AIACTION_MOVEONLY;
		int hexnum_inpath_0 = 0;
		struct GA *p_gafullpath_0 = ga_init(0,3,sizeof(int));
		struct GA *p_gapartpath_0 = ga_init(0,3,sizeof(int));
		const struct HexOfOffset move_objhex = {obj_loc4/100, obj_loc4%100};
		trendpathP2P(p_bop, &move_objhex, p_gafullpath_0, p_gapartpath_0);
		hexnum_inpath_0 = p_gapartpath_0->count - 1 ;
		if(!(hexnum_inpath_0 <= 7 && hexnum_inpath_0 > 0)){
		  ga_delete(p_gafullpath_0);  ga_delete(p_gapartpath_0);
		  p_aiaction[0] = AIACTION_INVALID; 
		  return ;
		}
		p_aiaction[2] = hexnum_inpath_0;
		for (int i = 3; i < 3 + hexnum_inpath_0; i ++){
		  int *p_ele = ga_getele(p_gapartpath_0, i - 3 + 1);
		  p_aiaction[i] = cvtOffsetIntLocToInt6((int)(p_ele[0]), (int)(p_ele[1]));
		}
		p_aiaction[18] = reward;
		ga_delete(p_gafullpath_0);  ga_delete(p_gapartpath_0);
		return;
	      }
	   }
    case 1:{
	      p_aiaction[0] = AIACTION_INVALID;
	   }
  }
  return;
  
}

bool getBestScoutloc(const struct GA *p_gahexs, const char * p_str_criterion, struct HexOfOffset *p_hex_o)
{
  // 参数检查
  bool flag = p_gahexs != NULL && p_str_criterion != NULL && p_hex_o != NULL;
  if(!flag){
    printf("error in getBestScoutloc()\n");
    return flag;
  }

  // 按照不同的指标选择最优 p_str_criterion: 选择消耗机动力最大的位置
  float * p_scores = (float*) malloc( p_gahexs->count * sizeof(float));
  for (int i = 0 ; i < p_gahexs->count; i ++){
    int *p_tmp_array = (int *) ga_getele(p_gahexs, i);
    p_scores[i] =  p_tmp_array[2] < 0 ? 0 : 10 - p_tmp_array[2];
  }
  float max_value; int  max_loc;
  flag = findmaxfloat(p_scores, p_gahexs->count, &max_value, &max_loc);
  if (flag){
    int * p_tmp_array = (int*)ga_getele(p_gahexs, max_loc);
    p_hex_o->row = p_tmp_array[0];
    p_hex_o->col = p_tmp_array[1];
  }

  // 资源释放
  free(p_scores);
  return flag;
}

