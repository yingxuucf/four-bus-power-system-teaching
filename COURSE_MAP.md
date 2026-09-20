# 20讲程序映射

| 讲次 | 教学主题 | 程序入口 | 复用/新增模型 |
|---:|---|---|---|
| 1 | 电力系统及其基本运行问题 | `lectures.lecture_01_overview` | 四母线拓扑、课程问题链 |
| 2 | 输电线路参数与等值电路 | `lectures.lecture_02_line_model` | L1/L2有名值与π型参数 |
| 3 | 变压器参数与负荷模型 | `lectures.lecture_03_transformer_load` | 短路试验、恒PQ负荷 |
| 4 | 电力系统标幺制 | `lectures.lecture_04_per_unit` | 基准量、换基准 |
| 5 | 电压降落与功率损耗 | `lectures.lecture_05_voltage_drop` | 复功率、电流、压降、损耗 |
| 6 | 简单电力系统潮流 | `lectures.lecture_06_simple_power_flow` | 径向网前推回代、N-1 |
| 7 | 节点导纳矩阵与网络建模 | `lectures.lecture_07_ybus` | 复数Ybus、稀疏结构 |
| 8 | 节点分类与潮流方程 | `lectures.lecture_08_bus_types` | Slack/PV/PQ |
| 9 | 计算机潮流程序与校核 | `lectures.lecture_09_newton_power_flow` | NR潮流、四种场景 |
| 10 | 有功平衡与频率调整 | `lectures.lecture_10_frequency_control` | 一次调频、功率分担 |
| 11 | 无功平衡与电压控制 | `lectures.lecture_11_voltage_control` | 补偿、分接头调压 |
| 12 | 三相短路初始电流 | `lectures.lecture_12_initial_short_circuit` | 仅G1、冲击系数、非周期时间常数 |
| 13 | 同步发电机模型与Park变换 | `lectures.lecture_13_park_transform` | abc↔dq0 |
| 14 | 同步机各时间态参数与模型 | `lectures.lecture_14_machine_parameters` | Xd/Xd′/Xd″及时间常数 |
| 15 | 同步机突然三相短路电流分量 | `lectures.lecture_15_sudden_short_circuit` | 周期包络、非周期与二倍频 |
| 16 | 三相短路实用计算与程序设计 | `lectures.lecture_16_practical_fault` | PF1预故障潮流、复数Zbus |
| 17 | 对称分量法 | `lectures.lecture_17_symmetrical_components` | 相量分解与重构 |
| 18 | 序网络与不对称故障 | `lectures.lecture_18_unbalanced_fault` | 正负零序、单相接地与两相短路 |
| 19 | 稳定性基本概念 | `lectures.lecture_19_stability_fundamentals` | 功角特性、转子运动 |
| 20 | 暂态稳定与综合案例 | `lectures.lecture_20_integrated_case` | 等面积定则、全课程证据链 |

每个入口均可独立运行；`run_all.py` 用于一次验证全部讲次。
