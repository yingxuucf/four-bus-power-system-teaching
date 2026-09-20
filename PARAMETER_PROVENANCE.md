# 参数来源与字段映射

唯一正式来源为 `references/贯穿案例_四母线系统完整参数体系.xlsx`。程序使用的固化数据位于 `src/four_bus_system/data/four_bus_system.json`。

| JSON区域 | 工作簿来源 | 主要内容 |
|---|---|---|
| `base`、`buses` | `01_基准与母线` | 100 MVA、50 Hz、母线电压与类型 |
| `branches` | `02_设备铭牌`、`03_标幺与序参数` | T1、L1、L2、T2正负零序参数 |
| `generators` | `02_设备铭牌`、`03_标幺与序参数` | G1动态参数与G2等值参数 |
| `loads` | `02_设备铭牌`、`04_运行与故障场景` | 正常/重载PQ与频率特性 |
| `frequency_control` | `06_频率短路与稳定` | 调差率、额定功率、负荷阶跃 |
| `stability` | `06_频率短路与稳定` | Pm、E′、Xpre、Xpost、切除时间 |
| `scenarios` | `04_运行与故障场景` | N0、N1、H1、PF1、F1、SC1、UF1、ST1 |
| `reference_*` | `05_潮流校验结果`、`06_频率短路与稳定` | 回归测试基准 |

更新流程：先修改正式工作簿，再同步JSON；最后运行 `python -m unittest discover -s tests -v` 和 `python run_all.py`。不得为了匹配旧答案直接修改回归结果。
