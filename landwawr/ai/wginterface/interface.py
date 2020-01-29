import sys
sys.path.append("../")
sys.path.append("")


from common.m_exception import print_exception
from wgconst.const import StateType
from wgmap.terrain import cvt_int6_to_int4
from wgmap.terrain import cvt_int4_to_offset
from wgmap.terrain import cvt_int6_to_offset
from wgmap.terrain import check_bop_see
from wgmap.terrain import Terrain
from wgloader.file_loader import FileLoader
from wgweapon.weapon_sets import WeaponSets
from ai.RJ_operator import AI_BasicOperator
from __wgcutility import CUtility
import __wgpreknow as wgpreknow
import __wgobject as wgobject

import random,copy


class AI_InterFace:
    def __init__(self, color, env, ruler, scenario):
        self.operators = []
        self.enemy_operators = []
        self.valid_actions = {}
        self.game_over = False
        self.red_step = 0
        self.blue_step = 0
        self.env = env
        self.ruler = ruler
        self.color = color
        self.loader = FileLoader(scenario=scenario, data_dir="../")
        self.terrain = Terrain(loader=self.loader)
        self.weaponsets = WeaponSets(loader=self.loader, terrain=self.terrain)
        observations, self.game_over = self.env.reset()
        self.observations = observations[self.color]
        # self.spath = GenPath(self.terrain)
        self._get_valid_action()
        dic_mainparas = {'str_wgrootdir': '../',
                         'str_global_flag': 'AC',
                         'num_plays': 1,
                         'num_objcutility': 1,
                         'ip': -1,
                         'roomid': -1,
                         'num_xd': scenario,
                         # 'strategy_ids': (0,0),
                         'flag_show': True,
                         'flag_action_cache': False,
                         'flag_qd_rm': False,
                         'flag_cache': False,
                         'flag_gpu': False,
                         'flag_dllnum': 0,
                         'flag_afm': True,
                         'cuda_id': 0,
                         'flag_savestate': False,
                         'dic2_aiparas': {
                             'flag_color4acai': color,
                         },
                         }
        self.obj_pk = wgpreknow.PreKnow(dic_mainparas)
        self.cutility = CUtility(self.obj_pk.dic_paras)
        #
        # try:
        #     self.a_star = AStar(excelfile=path_file)
        # except Exception as e:
        #     print_exception(e)
        #     raise e

    '''基本接口'''
    def _get_valid_action(self):
        try:
            self.valid_actions = self.observations['valid_actions']
            self.ruler.get_valid_action(self.valid_actions)
            return 1
        except Exception as e:
            print_exception(e)
            raise e

    def update_observation(self, observation):
        self.observations = observation
        # self.setNull()
        self._get_valid_action()

    def get_observations(self):
        observations, game_over = self.env.engine.get_sd_data(), self.env.engine.check_game_over()
        self.observations = observations[self.color]
        self.game_over = game_over
        # self.setNull()
        self._get_valid_action()
        return self.observations

    def get_game_over(self):
        return self.game_over

    def create_action_msg(self, obj_id, action_type, paras):
        """

        :param obj_id:
        :param action_type:
        :param paras:  [weapon_id]
        :return:
        """
        try:
            result = {
                "obj_id": obj_id,
                "type": action_type,
            }
            if action_type == StateType.Move:
                if 'move_path' not in paras.keys():
                    return False
            elif action_type == StateType.Shoot:
                if 'target_obj_id' not in paras.keys() or 'weapon_id' not in paras.keys():
                    return False
            elif action_type == StateType.GuideShoot:
                if 'target_obj_id' not in paras.keys() or 'weapon_id' not in paras.keys() or 'guided_obj_id' not in paras.keys():
                    return False
            elif action_type == StateType.JMPlan:
                if 'weapon_id' not in paras.keys() or 'jm_pos' not in paras.keys():
                    return False
            elif action_type == StateType.GetOn:
                if 'target_obj_id' not in paras.keys():
                    return False
            elif action_type == StateType.GetOff:
                if 'target_obj_id' not in paras.keys():
                    return False
            elif action_type == StateType.ChangeState:
                if 'target_state' not in paras.keys():
                    return False
            elif action_type == StateType.Occupy:
                paras = ''
                pass
            elif action_type == StateType.RestoreKeep:
                pass
            result.update(paras)
            return result
        except Exception as e:
            print_exception(e)
            raise e

    '''强化学习接口'''
    def envreset(self):
        observations, game_over = self.env.reset()
        self.game_over = game_over
        return observations[self.color], observations[(1 - self.color)]

    def envstep(self, actions, count=1):
        observations, game_over = self.env.step(actions, count)
        self.game_over = game_over
        self.observations = observations[self.color]
        return self.observations

    '''对象控制接口'''
    def setOccupy(self, operatorID):
        '''控制算子沿路径机动
        :return 0/执行成功 -1/参数类型不合法 -2/不符合夺控规则
        '''
        try:
            if not isinstance(operatorID, int):
                return -1
            actions = []
            valid_action_list = self.valid_actions[operatorID]
            valid_action_types = list(valid_action_list.keys())
            if StateType.Occupy not in valid_action_types:
                return -2
            valid_paras = valid_action_list[StateType.Occupy]
            random_para = random.choice(valid_paras) if valid_paras else None
            action = self.create_action_msg(operatorID, StateType.Occupy, random_para)
            actions.append(action)
            observations, game_over = self.env.step(actions, count=1)
            self.game_over = game_over
            print(actions)
            self.observations = observations[self.color]
            return 0
        except Exception as e:
            print_exception(" " + str(e))
            raise e
        except KeyboardInterrupt as k:
            print_exception(" " + str(k))
            raise

    def setFire(self,operatorID,targetID,weaponID,guideID=""):
        ''' 算子进行攻击
        :param operatorID: 攻击算子ID
        :param targetID: 被攻击算子ID
        :param weaponID: 武器ID
        :return: （0,Series)/(执行成功，本次攻击裁决结果)，(-1,None)/(参数类型不合法，None)，（-2,None）/(不符合射击规则,None)
        (-3,None) /(武器冷却中,None)
        '''
        try:
            if not (isinstance(operatorID,int) and isinstance(targetID,int) and isinstance(weaponID,int)):
                return (-1,None)
            # 检查是否在射击准备
            actions = []
            valid_action_list = self.valid_actions[operatorID]
            valid_action_types = list(valid_action_list.keys())
            if StateType.GuideShoot in valid_action_types:
                valid_paras = valid_action_list[StateType.GuideShoot]
                for paras in valid_paras:
                    if paras['target_obj_id'] == targetID:
                        for att_bop in self.operators:
                            if att_bop.ID == operatorID:
                                if weaponID in att_bop.carry_weapon_ids:
                                    paras['weapon_id'] = weaponID
                                    paras['guided_obj_id'] = guideID
                                    action = self.create_action_msg(operatorID, StateType.GuideShoot, paras)
                                    actions.append(action)
                                    observations, game_over = self.env.step(actions, count=1)
                                    self.game_over = game_over
                                    print(actions)
                                    self.observations = observations[self.color]
                                    return (0, None)
            elif StateType.Shoot in valid_action_types:
                valid_paras = valid_action_list[StateType.Shoot]
                for paras in valid_paras:
                    if paras['target_obj_id'] == targetID:
                        for att_bop in self.operators:
                            if att_bop.ID == operatorID:
                                if weaponID in att_bop.carry_weapon_ids:
                                    action = self.create_action_msg(operatorID, StateType.Shoot, paras)
                                    actions.append(action)
                                    observations, game_over = self.env.step(actions, count=1)
                                    self.game_over = game_over
                                    print(actions)
                                    self.observations = observations[self.color]
                                    return (0, None)

            else:
                return (-2,None)
        except Exception as e:
            print_exception(" " + str(e))
            raise
        except KeyboardInterrupt as k:
            print_exception(" " + str(k))
            raise

    def setGetoff(self, operatorID, objectSonType=1):
        '''
        人员下战车
        :param operatorID1: 本方战车算子
        :return: 0/执行成功，-1/参数类型不合法，-2/不符合下车规则
        '''
        try:
            if not isinstance(operatorID, int) and isinstance(objectSonType, int):
                return -1
            actions = []
            valid_action_list = self.valid_actions[operatorID]
            valid_action_types = list(valid_action_list.keys())
            if StateType.GetOff not in valid_action_types:
                return -2
            valid_paras = valid_action_list[StateType.GetOff]
            random_para = random.choice(valid_paras) if valid_paras else None
            action = self.create_action_msg(operatorID, StateType.GetOff, random_para)
            actions.append(action)
            observations, game_over = self.env.step(actions, count=1)
            self.game_over = game_over
            print(actions)
            self.observations = observations[self.color]
            # if objectSonType == 1:
            #     str_json = wgcom.genPeopleGettingOffJsonComStr(operatorID)
            # elif objectSonType == 2:
            #     str_json = wgcom.genUGCVGettingOffJsonComstr(operatorID)
            # elif objectSonType == 3:
            #     str_json = wgcom.genMissilesGettingOffJsonComstr(operatorID)
            # else:
            #     return -2
            # flag_success = wgcom.executeJsonAction(self.obj_pk.dic_paras, str_json, self.gameColor, self.roomID)
            return 0
        except Exception as e:
            print_exception(" " + str(e))
            raise
        except KeyboardInterrupt as k:
            print_exception(" " + str(k))
            raise

    def setGeton(self,operatorID1,operatorID2):
        '''
        人员上战车
        :param operatorID1: 本方步兵算子
        :param operatorID2: 本方战车算子
        :return: 0/执行成功 ，-1/参数类型不合法，-2/不符合上车规则
        '''
        try:
            if not (isinstance(operatorID1,int) and isinstance(operatorID2,int)):
                return -1
            actions = []
            valid_action_list = self.valid_actions[operatorID1]
            valid_action_types = list(valid_action_list.keys())
            if StateType.GetOn not in valid_action_types:
                return -2
            valid_paras = valid_action_list[3]
            random_para = random.choice(valid_paras) if valid_paras else None
            action = self.create_action_msg(operatorID1, StateType.GetOn, random_para)
            actions.append(action)
            observations, game_over = self.env.step(actions, count=1)
            self.game_over = game_over
            print(actions)
            self.observations = observations[self.color]
            # str_json = wgcom.genPeopleGettingOnJsonComStr(operatorID1,operatorID2)
            # flag_success = wgcom.executeJsonAction(self.obj_pk.dic_paras,str_json,self.gameColor,self.roomID)
            return 0
        except Exception as e:
            print_exception(" " + str(e))
            raise
        except KeyboardInterrupt as k:
            print_exception(" " + str(k))
            raise

    def setMove(self, operatorID,movePath):
        '''控制算子沿路径机动
        :return 0/执行成功 -1/参数类型不合法,-2/movePath长度等于0 ,-3/不符合机动规则
        '''
        try:
            if not (isinstance(operatorID,int) and isinstance(movePath,list)):
                return -1
            if len(movePath) == -1:
                return -2
            actions = []
            valid_action_list = self.valid_actions[operatorID]
            valid_action_types = list(valid_action_list.keys())
            if StateType.Move not in valid_action_types:
                return -3
            move_path = {"move_path": movePath}
            action = self.create_action_msg(operatorID, StateType.Move, move_path)
            actions.append(action)
            observations, game_over = self.env.step(actions, count=1)
            self.game_over = game_over
            print(actions)
            self.observations = observations[self.color]
            return 0
        except Exception as e:
            print_exception(" " + str(e))
            raise
        except KeyboardInterrupt as k:
            print_exception(" " + str(k))
            raise

    def setNull(self):
        '''
        生成空动作
        :return: 
        '''
        actions = []
        observations,game_over = self.env.step(actions)
        # observations, game_over = self.env.engine.get_sd_data(), self.env.engine.check_game_over()
        self.observations = observations[self.color]
        self.game_over = game_over
        return 0
        
    def setAutoGetOn_Off_atBegin(self):
        try:
            pass
        except Exception as e:
            print_exception(e)
            raise

    ''''''
    def getMovePath(self, operator,coordinate):
        # print(111)
        if not (isinstance(coordinate, int)):
            return -1
        coordinate = self._check_and_cvt_int6to4(coordinate)
        if not coordinate:
            return -1
        mod = 0
        if operator.ObjType == 1:
            if operator.ObjPass == 0:
                mod = 0
            else:
                mod = 1
        if operator.ObjType == 2: #  步兵算子
            mod = 2
        elif operator.ObjType == 3:
            mod = 3
        move_path = self.terrain.get_path(operator.cur_hex,  coordinate, mod)
        return (0, move_path)

    def _check_and_cvt_int6to4(self,loc):
        if loc // 10000 > 0:
            int4loc = cvt_int6_to_int4(loc)
            return int4loc
        elif loc //100 > 0:
            return loc
        return -1

    '''对象查询接口'''
    def getSideOperatorsData(self):
        try:
            self.operators = []
            l_ops = self.observations['operators']
            for op in l_ops:
                bop = AI_BasicOperator(terrain=None, data_source=op)
                if bop.color == self.color:
                    flag, _ = bop.can_control()
                    if flag:
                        self.operators.append(bop)
            return self.operators
        except Exception as e:
            print_exception(e)
            raise e

    def getEnemyOperatorsData(self):
        try:
            self.enemy_operators = []
            l_ops = self.observations['operators']
            for op in l_ops:
                bop = AI_BasicOperator(terrain=None, data_source=op)
                if bop.color == (1 - self.color):
                    flag, _ = bop.can_control()
                    if flag:
                        self.enemy_operators.append(bop)
            return self.enemy_operators
        except Exception as e:
            print_exception(e)
            raise e

    def getCarOperatorsData(self):
        try:
            self.on_car_operators = []
            l_ops = self.observations['operators']
            for op in l_ops:
                bop = AI_BasicOperator(terrain=None, data_source=op)
                if bop.color == self.color:
                    if bop.on_board == 1:
                        self.on_car_operators.append(bop)
            return self.on_car_operators
        except Exception as e:
            print_exception(e)
            raise e

    def getCityData(self):
        try:
            cities = self.observations['cities']
            city_list = []
            for city in cities:
                city['coord_int6'] = cvt_int4_to_int6(city['coord'])
                city_list.append(city)
            return city_list
        except Exception as e:
            print_exception(e)
            raise e

    def getScore(self):
        try:
            score = self.observations['scores']
            return score
        except Exception as e:
            print_exception(e)
            raise e

    def cal_blind_map(self, bop, ubop):
        try:
            np_blind_map = self.cutility.get_dynamicobserve_blindmap_p2p(bop, ubop)
            return np_blind_map
        except Exception as e:
            raise e

    '''分析工具接口'''
    def getAttackLevel(self, operator1, operator2, weaponID):
        if not (isinstance(operator1, AI_BasicOperator) and isinstance(operator2, AI_BasicOperator) and
                isinstance(weaponID,int)):
            return (-1, None)
        attack_level,_ = self.weaponsets.get_attack_level(operator1, operator2, weaponID)
        return (0, attack_level)

    def getLOS(self, coordinate1, coordinate2):
        if not (isinstance(coordinate1, int) and isinstance(coordinate2,int)):
            return (-1, None)
        coordinate1 = self._check_and_cvt_int6to4(coordinate1)
        coordinate2 = self._check_and_cvt_int6to4(coordinate2)
        if not (coordinate1 and coordinate2):
            return (-1, None)

        flag_see = self.terrain.check_see(coordinate1, coordinate2)
        if flag_see:
            dis = self.terrain.get_dis_between_hex(coordinate1, coordinate2)
            return (0, dis)
        return (0, -1)

    def getMapDistance(self, coordinate1, coordinate2):
        if not (isinstance(coordinate1, int) and isinstance(coordinate2,int)):
            return (-1, None)
        coordinate1 = self._check_and_cvt_int6to4(coordinate1)
        coordinate2 = self._check_and_cvt_int6to4(coordinate2)
        if not (coordinate1 and coordinate2):
            return (-1, None)
        dis = self.terrain.get_dis_between_hex(coordinate1, coordinate2)
        return (0, dis)

    def flagISU(self, operator1, operator2):
        if not (isinstance(operator1, AI_BasicOperator) and isinstance(operator2, AI_BasicOperator)):
            return (-1, None)
        flag = check_bop_see(operator1, operator2, self.terrain)
        return (0, flag)
        pass

    def chooseWeaponIndex(self, operator1, operator2):
        '''
        算子1攻击算子2最大攻击等级的武器
        :param operator1:
        :param operator2:
        :return: (0,int)/(执行成功，最佳武器ID),(-1,参数不合法),(-2,不符合射击规则)
        '''
        try:
            # if not (isinstance(operator1, pandas.Series) and isinstance(operator2, pandas.Series)):
            #     return (-1, None)
            valid_action_list = self.valid_actions[operator1.obj_id]
            valid_action_types = list(valid_action_list.keys())
            # if 9 not in valid_action_types or 2 not in valid_action_types:
            #     return (-2, None)
            if 9 in valid_action_types:
                valid_paras = valid_action_list[9]
                for paras in valid_paras:
                    if paras['target_obj_id'] == operator2.obj_id:
                        return (0, paras['weapon_id'])
            if 2 in valid_action_types:
                valid_paras = valid_action_list[2]
                for paras in valid_paras:
                    if paras['target_obj_id'] == operator2.obj_id:
                        return (0, paras['weapon_id'])
            return (-2, None)
        except Exception as e:
            print_exception(e)
            raise e

    def cvtHexOffset2Int6loc(self, row, col):
        return cvt_offset_to_int6(row, col)

    def cvtInt6loc2HexOffset(self, int6loc):
        return cvt_int6_to_offset(int6loc)

def cvt_int4_to_int6(int4_loc):
    try:
        assert isinstance(int4_loc, int)
        row, col = cvt_int4_to_offset(int4_loc)
        return cvt_offset_to_int6(row, col)
    except Exception as e:
        print_exception(e)
        raise e

def cvt_offset_to_int6(row, col):
    try:
        if row % 2 == 1:
            tmpfirst = (row - 1) // 2
            tmplast = col * 2 + 1
        else:
            tmpfirst = row // 2
            tmplast = col * 2
        if tmpfirst < 0 or tmplast < 0:
            return -1
        return int(tmpfirst * 10000 + tmplast)
    except Exception as e:
        print_exception(e)
        raise


# class InterFace(AI_InterFace):
#     def __init__(self, color, path_file, env):
#         super(InterFace, self).__init__(path_file, env)
#