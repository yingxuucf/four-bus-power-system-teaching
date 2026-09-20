"""第19讲：稳定性基本概念、功角特性和转子运动。"""

import numpy as np
from four_bus_system.stability import electrical_power, stability_summary
from ._common import heading


def main() -> None:
    heading(19, "电力系统稳定性基本概念")
    result = stability_summary()
    print(f"故障前 Pmax={result.pmax_pre_pu:.4f} p.u.，故障后 Pmax={result.pmax_post_pu:.4f} p.u.")
    print(f"初始功角 δ0={np.degrees(result.delta0_rad):.3f}°")
    for angle in (20.0, 40.0, 60.0, 90.0):
        power = float(electrical_power(np.deg2rad(angle), 0.61))
        print(f"δ={angle:>4.0f}°：Pe={power:.4f} p.u.")
    print("运动方程把 Pm-Pe 转化为转子加速度；稳定问题是功角能否保持有界。")


if __name__ == "__main__":
    main()
