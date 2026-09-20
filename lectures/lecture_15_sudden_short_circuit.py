"""第15讲：突然三相短路的周期、非周期和二倍频分量。"""

import numpy as np
from four_bus_system.machine import periodic_current_envelope, stator_free_current_components
from ._common import heading


def main() -> None:
    heading(15, "同步发电机突然三相短路电流分量分析")
    times = np.array([0.0, 0.04, 0.20, 1.0, 6.0])
    envelope = periodic_current_envelope(times, external_x_pu=0.10)
    for time, current in zip(times, envelope):
        print(f"t={time:>4.2f} s：基频周期分量有效值包络={current:.4f} p.u.")
    dc, double, total = stator_free_current_components(times, np.deg2rad(30.0), ta_s=0.20)
    print(f"xd''=xq''时二倍频最大值={np.max(np.abs(double)):.3e} p.u.")
    _, salient_double, _ = stator_free_current_components(times, np.deg2rad(30.0), ta_s=0.20, xqpp=0.30)
    print(f"若xd''≠xq''，二倍频样值最大值={np.max(np.abs(salient_double)):.4f} p.u.")
    print(f"非周期自由分量初值={float(np.asarray(dc)[0]):.4f} p.u.，总自由分量初值={float(np.asarray(total)[0]):.4f} p.u.")


if __name__ == "__main__":
    main()
