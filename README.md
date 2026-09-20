# 电力系统分析：四母线贯穿教学工程

本工程用同一套四母线系统贯通20讲本科《电力系统分析》课程。它不是20个互不相关的小算例：线路、变压器、负荷、发电机、母线编号、基准值和运行场景只定义一次，各讲在同一模型上逐步增加新的分析能力。

课程主线：

1. 第1—4讲：系统、线路、变压器、负荷与标幺制；
2. 第5—11讲：电压降落、简单潮流、Ybus、NR潮流、频率与电压控制；
3. 第12—18讲：三相短路、同步机/Park模型、短路电流分量、实用短路计算、对称分量与不对称故障；
4. 第19—20讲：稳定性基本概念、等面积定则与综合案例。

## 工程结构

```text
four-bus-power-system-teaching/
├─ src/four_bus_system/
│  ├─ data/four_bus_system.json  # 全课程唯一参数源
│  ├─ network.py                 # 支路对象、Ybus及网络装配
│  ├─ per_unit.py                # 基准量与标幺换算
│  ├─ steady_state.py            # 压降、损耗、前推回代
│  ├─ power_flow.py              # 极坐标NR潮流
│  ├─ control.py                 # 一次调频与电压控制
│  ├─ machine.py                 # Park变换与同步机短路过程
│  ├─ fault.py                   # 三相/不对称故障与序网络
│  ├─ stability.py               # 功角、运动方程、等面积定则
│  └─ integrated.py              # 全课程综合指标
├─ lectures/                     # 第1—20讲独立课堂入口
├─ examples/                     # 潮流与三相短路示例
├─ tests/                        # 参数、算法和20讲烟雾测试
├─ references/                   # 正式参数工作簿
├─ COURSE_MAP.md                 # 讲次—模型—程序映射
└─ run_all.py                    # 一次运行全部20讲
```

## 安装

要求 Python 3.10 及以上版本。

```bash
python -m venv .venv
python -m pip install -e .
```

Windows PowerShell 激活虚拟环境：

```powershell
.venv\Scripts\Activate.ps1
```

## 运行

运行20讲全部演示程序：

```bash
python run_all.py
```

单独运行一讲：

```bash
python -m lectures.lecture_09_newton_power_flow
python -m lectures.lecture_16_practical_fault
python -m lectures.lecture_20_integrated_case
```

运行公共计算模块：

```bash
python -m four_bus_system.power_flow --all
python -m four_bus_system.fault
```

运行回归测试：

```bash
python -m unittest discover -s tests -v
```

## 统一建模口径

- 全系统统一基准为100 MVA、50 Hz；
- 稳态采用三相对称一相等值，线路采用中长线π型模型；
- 功率以“注入母线为正”；B1为平衡节点，PF1工况下B3为PV节点；
- 第12讲单电源算例不引入G2；第16讲复杂网络算例引入B3外部等值电源；
- 三相短路使用完整复数矩阵；不对称故障按变压器接线形成正、负、零序网络；
- 稳定计算采用经典恒定 `E'` 模型，忽略调速、励磁和阻尼；
- 参数来自 `references/贯穿案例_四母线系统完整参数体系.xlsx`，字段映射见 `PARAMETER_PROVENANCE.md`。

程序和参数仅用于课堂教学，不用于设备选择、保护整定或电网运行决策。
