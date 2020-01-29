#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-11-13 下午2:46
# @Author  : sgr
# @Site    : 
# @File    : const.py


class StateType:
    Null = 0
    Move = 1  # 机动
    Shoot = 2  # 射击
    GetOn = 3  # 上车
    GetOff = 4  # 下车
    Occupy = 5  # 夺控
    ChangeState = 6  # 状态转换
    RemoveKeep = 7  # 移除压制
    JMPlan = 8  # 间瞄计划
    GuideShoot = 9  # 引导射击
    TongGeShoot = 10  # 同格射击
    RestoreKeep = 11  # 压制恢复
    RestoreTire = 12  # 疲劳恢复
    WeaponUnFold = 13  # 武器展开
    WeaponCool = 14  # 武器冷却
    MoveToStop = 15   # 机动切换到停止
    FlyMissileDestroy = 16  # 巡飞弹自毁倒计时


class StateClass:
    HandleActionFun = "handle_action"
    ValidActionFun = "get_valid_paras"
    AllStates = {
        StateType.Move: {'module': 'wgstate.moving', 'class': 'Moving'},
        StateType.Shoot: {'module': 'wgstate.shooting', 'class': "None"},
        StateType.GetOn: {'module': 'wgstate.getting_on', 'class': 'GettingOn'},
        StateType.GetOff: {'module': 'wgstate.getting_off', 'class': 'GettingOff'},
        StateType.Occupy: {'module': 'wgstate.occupy', 'class': 'None'},
        StateType.ChangeState: {'module': 'wgstate.switching_state', 'class': 'SwitchingState'},
        StateType.RemoveKeep: {'module': 'wgstate.remove_keep', 'class': 'None'},
        StateType.JMPlan: {'module': 'wgstate.jm_plan', 'class': 'None'},
        StateType.GuideShoot: {'module': 'wgstate.guide_shoot', 'class': 'None'},
        StateType.RestoreKeep: {'module': 'wgstate.restore_keep', 'class': 'RestoringKeep'},
        StateType.RestoreTire: {'module': 'wgstate.restore_tire', 'class': 'RestoringTire'},
        StateType.WeaponUnFold: {'module': 'wgstate.weapon_unfolding', 'class': 'WeaponUnfolding'},
        StateType.WeaponCool: {'module': 'wgstate.weapon_cooling', 'class': 'WeaponCooling'},
        StateType.MoveToStop: {'module': 'wgstate.move_to_stop', 'class': 'MovingToStop'},
        StateType.FlyMissileDestroy: {'module': 'wgstate.fly_missile_destroy', 'class': 'FlyMissileDestroy'},
    }

# StateClass = {
#                 "handle_action": "handle_action",
#                 "valid_action_paras": "get_valid_paras",
#                 StateType.Move: {'module': 'wgstate.moving', 'class': 'Moving'},
#                 # StateType.Shoot: {'module': 'wgstate.shooting', 'class': 'Shooting'},
#                 # StateType.GetOn: {'module': 'wgstate.getting_on', 'class': 'GettingOn'},
#             }


SupportActions = [StateType.Move, StateType.Shoot, StateType.GetOn, StateType.GetOff, StateType.Occupy,
                  StateType.ChangeState, StateType.RemoveKeep, StateType.JMPlan, StateType.GuideShoot]


SupportActionsNotes = ["{}-机动".format(StateType.Move), "{}-射击".format(StateType.Shoot), "{}-上车".format(StateType.GetOn),
                       "{}-下车".format(StateType.GetOff), "{}-夺控".format(StateType.Occupy),
                       "{}-切换状态".format(StateType.ChangeState), "{}-移除压制".format(StateType.RemoveKeep),
                       "{}-间瞄".format(StateType.JMPlan), "{}-引导射击".format(StateType.GuideShoot)]


class MoveState:
    NormalMove = 0  # 正常机动
    March = 1  # 行军
    Charge_1 = 2  # 一级冲锋
    Charge_2 = 3  # 二级冲锋
    Hide = 4  # 掩蔽
    all_states = [NormalMove, March, Charge_1, Charge_2, Hide]


class MoveParas:
    MaxHeightChangeLevel = 5


class TerrainMoveType:
    CarMove = 0
    CarMarch = 1
    PeoMove = 2
    PlaneMove = 3


class OperatorType:
    Car = 2  # 车辆
    People = 1  # 步兵
    Plane = 3  # 空中


class OperatorSubType:
    Tank = 0  # 坦克
    Chariot = 1  # 战车
    Soldier = 2  # 士兵
    Artillery = 3  # 炮兵
    AutoChariot = 4  # 无人战车
    AutoPlane = 5  # 无人机
    Helicopter = 6  # 武装直升机
    FlyMissile = 7  # 巡飞弹


class ActionStatus:
    Todo = 0  # 待处理
    Doing = 1  # 正在处理
    Done = 2  # 处理完毕


class InvalidDamage:
    InvalidAttackLevel = 0  # 计算出的AttackLevel<=此值表示射击无效
    InvalidDamageValue = -1   # 计算出的Damage<=此值表示射击无效


class HexType:
    Normal = 0
    Water = 1
    Road = 2
    Forest = 4
    Village = 5
    Soft = 6


class JMPointStatus:
    Flying = 0  # 炮弹飞行中
    Booming = 1    # 爆炸中
    Invalid = 2     # 失效


class JMAlignStatus:
    NoAlign = 0     # 无较射
    HexAlign = 1    # 格内较射
    TargetAlign = 2  # 目标较射


class Color:
    RED = 0
    BLUE = 1
    GREEN = -1
    name_to_color = {
        'RED': RED,
        'BLUE': BLUE,
        'GREEN': GREEN
    }
    all_colors = [RED, BLUE]
    enemy_colors = {
        RED: [BLUE],
        BLUE: [RED]
    }


class DBConfig:
    # 数据库相关配置
    Host = "10.1.14.70"
    Port = "3306"
    User = "root"
    Pwd = "root"
    WarGameDB = "WARGAME"
    ReviewDB = "RTSReview"
    WeaponTable = "WpData"
    RoomTable = "Room"


class MatchStatus:
    NotStarted = 0
    Matching = 1
    Ended = 2


class MatchMode:
    RR = 0
    RJ = 1
    JJ = 2


class EngineVersion:
    RTS = 2.0


class BasicSpeed:   # 算子的基础机动速度 km/h
    People = 5
    Car = 36
    Plane = 100


class ClockParas:
    time1 = 1800    # 30min
    time2 = 2880    # 48min
    MaxTime = {
        1531: time1,  # "城镇居民地连级想定"
        3531: time2,  # "城镇居民地营级想定"
        1631: time1,  # "岛上台地连级想定"
        3631: time2,  # "岛上台地营级想定"
        1231: time1,  # "高原通道连级想定"
        3231: time2,  # "高原通道营级想定"
    }
    MaxTimeDefault = 1800
    SpeedUpRatio = 50    # 加速比
    FPS = 1   # 每s更新步长数


ScenarioInfo = {
    1531: {
        "MapName": "城镇居民地",
    },
    3531: {
        "MapName": "城镇居民地",
    },
    1631: {
        "MapName": "岛上台地",
    },
    3631: {
        "MapName": "岛上台地",
    },
    1231: {
        "MapName": "高原通道",
    },
    3231: {
        "MapName": "高原通道",
    },
}


MaxPassengerNums = {
    OperatorSubType.Soldier: 1,
    OperatorSubType.AutoChariot: 1,
    OperatorSubType.FlyMissile: 2

}


class MoveParameter:
    MaxTireAccStep = {
        MoveState.Charge_1: 75,
        MoveState.Charge_2: 30,
    }   # 不同冲锋等级最大持续时间
    SpeedRatioByMoveState = {
        MoveState.Charge_1: 2,
        MoveState.Charge_2: 4,
    }  # 算子速度受机动状态影响的倍率
    MaxTire = {
        MoveState.NormalMove: 2,
        MoveState.Charge_1: 2,
        MoveState.Charge_2: 1,
    }  # 最大疲劳等级


class TimeParameter:
    FlyMissileAliveTime = 1200
    GettingOffTime = 75
    GettingOnTime = 75
    MoveToStopTime = 75
    RestoreKeepTime = 150
    RestoreTireTime = {
        1: 75,  # 1级疲劳 75s
        2: 75   # 2级疲劳 75s
    }
    SwitchStateTime = {
        MoveState.NormalMove: 75,
        MoveState.Hide: 75,
        MoveState.March: 75,
        MoveState.Charge_1: 0,
        MoveState.Charge_2: 0,
    }
    WeaponCoolTime = {
        OperatorSubType.Tank: 75,
        OperatorSubType.Chariot: 75,
        OperatorSubType.Soldier: 75,
        OperatorSubType.Artillery: 150,
        OperatorSubType.AutoChariot: 75,
        OperatorSubType.AutoPlane: 75,
        OperatorSubType.Helicopter: 75,
        OperatorSubType.FlyMissile: 75
    }
    WeaponUnfoldTime = 75
    JMTime = {
        "Fly": 150,
        "Boom": 300
    }
