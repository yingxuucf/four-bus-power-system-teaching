"""第16讲：完整复数 Ybus/Zbus 的三相短路实用计算。"""

import numpy as np
from four_bus_system.fault import format_complex, solve_b2_three_phase_fault
from ._common import heading, phasor


def main() -> None:
    heading(16, "电力系统三相短路电流实用计算与程序设计")
    result = solve_b2_three_phase_fault()
    print("故障前 PF1 电压：")
    for number, voltage in enumerate(result.prefault_voltage, start=1):
        print(f"  B{number}: {phasor(voltage,5)} p.u.")
    print("故障分量网络 Zbus / p.u.")
    for row in result.zbus:
        print("  " + "  ".join(format_complex(complex(x)) for x in row))
    print(f"Z22={format_complex(result.z_thevenin_engineering_pu)}，I''={format_complex(result.current_pu,4)} p.u.")
    print(f"|I''|={abs(result.current_pu):.3f} p.u.={result.current_ka:.3f} kA，S''={result.short_circuit_mva:.1f} MVA")
    print(f"故障点电压校核：|Uf|={abs(result.postfault_voltage[1]):.3e} p.u.")


if __name__ == "__main__":
    main()
