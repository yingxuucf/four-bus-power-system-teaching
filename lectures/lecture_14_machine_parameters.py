"""第14讲：同步机各时间尺度参数和等值模型。"""

from four_bus_system.data import CONFIG
from four_bus_system.machine import short_circuit_current_levels
from ._common import heading


def main() -> None:
    heading(14, "同步发电机短路过程各时间态参数与模型")
    g = CONFIG["generators"]["G1"]
    print(f"Xd={g['xd']:.2f}，Xd'={g['xdp']:.2f}，Xd''={g['xdpp']:.2f} p.u.")
    print(f"Tdo'={g['tdop_s']:.2f} s，Tdo''={g['tdopp_s']:.3f} s，Tqo''={g['tqopp_s']:.3f} s")
    levels = short_circuit_current_levels(source_voltage_pu=1.04, external_x_pu=0.10)
    print("以G1经T1短路的简化电抗印象：")
    print(f"  次暂态 {levels.subtransient_rms_pu:.3f}，暂态 {levels.transient_rms_pu:.3f}，稳态 {levels.steady_rms_pu:.3f} p.u.")


if __name__ == "__main__":
    main()
