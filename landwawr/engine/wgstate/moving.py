#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-8 下午3:22
# @Author  : sgr
# @Site    : 
# @File    : moving.py


import copy
from common.m_exception import print_exception
from wgstate.state import State
from wgconst.const import StateType
from wgconst.const import MoveState
from wgconst.const import OperatorType
from wgconst.const import ActionStatus
from wgconst.const import MoveParas
from wgconst.const import MoveParameter as ConstParameter


from wgmessage.action_result import ActionResult


def _check(action_msg, state_data):
    """
    动作合法性检查
    :param action_msg:
    :param state_data:
    :return: 是否检查通过
    """
    try:
        assert action_msg.get_action_type() == StateType.Move, \
            'State={} receive error action msg type= {}'.format(StateType.Move, action_msg.get_action_type())
        operator_sets = state_data.get_operator_sets()
        terrain = state_data.get_terrain()
        jm_point_sets = state_data.get_jm_point_sets()
        op_id = action_msg.get_op_id()
        bop = operator_sets.get_bop_by_id(op_id=op_id)
        if not bop:
            action_msg.set_result(ActionResult.CantFindOperator)  # 算子不存在
            return False
        move_flag, code = bop.can_move()
        if not move_flag:
            action_msg.set_result(code)
            return False
        if jm_point_sets.get_flying_points_by_bop(op_id):  # 有正在飞行的炮弹,无法机动
            action_msg.set_result(ActionResult.CantMoveCausePrepareJM)
            return False
        move_path = copy.deepcopy(action_msg.get_move_path())
        move_flag, code = _check_move_paras(bop, move_path=move_path, terrain=terrain, operator_sets=operator_sets)
        if not move_flag:
            action_msg.set_result(code)
            return False

        return True
    except Exception as e:
        print_exception(e)
        raise e


def _check_move_paras(bop, move_path, terrain, operator_sets):
    """
    检查机动参数是否合法
    若参数是机动路径：需满足下一个目标点与当前点相邻；若为行军状态，下一个目标点为道路
    :return:
    """
    try:
        if not move_path:
            return False, ActionResult.InvalidMovePath

        cur_hex = bop.get_hex_pos()
        move_path = _filter_move_path(cur_hex, move_path)
        if not move_path:    # 已到达目标位置
            return False, ActionResult.InvalidMovePath

        next_hex = move_path[0]
        flag, result = _check_next_move_pos_valid(bop, next_hex, terrain, operator_sets)
        return flag, result
    except Exception as e:
        print_exception(e)
        raise e


def _filter_move_path(cur_hex, move_path):
    """
    过滤 move_path 使其第一个元素与 cur_hex 不相等
    :param cur_hex:
    :param move_path:
    :return:
    """
    try:
        next_hex = None
        # 过滤与当前算子位置相同的目标位置
        while move_path and next_hex is None:
            next_hex = move_path[0]
            if next_hex == cur_hex:
                next_hex = None
                move_path.pop(0)
        return move_path
    except Exception as e:
        print_exception(e)
        raise e


def _check_next_move_pos_valid(bop, next_hex, terrain, operator_sets):
    """
    检查下个目标点是否合法：
        与当前位置相邻;
        行军状态下： 当前坐标与下个目标点之间必须有道路;
        行军状态下： 下一格不能有非行军状态下的地面算子；
    :param bop:
    :param next_hex:
    :param terrain:
    :param operator_sets:
    :return:
    """
    try:
        cur_hex = bop.get_hex_pos()
        if not terrain.is_neighbor(cur_hex, next_hex):  # 路径错误,下一个点与当前点不相邻
            return False, ActionResult.InvalidMovePath
        if bop.get_bop_type() == OperatorType.Car:
            if abs(terrain.get_height_change_level(cur_hex, next_hex)) > MoveParas.MaxHeightChangeLevel:
                return False, ActionResult.CantMoveCauseTooSteep
        if bop.get_move_state() == MoveState.March:
            if not terrain.has_road_between_hex(cur_hex, next_hex):
                return False, ActionResult.CantMarchToNotRoad   # 无法行军到非道路位置
            other_bops = operator_sets.get_valid_bops_by_pos(next_hex)
            for bop in other_bops:
                if bop.get_bop_type() != OperatorType.Plane:
                    if not (bop.get_move_state() == MoveState.March and bop.is_moving()):
                        return False, ActionResult.CantMarchCauseOperatorBlock
        return True, ActionResult.Success
    except Exception as e:
        print_exception(e)
        raise e


def _execute(action_msg, state_manager, state_data):
    """
    执行动作
    :param action_msg:
    :param state_manager:
    :param state_data:
    :return:
    """
    try:
        operator_sets = state_data.get_operator_sets()
        obj_id = action_msg.get_op_id()
        bop = operator_sets.get_bop_by_id(op_id=obj_id)
        if not bop:
            action_msg.set_result(ActionResult.CantFindOperator)  # 算子不存在
            return ActionStatus.Done
        valid_state_types = state_manager.get_valid_state_type_by_bop(obj_id)
        if StateType.Move in valid_state_types:
            state_manager.refresh_state(obj_id=obj_id, state_type=StateType.Move,
                                        action_msg=action_msg)
        else:
            state_manager.start_state(obj_id=obj_id, state_type=StateType.Move,
                                      action_msg=action_msg)
        if StateType.RestoreTire in valid_state_types:
            state_manager.stop_state(obj_id=obj_id, state_type=StateType.RestoreTire)

        if StateType.WeaponUnFold in valid_state_types:
            state_manager.stop_state(obj_id=obj_id, state_type=StateType.WeaponUnFold)

        bop.set_stop_status(0)
        if bop.get_move_state() == MoveState.Hide:
            bop.set_move_state(MoveState.NormalMove)
        return ActionStatus.Doing
    except Exception as e:
        print_exception(e)
        raise e


def handle_action(message, state_manager, state_data):
    """
    处理动作:

    :param message:
    :param state_manager:
    :param state_data:
    :return:
    """
    try:
        valid = _check(action_msg=message, state_data=state_data)
        if not valid:
            return ActionStatus.Done
        status = _execute(action_msg=message, state_manager=state_manager, state_data=state_data)
        return status
    except Exception as e:
        print_exception(e)
        raise e


def get_valid_paras(obj_id, state_data):
    """
    :param obj_id:
    :param state_data:
    :return: (True,None) or (False,code)
    """
    try:
        operator_sets = state_data.get_operator_sets()
        bop = operator_sets.get_bop_by_id(op_id=obj_id)
        if not bop:
            return False, ActionResult.CantFindOperator
        flag, code = bop.can_move()
        if not flag:
            return False, code
        jm_point_sets = state_data.get_jm_point_sets()
        if jm_point_sets.get_flying_points_by_bop(obj_id):  # 有正在飞行的炮弹,无法机动
            return False, ActionResult.CantMoveCausePrepareJM

        return True, None
    except Exception as e:
        print_exception(e)
        raise e


class Moving(State):
    """
    机动状态
    """
    def __init__(self, bop, state_data, action_msg_sets):
        super(Moving, self).__init__(bop=bop, state_data=state_data, action_msg_sets=action_msg_sets)
        self.type = StateType.Move

        try:
            self.clock = self.state_data.get_clock()
            self.terrain = self.state_data.get_terrain()
            self.operator_sets = self.state_data.get_operator_sets()
            self.jm_point_sets = self.state_data.get_jm_point_sets()

            self.new_action_msg = None  # 新的动作; self.refresh() 时更新此值;
        except Exception as e:
            print_exception(e)
            raise e

    def enter(self, action_msg):
        """
        进入当前状态
            提取move_path参数;
            设置bop的move_path属性;
        :param action_msg:
        :return:
        """
        try:
            self.action_msg = action_msg
            self.bop.move_path = copy.deepcopy(action_msg.get_move_path())
            _filter_move_path(self.bop.get_hex_pos(), self.bop.move_path)
        except Exception as e:
            print_exception(e)
            raise e

    def refresh(self, action_msg):
        """
        刷新当前状态:
            与enter操作相同
        :param action_msg:
        :return:
        """
        try:
            assert isinstance(self.bop.move_path, list) and self.bop.move_path, "not moving but enter refresh function"
            self.new_action_msg = action_msg
        except Exception as e:
            print_exception(e)
            raise e

    def update(self, state_manager):
        """
        更新当前状态:
            1. 计算算子速度
            2. 若算子速度 > 0:
                2.1 更新算子位置
                2.2 更新算子疲劳值, 更新算子速度
            3. 若算子速度 == 0:
                结束本状态
            Todo: 行军无法超越前方算子
        :return:
        """
        try:
            speed = self._cal_bop_speed()
            if speed > 0:
                self._update_bop_pos(state_manager)
            if self.bop:
                if self.bop.speed == 0:
                    self._end(state_manager)

        except Exception as e:
            print_exception(e)
            raise e

    def stop(self, state_manager):
        """
        停止当前状态:
            1. 设置算子的move_path, speed, cur_pos属性为默认值
            2. 更新动作状态
        释放内存；
        :return:
        """
        self._end_move_state()
        bop_id = self.bop.get_bop_id()
        valid_states = state_manager.get_valid_state_type_by_bop(obj_id=bop_id)
        if self.bop.get_tire_level() > 0:
            assert StateType.RestoreTire not in valid_states, "机动中不应恢复疲劳"
            state_manager.start_state(obj_id=bop_id, state_type=StateType.RestoreTire, action_msg=None)

        assert StateType.MoveToStop not in valid_states, "机动中不应正在向停止转换"
        if self.bop.get_bop_type() != OperatorType.Plane and self.bop.get_move_state() != MoveState.March:
            state_manager.start_state(obj_id=bop_id, state_type=StateType.MoveToStop, action_msg=None)

        super(Moving, self).stop(state_manager)
        self.__del__()

    def _cal_bop_speed(self):
        """
        计算算子当前速度：
            1. 如果算子当前速度 > 0: 直接返回当前速度
            2. 如果算子move_path为空, 返回 0
            3. 从move_path中获取下一个目标点next_hex，如果与当前位置不是相邻格或者非法行军，返回0, 记录动作结果
            4. 根据next_hex计算算子速度(格/s), 并返回
        :return: 算子当前速度
        """
        try:
            if self.bop.speed > 0:
                return self.bop.speed
            if not self.bop.move_path:
                return 0
            next_hex = self.bop.move_path[0]
            flag, result = _check_next_move_pos_valid(self.bop, next_hex, self.terrain, self.operator_sets)
            if not flag:
                self.action_msg.set_result(result)
                return 0
            cur_speed = self._cal_bop_speed_by_next_hex(next_hex=next_hex)
            self.bop.speed = cur_speed
            return cur_speed
        except Exception as e:
            print_exception(e)
            raise e

    def _cal_bop_speed_by_next_hex(self, next_hex):
        """
        根据next_hex计算算子速度(格/s):
            1. 获取算子基本速度
            2. 根据算子状态获取算子机动类型，计算地形对速度的影响值
            3. 获取机动状态对算子速度的影响值
            4. 计算算子速度
        :return: 速度(格/s)
        """
        try:
            basic_speed = self.bop.get_basic_speed()
            move_type = self.bop.get_terrain_move_type()
            cur_hex = self.bop.get_hex_pos()
            speed_ratio = self.terrain.get_speed_ratio(move_type=move_type, pos1=cur_hex, pos2=next_hex)
            cur_speed = basic_speed * speed_ratio
            move_state = self.bop.get_move_state()
            if move_state in ConstParameter.SpeedRatioByMoveState.keys():
                cur_speed = cur_speed * ConstParameter.SpeedRatioByMoveState[move_state]
            cur_speed = self.terrain.change_speed_to_hex_sec(cur_speed)
            return cur_speed
        except Exception as e:
            print_exception(e)
            raise e

    def _update_bop_pos(self, state_manager):
        """
        更新算子机动位置(格%):
            1. 算子位置 += (格/s) * (s/步)
            2. 如果机动位置 >= 1格:
                2.1 机动位置置0
                2.2 更新算子move_path
                2.2 更新算子坐标
                2.3 更新算子速度
            返回算子速度
        :return: 算子速度
        """
        try:
            self.bop.cur_pos += self.bop.speed * self.clock.get_tick()
            if self.bop.cur_pos >= 1:
                self.bop.cur_pos = 0
                cur_hex = self.bop.move_path.pop(0)
                self._bop_hex_changed(cur_hex, state_manager)
                if not self.bop:    # died
                    return 0
                self.bop.speed = 0

                if self.new_action_msg:
                    self._end_move_state()
                    move_path = copy.deepcopy(self.new_action_msg.get_move_path())
                    move_path = _filter_move_path(cur_hex, move_path)
                    self.bop.set_bop_move_path(move_path)
                    self.action_msg = self.new_action_msg

                if self._update_bop_tire():
                    self._cal_bop_speed()

            return self.bop.speed
        except Exception as e:
            print_exception(e)
            raise e

    def _bop_hex_changed(self, cur_hex, state_manager):
        """
        更新算子的坐标
        :param cur_hex:
        :return:
        """
        try:
            last_hex = self.bop.cur_hex
            self.bop.cur_hex = cur_hex
            self._update_passenger_pos()
            self.operator_sets.on_bop_hex_changed(self.bop, last_hex)
            if self.bop.get_bop_type() != OperatorType.Plane:
                self.jm_point_sets.on_bop_hex_changed(bop=self.bop,
                                                      state_manager=state_manager)
        except Exception as e:
            print_exception(e)
            raise e

    def _update_passenger_pos(self):
        try:
            passenger_ids = self.bop.get_passenger_ids()
            passenger_bops = [self.operator_sets.get_bop_by_id(obj_id) for obj_id in passenger_ids]
            for bop in passenger_bops:
                if bop is not None:
                    bop.set_hex_pos(self.bop.get_hex_pos())
        except Exception as e:
            print_exception(e)
            raise e

    def _update_bop_tire(self):
        """
                更新算子的疲劳值：
                    1. 若是步兵：
                        1.1 若机动类型会累积疲劳：
                            1.1.1 更新算子疲劳累积时间
                            1.1.2 如果疲劳累积时间大于最大值：疲劳等级加一，清空疲劳累积时间
                            1.1.3 如果疲劳等级达到最大值，算子速度置0, 记录动作结果
                    返回算子速度
                :return: 是否能继续机动
                """
        try:
            if self.bop.get_bop_type() == OperatorType.People:
                move_state = self.bop.get_move_state()
                if move_state in ConstParameter.MaxTireAccStep.keys():
                    self.bop.tire += 1
                    if move_state in ConstParameter.MaxTire:
                        if self.bop.tire >= ConstParameter.MaxTire[move_state]:
                            self.bop.speed = 0
                            result = ActionResult.CantMoveUnderTireLv2 if self.bop.tire >= 2 else ActionResult.CantCharge2UnderTireLv1
                            self.action_msg.set_result(result)
                            return False
            return True
        except Exception as e:
            print_exception(e)
            raise e

    # def _update_bop_tire(self):
    #     """
    #     更新算子的疲劳值：
    #         1. 若是步兵：
    #             1.1 若机动类型会累积疲劳：
    #                 1.1.1 更新算子疲劳累积时间
    #                 1.1.2 如果疲劳累积时间大于最大值：疲劳等级加一，清空疲劳累积时间
    #                 1.1.3 如果疲劳等级达到最大值，算子速度置0, 记录动作结果
    #         返回算子速度
    #     :return: 算子速度
    #     """
    #     try:
    #         if self.bop.get_bop_type() == OperatorType.People:
    #             move_state = self.bop.get_move_state()
    #             if move_state in ConstParameter.MaxTireAccStep.keys():
    #                 self.bop.tire_accumulate_time += self.clock.get_tick()
    #                 max_time = ConstParameter.MaxTireAccStep[move_state]
    #                 if self.bop.tire_accumulate_time > max_time:
    #                     self.bop.tire += 1
    #                     self.bop.tire_accumulate_time = 0
    #                     if move_state in ConstParameter.MaxTire:
    #                         if self.bop.tire >= ConstParameter.MaxTire[move_state]:
    #                             self.bop.speed = 0
    #                             result = ActionResult.CantMoveUnderTireLv2 if self.bop.tire >= 2 \
    #                                 else ActionResult.CantCharge2UnderTireLv1
    #                             self.action_msg.set_result(result)
    #         return self.bop.speed
    #     except Exception as e:
    #         print_exception(e)
    #         raise e

    def _end(self, state_manager):
        """
        结束此状态:
            state_manager结束此状态
        :param state_manager:
        :return:
        """
        try:
            state_manager.stop_state(obj_id=self.bop.obj_id, state_type=self.type)
        except Exception as e:
            print_exception(e)
            raise e

    def _end_move_state(self):
        """停止机动状态"""
        try:
            self.bop.move_path = []
            self.bop.speed = 0
            self.bop.cur_pos = 0
            if self.action_msg is not None:
                assert self.action_msg_sets is not None, 'State {} need action_msg_sets'.format(self.__class__.__name__)
                self.action_msg_sets.set_action_status(action_id=self.action_msg.get_msg_id(), status=ActionStatus.Done)
        except Exception as e:
            print_exception(e)
            raise e

    def __del__(self):
        super(Moving, self).__del__()
        self.clock = None
        self.terrain = None
        self.operator_sets = None
        self.jm_point_sets = None
        self.new_action_msg = None


if __name__ == "__main__":
    l = [1, 2]
    print(l[0: 1])
    c = l.pop(0)
    print('c={}, l={}'.format(c, l))
    a = 1