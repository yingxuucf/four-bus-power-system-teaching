"""第12讲：单电源三相短路初始电流与冲击电流。"""

from four_bus_system.fault import (
    aperiodic_time_constant,
    peak_factor_iec,
    peak_short_circuit_current,
    solve_b2_single_source_fault,
)
from ._common import heading, phasor


def main() -> None:
    heading(12, "三相短路的故障机理与初始电流计算")
    result = solve_b2_single_source_fault()
    z = result.z_thevenin_engineering_pu
    kappa = peak_factor_iec(z.real, z.imag)
    peak_ka = peak_short_circuit_current(result.current_ka, kappa)
    print(f"故障前 U_B2={phasor(result.prefault_voltage[1], 5)} p.u.")
    print(f"仅G1供电：ZΣ={z.real:.3f}+j{z.imag:.3f} p.u.")
    print(f"I''={phasor(result.current_pu)} p.u.={result.current_ka:.3f} kA")
    print(f"Ta={aperiodic_time_constant(z.real,z.imag):.4f} s，κ={kappa:.4f}，冲击电流={peak_ka:.3f} kA")


if __name__ == "__main__":
    main()
