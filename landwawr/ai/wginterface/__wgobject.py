# coding:utf-8

from ctypes import *
import pandas



global MaxObjNum #最大班车数
MaxObjNum = 5

class BasicTensor(Structure):
    _fields_ = [('ndim', c_int),            #维度数目
                ('shape', POINTER(c_int)),  #各维大小
                ('data', POINTER(c_float))] #数据指针

class BasicOperator(Structure):
    pass

    def __hash__(self):
        try:
            list_idens = [self.GameColor, self.ObjArmy, self.ObjType]
            list_states = [self.D1,
                           self.D3,
                           self.ObjPos,
                           self.ObjStep,
                           self.ObjPass,
                           self.ObjKeep,
                           self.ObjHide,
                           self.ObjRound,
                           self.ObjAttack,
                           # self.ObjTire,
                           # self.ObjStack,
                           self.ObjBlood,
                           self.C2,
                           self.C3,
                           self.ObjSup,
                           self.ObjSonNum,
                           # self.ObjTongge,
                           # self.ObjFlagTask,
                           # self.ObjFlagMoving,
                           # self.isVisible,
                           ]
            hashkey = hash(str(list_idens + list_states))
            return hashkey
        except Exception as e:
            raise

arr_int5_type = c_int * 5

BasicOperator._fields_ = [('ObjID',c_int),  # 算子自身ID
                          ('RoomID',c_int),  # 房间号
                          ('UserID',c_int),  # 用户ID
                          ('GameColor', c_int),  # 游戏双方 红：0，蓝：1 =ObjFlag=ObjColor
                          
                          # ('ObjName',c_wchar_p), # 算子名称（汉语拼音：如战车棋子等）
                          ('ObjArmy',c_int), # 标志x营y排z班
                          # ('ObjIco', c_wchar_p),  #算子军标名称
                          ('ObjType', c_int),   # 算子类型 人：1，车：2
                          ('ObjTypeX', c_int),  # 算子类型的进一步细化：坦克 0/  战车1 / 人员2
                          
                          ('A1', c_int),  # 行进间射击能力 无：0 有：1
                          ('D1', c_int),  # 行军状态下消耗一个机动力单位可以移动的格子数目
                          ('D3', c_int),  # 当前行军的总格数目
                          ('B0', c_int),  # 装甲类型 无装甲：0，轻型装甲：1，中型装甲：2，重型装甲：3，合装甲：4
                          ('S1', c_int),  # 对人观察距离
                          ('S2', c_int),  # 对车观察距离
                          
                          ('ObjPos', c_int),  # 当前位置
                          ('ObjLastPos', c_int),  # 算子上一个时刻的位置，用于同格交战不胜之后的回退
                          ('ObjStep', c_float),  # 剩余机动力
                          ('ObjStepMax', c_float),  # 算子机动力上限
                          
                          ('ObjPass', c_int),  # 车辆机动状态 机动：0 行军：非0  短停：2
                          ('ObjKeep', c_int),  # 是否被压制 否：0 是：非0
                          ('ObjHide', c_int),  # 是否遮蔽 否：0 是：非0
                          ('ObjRound', c_int),  # 是否已机动 否：0 是：非0
                          ('ObjAttack', c_int),  # 是否已射击 否：0 是：非0
                          ('ObjTire', c_int),  # 疲劳度 正常：0 一级疲劳：1 二级疲劳：2
                          ('ObjStack', c_int),  # 算子是否发生了堆叠 0 未发生 1 发生
                          ('ObjTongge', c_int),  # 算子当前是否处于同格状态，0否 1是
                          ('ObjTonggeOrder', c_int), # 先进入同格位置，被动同格，1 ； 后进入同格位置，主动同格 2
                          ('ObjTonggeShootCountLeft', c_int), # 在同格交战环节，剩余的射击次数
                          
                          
                          ('ObjBlood', c_int),  # 当前车班数
                          ('C2', c_int),  # 剩余弹药数
                          ('C3', c_int),  # 剩余导弹数
                          
                          ('ObjWzNum', c_int),  # 关联武器数量
                          ('ObjMaxWzNum', c_int), # ObjArrWzIDs的长度，默认为5
                          ('ObjArrWzIDs', c_int * 5), # 算子挂载的武器编号列表 换成5个整形数据
                          
                          ('ObjSup', c_int),  # 算子是否乘车（在车上） 0 不乘车、1 乘车
                          ('ObjSpace', c_int),  # 运兵数量上限
                          ('ObjSonNum', c_int),  # 当前运兵数量
                          ('ObjSonID',c_int),   # 车上的人员算子的ID编号
                          ('ObjValue', c_float),  #算子分值
                          
                          ('ObjFlagTask', c_int), # 基于态势的任务分配 0 进攻 / 1 防御 / 2 撤退
                          ('ObjFlagMoving', c_int), # 针对无行射能力的算子, 用在机动环节检测到可以射击的情况下, 保留机动能力以便于在最终阶段可以射击
                          ('isVisible', c_int), # 该算子能够被对方看到(1) / 不能(0)
                          ('ObjActState', c_int) , # 当前算子位置是否准确
                          ('ObjCanShoot', c_int),
                          ('ObjCanOccupy', c_int),
                          ('ObjCanSuicide', c_int),
                          ('ObjIndex', c_int), # sgr, 增加算子的索引信息

                        ]

'''modify:2018年11月06日 宋国瑞 增加ObjActState标识是否为伪算子 1-真实算子,0-伪算子'''
l_pdfield = ['ID','Room','UserID','GameColor','Army','ObjType','A1','D1','D3','B0','S1','S2','ObjPos','ObjStep','ObjStepMax',
             'ObjPass','ObjKeep','ObjHide','ObjRound','ObjAttack','ObjBlood','C2','A3','Wz','ObjSup','ObjSpace','ObjSonNum','ObjValue','ObjActState']
def Gen_Op(Objects, WuziData = None):
    try:
        op=BasicOperator()
        
        op.ObjID = Objects.ID
        op.RoomID = Objects.Room
        op.UserID = Objects.UserID
        op.GameColor = 0 if Objects.GameColor == 'RED' else 1
        # op.ObjName = Objects.ObjName # 汉语步兵棋子转码的问题？
        op.ObjArmy = int(Objects.Army) # GameColor + Amy + ObjType 三者可以作为算子的唯一标识
        # op.ObjIco=Objects.ObjIco
        op.ObjType = Objects.ObjType
        op.ObjTypeX= Objects.ObjTypeX
        
        op.A1 = Objects.A1
        if op.A1 == 1:
            op.ObjTypeX = 0  # 坦克
        elif op.ObjType == 2:
            op.ObjTypeX = 1# 战车
        else:
            op.ObjTypeX = 2  # 人员
        
        op.D1 = Objects.D1 # 出现/0错误
        op.D3 = Objects.D3
        op.B0 = Objects.B0
        op.S1 = Objects.S1
        op.S2 = Objects.S2
        
        op.ObjPos = Objects.ObjPos
        op.ObjLastPos = Objects.ObjPos
        op.ObjStep = Objects.ObjStepMax
        op.ObjStepMax = Objects.ObjStep
    
        # 状态标志位置
        op.ObjPass = Objects.ObjPass
        op.ObjKeep = Objects.ObjKeep
        op.ObjHide = Objects.ObjHide
        op.ObjRound = Objects.D0
        op.ObjAttack = Objects.ObjAttack
        op.ObjTire = 0
        op.ObjStack = 0
        op.ObjTongge = 0
        op.ObjTonggeOrder = 0
        op.ObjTonggeShootCountLeft = 0
        
        op.ObjBlood = Objects.ObjBlood
        op.C2 = int(Objects.C2) #用于武器的弹药数
        op.C3 = int(Objects.A3) # 用于武器的导弹数
    
        #  武器部分
        # wzlist = Objects.Wz.split( ',' )
        wzlist = Objects.Wz
        op.ObjWzNum =len(wzlist)
        op.ObjMaxWzNum = 5
        assert (op.ObjWzNum < op.ObjMaxWzNum)
        
        my_wzids = arr_int5_type()
        for i in range(op.ObjWzNum):
            my_wzids[i] = c_int(int(wzlist[i]))
        op.ObjArrWzIDs = my_wzids
    
        op.ObjSup = Objects.ObjSup  # 标记算子是否在车上
        op.ObjSpace = Objects.ObjSpace
        op.ObjSonID = Objects.ObjSup  #乘车算子的ObjID编号
        op.ObjSonNum =Objects.ObjSonNum #乘车人员的数量（班数）
        op.ObjValue = Objects.ObjValue
        
        #  算子模型标记
        op.ObjFlagTask = 0
        op.ObjFlagMoving = 1
        op.isVisible = 1
    
        # 策略AI的标记
        op.ObjActState = 1
        op.ObjCanShoot = 0
        op.ObjCanOccupy = 0
        op.ObjCanSuicide = 0
        
        op.ObjIndex = 0
    
        return op
    except Exception as e:
        raise e

def bop2Ser(bop):
    '''modify:2018年11月06日 宋国瑞 增加ObjActState标识是否为伪算子 1-真实算子,0-伪算子
    modify:2018年11月06日 宋国瑞 创建Series时指定列名应使用index关键字
    '''
    try:
        ser = pandas.Series(index=l_pdfield,dtype=int)
        ser.ID = bop.ObjID
        ser.Room = bop.RoomID
        ser.UserID = bop.UserID
        ser.GameColor = 'RED' if bop.GameColor == 0 else 'BLUE'
        # op.ObjName = Objects.ObjName # 汉语步兵棋子转码的问题？
        ser.Army = int(bop.ObjArmy)  # GameColor + Amy + ObjType 三者可以作为算子的唯一标识
        # op.ObjIco=Objects.ObjIco
        ser.ObjType = bop.ObjType

        ser.A1 = bop.A1
        ser.D1 = bop.D1  # 出现/0错误
        ser.D3 = bop.D3  # 出现/0错误
        ser.B0 = bop.B0
        ser.S1 = bop.S1
        ser.S2 = bop.S2


        ser.ObjPos = bop.ObjPos
        ser.ObjLastPos = bop.ObjPos
        ser.ObjStep = bop.ObjStepMax
        ser.ObjStepMax = bop.ObjStep

        # 状态标志位置
        ser.ObjPass = bop.ObjPass
        ser.ObjKeep = bop.ObjKeep
        ser.ObjHide = bop.ObjHide
        ser.ObjRound = bop.ObjRound
        ser.ObjAttack = bop.ObjAttack
        ser.ObjBlood = bop.ObjBlood
        ser.C2 = bop.C2  # 用于武器的弹药数
        ser.A3 = bop.C3  # 用于武器的导弹数

        #  武器部分
        l_wz = []
        for wz in bop.ObjArrWzIDs:
            l_wz.append(int(wz))
        str_wz =''
        if len(l_wz) > 0:
            str_wz = str(l_wz[0])
            for i in range(1,len(l_wz)):
                if l_wz[i] == 0:
                    break
                str_wz = str_wz + ', ' + str(l_wz[i])
        ser.Wz = str_wz

        ser.ObjSup = bop.ObjSup  # 标记算子是否在车上
        ser.ObjSpace = bop.ObjSpace
        # ser.ObjSonID = bop.ObjSup  # 乘车算子的ObjID编号
        ser.ObjSonNum = bop.ObjSonNum  # 乘车人员的数量（班数）
        ser.ObjValue = bop.ObjValue


        ser.ObjActState = bop.ObjActState #标识是否为伪算子 1-真实算子,0-伪算子
        return ser
    except Exception as e:
        print(e)
        raise

def op_deepcopy(op_s):
    op = BasicOperator()
    assert (op_s)
    op.ObjID = op_s.ObjID
    op.RoomID = op_s.RoomID
    op.UserID = op_s.UserID
    op.GameColor = op_s.GameColor
    # op.ObjName = op_s.ObjName
    # op.ObjDataID = op_s.ObjDataID
    op.ObjArmy = op_s.ObjArmy
    # op.ObjIco=op_s.ObjIco
    op.ObjType = op_s.ObjType
    op.ObjTypeX = op_s.ObjTypeX
    
    op.A1 = op_s.A1
    op.D1 = op_s.D1  # 出现/0错误
    op.D3 = op_s.D3  # 出现/0错误
    op.B0 = op_s.B0
    op.S1 = op_s.S1
    op.S2 = op_s.S2
    
    op.ObjPos = op_s.ObjPos
    op.ObjLastPos = op_s.ObjLastPos
    op.ObjStep = op_s.ObjStep
    op.ObjStepMax = op_s.ObjStepMax
    
    # 状态标志位置
    op.ObjPass = op_s.ObjPass
    op.ObjKeep = op_s.ObjKeep
    op.ObjHide = op_s.ObjHide
    op.ObjRound = op_s.ObjRound
    op.ObjAttack = op_s.ObjAttack
    op.ObjTire = op_s.ObjTire
    op.ObjStack = op_s.ObjStack
    op.ObjTongge = op_s.ObjTongge
    op.ObjTonggeOrder = op_s.ObjTonggeOrder
    op.ObjTonggeShootCountLeft = op_s.ObjTonggeShootCountLeft
    
    op.ObjBlood = op_s.ObjBlood
    op.C2 = op_s.C2
    op.C3 = op_s.C3
    
    #  武器部分
    op.ObjWzNum = op_s.ObjWzNum
    op.ObjMaxWzNum = op_s.ObjMaxWzNum
    
    # op.ObjWz0 = op_s.ObjWz0
    # op.ObjWz1 = op_s.ObjWz1
    # op.ObjWz2 = op_s.ObjWz2
    # op.ObjWz3 = op_s.ObjWz3
    # op.ObjWz4= op_s.ObjWz4
    
    my_wzids = arr_int5_type()
    for i in range(op_s.ObjWzNum):
        my_wzids[i] = op_s.ObjArrWzIDs[i]
    op.ObjArrWzIDs = my_wzids
    
    op.ObjSup = op_s.ObjSup  # 标记算子是否在车上
    op.ObjSpace = op_s.ObjSpace
    op.ObjSonID = op_s.ObjSonID  # 乘车算子的ObjID编号
    op.ObjSonNum = op_s.ObjSonNum  # 乘车人员的数量（班数）
    op.ObjValue = op_s.ObjValue
    
    op.ObjFlagMoving = op_s.ObjFlagMoving
    op.ObjFlagTask = op_s.ObjFlagTask
    op.isVisible = op_s.isVisible
    
    op.ObjActState = op_s.ObjActState
    op.ObjCanShoot = op_s.ObjCanShoot
    op.ObjCanOccupy = op_s.ObjCanOccupy
    op.ObjCanSuicide = op_s.ObjCanSuicide
    op.ObjIndex = op_s.ObjIndex
    return op



def checkBopEq(bop_a, bop_b):
    try:
        if not bop_a.D1 == bop_b.D1:
            print('D1')
            assert  False
        if not bop_a.D3 == bop_b.D3:
            print('D3')
            assert  False

        if not bop_a.ObjPos == bop_b.ObjPos:
            print('ObjPos')
            assert  False

        if not bop_a.ObjStep == bop_b.ObjStep:
            print('ObjStep')
            assert  False

        if not bop_a.ObjPass == bop_b.ObjPass:
            print('ObjPass')
            assert  False

        if not bop_a.ObjKeep == bop_b.ObjKeep:
            print('ObjKeep')
            assert  False

        if not bop_a.ObjHide == bop_b.ObjHide:
            print('ObjHide')
            assert  False

        if not bop_a.ObjRound == bop_b.ObjRound:
            print('ObjRound')
            assert  False

        if not bop_a.ObjAttack == bop_b.ObjAttack:
            print('ObjAttack')
            assert  False

        if not bop_a.ObjBlood == bop_b.ObjBlood:
            print('ObjBlood')
            assert  False

        if not bop_a.C2 == bop_b.C2:
            print('C2')
            assert  False

        if not bop_a.C3 == bop_b.C3:
            print('C3')
            assert  False

        if not bop_a.ObjSonNum == bop_b.ObjSonNum:
            print('ObjSonNum')
            assert  False

        if not bop_a.ObjSup == bop_b.ObjSup:
            print('ObjSup')
            assert  False

        return True
    except Exception as e:
        raise e

def getBopTypeName(cur_bop):
    try:
        assert  cur_bop is not None
        return u'坦克' if cur_bop.A1 == 1 else u'战车' if cur_bop.ObjType == 2 else u'步兵'
    except Exception as e:
        return 'OTHER'
    
if __name__ == '__main__':
    pass
