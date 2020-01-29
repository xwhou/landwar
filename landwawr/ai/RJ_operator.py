import sys
sys.path.append("../engine/wgmap")
sys.path.append("../engine/wgoperator")
sys.path.append("../engine/wgconst")
from basic_operator import BasicOperator
from wgconst.const import OperatorType
from wgmap.terrain import cvt_int4_to_int6

class AI_BasicOperator(BasicOperator):
    def __init__(self, terrain, data_source):
        super(AI_BasicOperator, self).__init__(terrain, data_source)

        self.ID = self.obj_id   # 算子ID
        self.Room = 1
        self.UserID = 1
        self.GameColor = self.color # 算子阵营
        self.Army = 111
        self.ObjType = self.type    # 类型 1-步兵 2-车辆 3-空中

        if self.sub_type == 0 or self.sub_type == 1 or self.sub_type == 2:
            self.ObjTypeX = self.sub_type   # 细分类型 0-坦克 1-战车 2-步兵
        elif self.sub_type == 3:
            self.ObjTypeX = 11  # 炮兵
        elif self.sub_type == 4:
            self.ObjTypeX = 10  # 无人战车
        elif self.sub_type == 5:
            self.ObjTypeX = 30  # 无人机
        elif self.sub_type == 6:
            self.ObjTypeX = 3   # 直升机
        elif self.sub_type == 7:
            self.ObjTypeX = 4   # 巡飞弹

    #   self.A1         # 行进间射击能力   和basicoperator一样，可以直接用
        self.D0 = 1 if self.speed > 0 else 0    # 是否在机动
        self.D1 = 1
        self.D3 = 0  # 行军的总格数目
        self.B0 = self.armor    # 装甲类型 0-无装甲， 1-轻型装甲，2-中型装甲，3-重型装甲，4-复合装甲
        self.S1 = self.observe_distance[OperatorType.People]     # 人观察距离
        self.S2 = self.observe_distance[OperatorType.Car]     # 车观察距离
        self.ObjPos = cvt_int4_to_int6(self.cur_hex)     #六角格坐标，int6
        self.LastPos = self.ObjPos  # 最后位置
        # self.ObjStep = self.basic_speed     # 基础速度
        self.ObjStep = 5
        self.ObjStepMax = self.ObjStep  # 最大机动力
        self.ObjPass = self.move_state if self.move_state != 4 else 0   # 车辆机动状态 0-机动 1-行军
        self.ObjKeep = self.keep    # 压制状态
        self.ObjHide = 1 if self.move_state == 4 else 0     # 隐蔽状态
        self.ObjRound = self.speed      # 移动速度
        self.ObjAttack = 1 if self.weapon_cool_time != 0 else 0
        self.ObjTire = self.tire  # 疲劳度 正常：0 一级疲劳：1 二级疲劳：2
        self.ObjBlood = self.blood      # 算子血量
    #   self.C2          # 剩余子弹数   和basicoperator一样，可以直接用
        self.A3 = self.C3   # 剩余导弹数
        self.Wz = self.carry_weapon_ids     # 携带武器列表

        if self.sub_type == 1:
            self.ObjSup = 0 if not self.launch_ids else self.launch_ids[-1]     # 对于车来说，Sup没有算子上过车为0，有算子上过为最后上车算子的ID
        else:
            self.ObjSup = 0 if self.launcher is None else self.launcher     # 对于其他算子来说，没上过车为0，上过车为绑定战车的ID

        self.ObjSpace = self.space      # 最大搭乘数量
        self.ObjSonNum = len(self.passenger_ids)    # 当前运兵数量
        self.ObjValue = self.value      # 算子分值
        self.ObjDate = []
        self.ObjRadar = self.weapon_cool_time   # 射击冷却时间
        self.ObjStack = 0







