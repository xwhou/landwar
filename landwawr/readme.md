# demoAI启动方式
```bash
cd bin
python train_rule.py
```
# randomAI启动方式
```bash
cd bin
python train_random.py
```

#参数
```python
# bin/train.py main函数中
scenario = {
    1531: "城镇居民地连级想定",
    3531: "城镇居民地营级想定",
    1631: "岛上台地连级想定",
    3631: "岛上台地营级想定",
    1231: "高原通道连级想定",
    3231: "高原通道营级想定",

}
match_id = "str"  # 指定回放文件名或回放数据库中表名称

# engine/wgconst/const.py
class ClockParas:
    MaxTime = 600    # 最大时长s
    SpeedUpRatio = 30    # 加速比
    FPS = 2   # 每s更新步长数


class BasicSpeed:  # 算子的基础机动速度
    People = 5
    Car = 36
    Plane = 100

```
