from common.m_exception import print_exception


class Rule:
    def __init__(self):
        self.valid_actions = {}

    def get_valid_action(self, valid_action):
        try:
            self.valid_actions = valid_action
        except Exception as e:
            print_exception('__wgruler.py > valid_action():{}'.format(str(e)))
            raise

    '''规则判断接口'''
    def updateNotMyCityList(self, l_cities, flag_color):
        '''更新非我方城市列表'''
        try:
            cities= []
            for city in l_cities:
                if city['flag'] != flag_color:
                    cities.append(city)
            return cities
        except Exception as e:
            print_exception('__wgruler.py > updateNotMyCityList():{}'.format(str(e)))
            raise

    def stackCheck(self, list_bops):
        '''算子的堆叠检查'''
        try:
            for cur_index, cur_bop in enumerate(list_bops):
                flag_stack = False
                for inter_index, inter_bop in enumerate(list_bops):
                    if cur_index != inter_index and cur_bop.ObjPos == inter_bop.ObjPos:
                        flag_stack = True
                        break
                cur_bop.ObjStack = 1 if flag_stack else 0
        except Exception as e:
            print_exception('wgruler > stackCheck():{}'.format(str(e)))
            raise

    def cvtMapBop2AIBop(self, map_bop):
        '''地图算子 -> AI算子的映射函数 （将算子的阶段标志换成0_1标志）
            BUG0: 2018/08/06 - 08:23 加入隐蔽状态的判断
            BUG1:算子在同格时候会将机动力设置0，导致依赖机动力进行判断的其他标志不准确，需要单独调整： objround
            BUG2:人员算子的机动力objstep不仅仅还需要objpass进行调整（但是一旦算子处于同格，机动力不应该再进行变化）
        '''
        try:
            return map_bop
        except Exception as e:
            print_exception('wgruler > cvtMapBop2AIBop():{}'.format(str(e)))
            raise

    def TonggeCheck(self, list_obops, list_ubops):
        '''算子是否处于同格交战状态,
            处于同格状态，强制将机动力设置=0
        '''
        try:
            for obop in list_obops:
                for ubop in list_ubops:
                    if obop.ObjPos == ubop.ObjPos:
                        obop.ObjTongge = 1
        except Exception as e:
            print_exception('wgruler > tonggeCheck():{}'.format(str(e)))
            raise e

    def OccupyCheck(self, cur_bop, list_loc_notmycity, list_ubops):
        try:
            valid_action_list = self.valid_actions[cur_bop.obj_id]
            valid_action_types = list(valid_action_list.keys())
            if 5 in valid_action_types:
                return 'O'
            return 'N'
        except Exception as e:
            print_exception('wgruler > OccupyingRightNow():{}'.format(str(e)))
            raise e

    def MoveCheck(self, cur_bop):
        ''' 外部规则针对机动动作的判断(只关注机动动作)
            第一批: 'M' 能够进行机动/ 'N' 不能进行机动
            BUG0: 隐蔽状态下，只有满格机动里才能机动，非满格机动力，无法切换到机动状态，不能机动
        '''
        try:
            valid_action_list = self.valid_actions[cur_bop.obj_id]
            valid_action_types = list(valid_action_list.keys())
            if 1 in valid_action_types:
                return 'M'
            return 'N'
        except Exception as e:
            print_exception('wgruler > Moving():{}'.format (str(e)))
            raise

    def ShootCheck (self, bop_attacker , bop_obj):
        '''外部规则针对射击动作的判断(只关注射击动作)
            第一批: 'S' (射击) | 'N'(不允许射击) | 'MS' 移动射击组合动作(针对坦克) |  'TS' 测试射击能力(针对战车/人员在机动阶段可以射击,需要测试是否保留该射击能力到最终阶段的情况)
            给定参数: 攻击算子bop_attacker, 目标算子 bop_obj, 返回bop_attacker能够对bop_obj的射击动作类型
        '''
        try:
            valid_action_list = self.valid_actions[bop_attacker.obj_id]
            valid_action_types = list(valid_action_list.keys())
            # shoot_paras = valid_action_list[3]
            # if shoot_paras['target_obj_id'] == bop_obj.obj_id:
            if 9 in valid_action_types:
                shoot_paras = valid_action_list[9]
                if shoot_paras[0]['target_obj_id'] == bop_obj.obj_id:
                    return 'S'
            elif 2 in valid_action_types:
                shoot_paras = valid_action_list[2]
                if shoot_paras[0]['target_obj_id'] == bop_obj.obj_id:
                    return 'S'
            # elif 10 in valid_action_types:
            #     shoot_paras = valid_action_list[9]
            #     if shoot_paras['target_obj_id'] == bop_obj.obj_id:
            #         return 'S'
            return 'N'
            # else:
            #     return 'N'
        except Exception as e:
            print_exception('wgruler > Shooting():{}'.format (str(e)))
            raise
