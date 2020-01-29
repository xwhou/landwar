# coding: utf-8
'''
    2017年9月15日/gsliu/pal_wargame
    文件描述： 针对射击动作给出裁决结果
    更新过程：
        2017年9月15日： 建立文档

'''

import numpy, random, pandas
import __common as common
import __hex as hex


class Judge():

    def __init__(self, dic_paras):
        '''
            BUG0 Python 3.6 + numpy.loadtxt : numpy.version >= 1.15
            KEY0:wgjudge.py中Judge（） 成员变量的定义
                self.np_zm2car_0_juder：直瞄对车辆的战斗结果，索引：行（车班数）， 列（攻击等级）> 内容：确定战斗结果的列索引 x
                self.np_zm2car_1_juder：直瞄对车辆的战斗结果，索引：行（2-12）的随机数字， 列（x） > 内容：战斗结果 1，2，3 ,-1为无效
                self.np_zm2car_2_juder：直瞄对车辆的战斗结果，车辆战损结果修正：索引：行（随机数字0-15）， 列（车辆的装甲等级5列 ）> 内容：结果修正 [-3,+3]
                self.np_anyweapen2people_0_juder : 任意武器对人员算子的战斗结果： 直接结果； 行（随机数字 2-12）, 列 （攻击等级）： -1 无效，0 压制，1 ，2 ， 3
                self.np_anyweapen2people_1_juder : 任意武器对人员算子的战斗结果： 结果修正：行（随机数字0-8），列（0（随机数字0-8），1（结果修正））[-1,1]

        '''
        try:
            self.ele_qua = dic_paras['ele_qua']
            self.np_anyweapen2people_0_juder = numpy.loadtxt(dic_paras['str_anywp2peo_0'], int,
                                                             '#')  # str_public_dir +'anyweapen2people_0_forPythonJuder'
            self.np_anyweapen2people_1_juder = numpy.loadtxt(dic_paras['str_anywp2peo_1'], int,
                                                             '#')  # str_public_dir +'anyweapen2people_1_forPythonJuder'
            self.np_zm2car_0_juder = numpy.loadtxt(dic_paras['str_zm2car_0'], int,
                                                   '#')  # str_public_dir +'zm2car_0_forPythonJuder' ,
            self.np_zm2car_1_juder = numpy.loadtxt(dic_paras['str_zm2car_1'], int,
                                                   '#')  # str_public_dir +'zm2car_1_forPythonJuder'
            self.np_zm2car_2_juder = numpy.loadtxt(dic_paras['str_zm2car_2'], int,
                                                   '#')  # str_public_dir +'zm2car_2_forPythonJuder'
            self.np_elerect = numpy.loadtxt(dic_paras['str_elerect_file'], int,
                                            '#')  # str_public_dir +'elerecttable.txt'
            self.np_wptable = numpy.loadtxt(dic_paras['str_wptable_file'],
                                            int)  # str_public_dir +'wp_table_{}.txt'.format ( 0 ) ,
            self.np_eptable = numpy.loadtxt(dic_paras['str_eptfile'],
                                            int)  # str_data4ai_dir + mapname +'/edgepower_table'
            self.df_rdmap = pandas.read_excel(
                dic_paras['str_rdmap_file'])  # str_data4ai_dir + mapname +'/reduced_map.xls'
            self.df_rdmap.index = self.df_rdmap.MapID

            # new variable for expectation judge by cll
            self.exp_zm2car_1_juder = self.getExpection(self.np_zm2car_1_juder)
            self.exp_anyweapen2people_0_juder = self.getExpection(self.np_anyweapen2people_0_juder)
        except Exception as e:
            common.echosentence_color('Judge > __init__():{}'.format(str(e)))
            raise

    def getExpection(self, npdamage):
        """基于随机伤害表,计算基于正态分布的期望"""
        weight = numpy.zeros((13 - 2,))
        for value in range(2, 13):
            for i in range(1, 7):
                if i >= value: break
                for j in range(1, 7):
                    if i + j > value: break
                    if i + j == value:
                        weight[value - 2] += 1
        weight = weight / (6 * 6)
        average4seed = numpy.dot(weight, npdamage)

        unique_value = numpy.unique(npdamage)
        result_damage = numpy.zeros((npdamage.shape[1],), dtype=numpy.int)
        for n, av in enumerate(average4seed):
            min_dis = 10000
            for v in unique_value:
                if abs(av - v) < min_dis:
                    min_dis = abs(av - v)
                    min_v = v
            result_damage[n] = min_v
        return average4seed

    def getWpRowIndex(self, weaponid):
        '''获取指定武器的行索引'''
        try:
            list_firstcol = list(self.np_wptable[:, 0])
            return list_firstcol.index(weaponid)
        except Exception as e:
            common.echosentence_color('Judge > getWpRowIndex():{}'.format(str(e)))
            raise

    def getElevRectValue(self, ele_diff, distance, obj_type):
        '''获取高程修正数值'''
        try:
            assert (obj_type == 1 or obj_type == 2) and distance >= 0
            if ele_diff <= 0 or distance == 0: return 0
            ele_diff = 8 - 1 if ele_diff >= 8 else ele_diff - 1
            rowindex = (obj_type - 1) * 8 + ele_diff
            colindex = 12 - 1 if distance >= 12 else distance - 1
            return self.np_elerect[rowindex, colindex]
        except Exception as e:
            common.echosentence_color('Judge > getElevRectValue():{}'.format(str(e)))
            raise

    def getDMRandomRect(self, bop_attacker, bop_obj):
        '''获取决定战损的随机数的修正
            # 射击单位修正(射击单位状态)
            # 目标状态( 隐蔽与 普通机动，行军互斥； 非隐蔽状态下的机动或者行军才有意义)
            # 目标所处的位置(地形修正)
        '''
        try:
            randomnumber_rect = 0
            if bop_attacker.ObjKeep == 1: randomnumber_rect -= 1
            if bop_attacker.ObjRound == 1: randomnumber_rect -= 1
            if bop_obj.ObjHide == 1:
                randomnumber_rect -= 2
            else:
                if bop_obj.ObjRound == 1: randomnumber_rect -= 2
                if bop_obj.ObjPass == 1 and bop_obj.ObjType == 2: randomnumber_rect += 4
            if bop_obj.ObjStack == 1:
                randomnumber_rect += 2
            hextype_obj = getHexType(self.df_rdmap, common.cvtInt6loc2Int4loc(int(bop_obj.ObjPos)))
            randomnumber_rect -= hextype_obj
            assert (randomnumber_rect >= -6 and randomnumber_rect <= 6)
            return randomnumber_rect
        except Exception as e:
            common.echosentence_color('Judge > getDMRandomRect():{}'.format(str(e)))
            raise

    def judgeShootDamage(self, bop_attacker, bop_obj, weaponid, useRandom=True):
        '''
            0 获取武器信息
            1 计算攻击者/目标的距离
            2 计算高差（目标-攻击算子）,带有高差修正
            3 计算攻击等级
            4 战损修正
            5 返回列表[武器编号, 距离, 高差, 攻击等级, 生成战损的随机数, 原始战损, 修正战损的随机数, 修正战损]
            KYE0: 最终返回的结果 -1 无效 0 压制 x压制+战斗损失x
            BUG0: 最大伤害是目标算子的当前血量 rected_damage = bop_obj.ObjBlood if rected_damage > bop_obj.ObjBlood else rected_damage
        '''
        try:
            assert (bop_attacker and bop_obj and weaponid > 0 and weaponid < 100 and bop_attacker.ObjBlood > 0)
            obj_type = bop_obj.ObjType
            wp_rowindex = self.getWpRowIndex(weaponid)
            wp_type = self.np_wptable[wp_rowindex, 1]
            if wp_type != 0 and wp_type != obj_type:
                common.echosentence_color(
                    '\t Judge > weaponid = {}, wp_type = {}, obj_type = {}'.format(weaponid, wp_type, obj_type))

            hex_row_a, hex_col_a = common.cvtInt6loc2HexOffset(int(bop_attacker.ObjPos))
            hex_att = hex.HEX_OFF(hex_row_a, hex_col_a)
            hex_row_o, hex_col_o = common.cvtInt6loc2HexOffset(int(bop_obj.ObjPos))
            hex_obj = hex.HEX_OFF(hex_row_o, hex_col_o)
            distance = hex.getDistanceInOff(hex_att, hex_obj)
            if distance >= 21 or distance < 0:
                common.echosentence_color('\t Judge > distance({})'.format(distance))

            ele_a = self.df_rdmap.loc[common.cvtInt6loc2Int4loc(int(bop_attacker.ObjPos)), 'GroundID']
            ele_o = self.df_rdmap.loc[common.cvtInt6loc2Int4loc(int(bop_obj.ObjPos)), 'GroundID']
            ele_diff = (ele_o - ele_a) // self.ele_qua
            attacklevel_rect = self.getElevRectValue(ele_diff, distance, obj_type)
            attacklevel_col = 7 + (
                        bop_attacker.ObjBlood - 1) * 21 + distance if obj_type == 1 else 7 + 5 * 21 + distance
            attacklevel = self.np_wptable[wp_rowindex, attacklevel_col]
            attacklevel += attacklevel_rect
            attacklevel = 10 if attacklevel > 10 else attacklevel
            attacklevel = 0 if attacklevel < 0 else attacklevel
            try:
                assert attacklevel > 0
            except Exception as e:
                common.echosentence_color('attacklevel={}'.format(attacklevel))
                attacklevel = 1

            if obj_type == 2:
                colindex = self.np_zm2car_0_juder[bop_obj.ObjBlood - 1][attacklevel - 1]
                if useRandom:
                    diceRandom2_fordamage = random.randint(1, 6) + random.randint(1, 6)
                    ori_damage = self.np_zm2car_1_juder[diceRandom2_fordamage - 2][colindex - 1]
                else:
                    diceRandom2_fordamage = -1  # new value for average
                    ori_damage = self.exp_zm2car_1_juder[colindex - 1]
                randomnumber_rect = self.getDMRandomRect(bop_attacker, bop_obj)
                if useRandom:
                    diceRandom2_forrect = random.randint(1, 6) + random.randint(1, 6)
                else:
                    diceRandom2_forrect = 7
                rowindex_rect = diceRandom2_forrect + randomnumber_rect
                rowindex_rect = -3 if rowindex_rect < -3 else rowindex_rect
                rowindex_rect = 12 if rowindex_rect > 12 else rowindex_rect
                # -3 - 12 ==> 0 ==> 7 ==> 3 ==> 10
                try:
                    if common.soft_highpro():
                        rowindex_rect = 0 if rowindex_rect < 0 else 7 if rowindex_rect > 7 else rowindex_rect
                except Exception as e:
                    pass
                rowindex_rect += 3
                rected_damage = ori_damage + self.np_zm2car_2_juder[rowindex_rect][int(bop_obj.B0)]
                rected_damage = -1 if rected_damage < -1 else rected_damage
                rected_damage = bop_obj.ObjBlood if rected_damage > bop_obj.ObjBlood else rected_damage
                list_return_value = [weaponid, hex.getDistanceInOff(hex_att, hex_obj), (ele_o - ele_a) // self.ele_qua,
                                     attacklevel, diceRandom2_fordamage, ori_damage, diceRandom2_forrect,
                                     rected_damage]
            else:
                if useRandom:
                    diceRandom2_fordamage = random.randint(1, 6) + random.randint(1, 6)
                    ori_damage = self.np_anyweapen2people_0_juder[diceRandom2_fordamage - 2][attacklevel - 1]
                else:
                    diceRandom2_fordamage = -1
                    ori_damage = self.exp_anyweapen2people_0_juder[attacklevel - 1]
                if useRandom:
                    diceRandom1_forrect = random.randint(1, 6)
                else:
                    diceRandom1_forrect = 3.5
                rowindex_rect = diceRandom1_forrect + self.getDMRandomRect(bop_attacker, bop_obj)
                rowindex_rect = 0 if rowindex_rect <= 0 else int(rowindex_rect)
                rowindex_rect = 8 if rowindex_rect >= 8 else int(rowindex_rect)
                rected_damage = ori_damage + self.np_anyweapen2people_1_juder[rowindex_rect][1]
                rected_damage = -1 if rected_damage < -1 else rected_damage
                rected_damage = bop_obj.ObjBlood if rected_damage > bop_obj.ObjBlood else rected_damage
                list_return_value = [weaponid, hex.getDistanceInOff(hex_att, hex_obj), (ele_o - ele_a) // self.ele_qua,
                                     attacklevel, diceRandom2_fordamage, ori_damage, diceRandom1_forrect,
                                     rected_damage]
            list_return_value[7] = cvtDamage2Lost(bop_obj, list_return_value[7])
            return list_return_value
        except Exception as e:
            common.echosentence_color('Judge > judgeShootDamage():{}'.format(str(e)))
            raise

    def judgeActionObj(self, dic_metadata, obj_pa, useRandom=True):
        '''
            动作裁决，目前只有射击动作（action_type == 3）需要裁决
            KEY0: 基于普通射击的裁决和基于同格交战的裁决
            KEY3: 所有的射击动作需要更新reward/ damage
            modify 2018年10月25日 宋国瑞 更新obj_pa中的dict_caijueinfos变量，用于裁决表的记录
        '''
        try:
            if obj_pa.action_type == 3:
                bop_att = common.getSpecifiedBopById(dic_metadata['l_rbops'] + dic_metadata['l_bbops'], obj_pa.objid_0)
                bop_obj = common.getSpecifiedBopById(dic_metadata['l_rbops'] + dic_metadata['l_bbops'], obj_pa.objid_1)
                list_return_value = self.judgeShootDamage(bop_att, bop_obj, obj_pa.shoot_wzid, useRandom=useRandom)
                obj_pa.shoot_damage = list_return_value[7]
                reward_factor = 0 if obj_pa.shoot_damage < 0 else 0.5 if obj_pa.shoot_damage == 0 else obj_pa.shoot_damage + 0.25
                obj_pa.reward = reward_factor * obj_pa.shoot_damage * bop_obj.ObjValue
                obj_pa.dict_caijueinfos = {}
                obj_pa.dict_caijueinfos['WeaponID'] = list_return_value[0]
                obj_pa.dict_caijueinfos['Dist'] = list_return_value[1]
                obj_pa.dict_caijueinfos['EleDiff'] = list_return_value[2]
                obj_pa.dict_caijueinfos['AttackLevel'] = list_return_value[3]
                obj_pa.dict_caijueinfos['RandomNum1'] = list_return_value[4]
                obj_pa.dict_caijueinfos['Result1'] = list_return_value[5]
                obj_pa.dict_caijueinfos['RandomNum2'] = list_return_value[6]
                obj_pa.dict_caijueinfos['Result'] = list_return_value[7]
            else:
                pass
        except Exception as e:
            common.echosentence_color('Judge > judgeActionObj():{}'.format(str(e)))
            raise

    def judgeTonggeShootDamage(self, bop_attacker, bop_obj, attacklevel=0, flag_shootindex=0, useRandom=True):
        '''
            RETURN:返回最终的战斗结果
            KEY1:flag_shootindex 当前是第几轮同格交战的射击，只有第一轮同格交战才会进行战斗结果的修正
            modify 2018年10月25日 宋国瑞 返回格式与judgeShootDamage相同，便于记录caijue表
        '''
        try:
            assert attacklevel > 0 and attacklevel <= 10 and flag_shootindex in [1, 2, 3]
            obj_type = bop_obj.ObjType
            if obj_type == 2:
                colindex = self.np_zm2car_0_juder[bop_obj.ObjBlood - 1][attacklevel - 1]
                if useRandom:
                    diceRandom2_fordamage = random.randint(1, 6) + random.randint(1, 6)
                    rected_damage = ori_damage = self.np_zm2car_1_juder[diceRandom2_fordamage - 2][colindex - 1]
                else:
                    diceRandom2_fordamage = -1
                    rected_damage = ori_damage = self.exp_zm2car_1_juder[colindex - 1]
                    # rected_damage = ori_damage = self.np_zm2car_1_juder[diceRandom2_fordamage - 2][colindex - 1]
                if flag_shootindex == 1:  # 只有第一轮射击进行战斗结果矫正
                    randomnumber_rect = self.getDMRandomRect(bop_attacker, bop_obj)
                    if useRandom:
                        diceRandom2_forrect = random.randint(1, 6) + random.randint(1, 6)
                    else:
                        diceRandom2_forrect = 7
                    rowindex_rect = diceRandom2_forrect + randomnumber_rect

                    rowindex_rect = -3 if rowindex_rect < -3 else rowindex_rect
                    rowindex_rect = 12 if rowindex_rect > 12 else rowindex_rect
                    # -3 - 12 ==> 0 ==> 7 ==> 3 ==> 10
                    try:
                        if common.soft_highpro():
                            rowindex_rect = 0 if rowindex_rect < 0 else 7 if rowindex_rect > 7 else rowindex_rect
                    except Exception as e:
                        pass
                    rowindex_rect += 3

                    rected_damage = ori_damage + self.np_zm2car_2_juder[rowindex_rect][int(bop_obj.B0)]
                    rected_damage = -1 if rected_damage < -1 else rected_damage
                    rected_damage = bop_obj.ObjBlood if rected_damage > bop_obj.ObjBlood else rected_damage
                else:
                    diceRandom2_forrect = diceRandom2_fordamage
                list_return_value = [0, 0, 0, attacklevel, diceRandom2_fordamage, ori_damage, diceRandom2_forrect,
                                     rected_damage]
            else:
                if useRandom:
                    diceRandom2_fordamage = random.randint(1, 6) + random.randint(1, 6)
                    rected_damage = ori_damage = self.np_anyweapen2people_0_juder[diceRandom2_fordamage - 2][
                        attacklevel - 1]
                else:
                    diceRandom2_fordamage = -1
                    rected_damage = ori_damage = self.exp_anyweapen2people_0_juder[attacklevel - 1]
                if flag_shootindex == 1:
                    if useRandom:
                        diceRandom1_forrect = random.randint(1, 6)
                    else:
                        diceRandom1_forrect = 3.5
                    rowindex_rect = diceRandom1_forrect + self.getDMRandomRect(bop_attacker, bop_obj)
                    rowindex_rect = 0 if rowindex_rect <= 0 else int(rowindex_rect)
                    rowindex_rect = 8 if rowindex_rect >= 8 else int(rowindex_rect)
                    rected_damage = ori_damage + self.np_anyweapen2people_1_juder[rowindex_rect][1]
                    rected_damage = -1 if rected_damage < -1 else rected_damage
                    rected_damage = bop_obj.ObjBlood if rected_damage > bop_obj.ObjBlood else rected_damage
                else:
                    diceRandom1_forrect = diceRandom2_fordamage
                list_return_value = [0, 0, 0, attacklevel, diceRandom2_fordamage, ori_damage, diceRandom1_forrect,
                                     rected_damage]
            return list_return_value
        except Exception as e:
            common.echosentence_color('Judge > judgeTonggeShootDamage():{}'.format(str(e)))
            raise

    def judgeTonggeShootObj(self, dic_metadata, obj_pa, flag_shootindex=0, useRandom=True):
        '''
            KEY1:flag_shootindex 当前是第几轮同格交战的射击，只有第一轮同格交战才会进行战斗结果的修正
            KEY2:同格交战的攻击等级单独设置
                步兵棋子：1个班用2，2个班用4，3个班用6
                战车棋子：对人10，对车8（目前版本中与车数无关）
                坦克棋子：对人10，对车10（目前版本中与车数无关）
            KEY3: 所有的射击动作需要更新reward/ damage
            BUG0: 最大伤害是目标算子的当前血量 rected_damage = bop_obj.ObjBlood if rected_damage > bop_obj.ObjBlood else rected_damage
            modfigy 2018年10月25日 宋国瑞 ： 更新obj_pa中dict_caijueinfos变量，用于裁决表的记录
        '''
        try:
            assert obj_pa.action_type == 3
            bop_att = common.getSpecifiedBopById(dic_metadata['l_rbops'] + dic_metadata['l_bbops'], obj_pa.objid_0)
            bop_obj = common.getSpecifiedBopById(dic_metadata['l_rbops'] + dic_metadata['l_bbops'], obj_pa.objid_1)
            try:
                assert bop_att.GameColor != bop_obj.GameColor
            except Exception as e:
                common.echosentence_color("BOOOOOOOOOO", 'red')
                raise e

            if bop_att.ObjTypeX == 0:
                attacklevel = 10
            elif bop_att.ObjTypeX == 1:
                attacklevel = 10 if bop_obj.ObjType == 1 else 8
            else:
                attacklevel = bop_att.ObjBlood * 2
            list_return_value = self.judgeTonggeShootDamage(bop_att, bop_obj, attacklevel=attacklevel,
                                                            flag_shootindex=flag_shootindex, useRandom=useRandom)
            obj_pa.shoot_damage = list_return_value[7]
            reward_factor = 0 if obj_pa.shoot_damage < 0 else 0.5 if obj_pa.shoot_damage == 0 else obj_pa.shoot_damage + 0.25
            obj_pa.reward = reward_factor * obj_pa.shoot_damage * bop_obj.ObjValue
            obj_pa.dict_caijueinfos = {}
            obj_pa.dict_caijueinfos['WeaponID'] = list_return_value[0]
            obj_pa.dict_caijueinfos['Dist'] = list_return_value[1]
            obj_pa.dict_caijueinfos['EleDiff'] = list_return_value[2]
            obj_pa.dict_caijueinfos['AttackLevel'] = list_return_value[3]
            obj_pa.dict_caijueinfos['RandomNum1'] = list_return_value[4]
            obj_pa.dict_caijueinfos['Result1'] = list_return_value[5]
            obj_pa.dict_caijueinfos['RandomNum2'] = list_return_value[6]
            obj_pa.dict_caijueinfos['Result'] = list_return_value[7]
        except Exception as e:
            common.echosentence_color('Judge > judgeTonggeShootObj():{}'.format(str(e)))
            raise


def getEnterHexPower(np_eptable, bop_type, src_int6loc, des_int6loc):
    '''给定算子位置与距离1格的目标位置，计算算子以普通机动的方式进入目标六角格所消耗的机动力'''
    try:
        assert (bop_type == 1 or bop_type == 2)
        hex_src_y, hex_src_x = common.cvtInt6loc2HexOffset(int(src_int6loc))
        hex_src = hex.HEX_OFF(hex_src_y, hex_src_x)
        hex_des_y, hex_des_x = common.cvtInt6loc2HexOffset(int(des_int6loc))
        hex_des = hex.HEX_OFF(hex_des_y, hex_des_x)
        assert hex_des_x >= 0 and hex_des_y >= 0 and hex_src_x >= 0 and hex_src_y >= 0
        assert hex.getDistanceInOff(hex_src, hex_des) == 1

        epvalue = 0
        if bop_type == 1:
            epvalue = 1
        else:
            dir_des2src = hex.getSpecifiedDirection(hex_src, hex_des)  # 初始位置位于目标位置的哪个方向[0,5]
            assert dir_des2src in range(6)
            list_1stcol = list(np_eptable[:, 0])
            value = hex_des_y * 100 + hex_des_x
            if value not in list_1stcol:
                epvalue = 1
            else:
                row_index = list_1stcol.index(value)
                epvalue = np_eptable[row_index, dir_des2src + 1]
                assert (epvalue > 0 and epvalue < 10)
        return epvalue
    except Exception as e:
        common.echosentence_color('wgjudge > getEnterHexPower():{}'.format(str(e)))
        raise


def getHexType(df_rdmap, int4loc):
    '''获取位置六角格的类型
        0 普通 1 居民地 2 从林地
    '''
    try:
        tmp_df_rdmap = df_rdmap[df_rdmap.MapID == int4loc]
        assert (len(tmp_df_rdmap) == 1)
        flag = 0
        gridtype, hexnum, cond = tmp_df_rdmap.loc[int4loc, 'GridType'], tmp_df_rdmap.loc[int4loc, 'GridID'], \
                                 tmp_df_rdmap.loc[int4loc, 'Cond']
        if gridtype == 3: flag = 1 if hexnum == 51 else 2
        if gridtype == 2 and cond == 7: flag = 1
        return flag
    except Exception as e:
        common.echosentence_color('wgjudger > getHexType():{}'.format(str(e)))
        raise


def cvtDamage2Lost(bop_obj, rected_damageresult):
    '''战损转换成为对算子具体的损失
        rected_damageresult ： -1 0 1 2 3
        返回数值：损失的车班数(附带压制效果)
    '''
    try:
        tmp_tarlost = 0
        if rected_damageresult < 0:
            pass
        elif rected_damageresult == 0:
            if bop_obj.ObjType == 1 and bop_obj.ObjKeep == 1: tmp_tarlost = 1
        else:
            tmp_tarlost = rected_damageresult
        return tmp_tarlost
    except Exception as e:
        common.echosentence_color('wgjudger > cvtDamage2Lost():{}'.format(str(e)))
        raise


if __name__ == '__main__':
    pass