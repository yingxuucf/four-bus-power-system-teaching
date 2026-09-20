"""第18讲：序网络连接与不对称故障。"""

from four_bus_system.fault import (
    sequence_driving_point_impedance,
    solve_b4_line_to_line_fault,
    solve_b4_single_line_ground_fault,
)
from ._common import heading, phasor


def main() -> None:
    heading(18, "序网络与不对称故障分析")
    for sequence in (1, 2, 0):
        z = sequence_driving_point_impedance("B4", sequence)
        print(f"B4 Z{sequence}={z.real:.5f}+j{z.imag:.5f} p.u.")
    slg = solve_b4_single_line_ground_fault()
    ll = solve_b4_line_to_line_fault()
    print(f"B4单相接地：Ia={phasor(slg.phase_current_pu[0])} p.u.，Ib/Ic≈0")
    print(f"B4两相短路：|Ia|={abs(ll.phase_current_pu[0]):.3e}，|Ib|=|Ic|={abs(ll.phase_current_pu[1]):.4f} p.u.")


if __name__ == "__main__":
    main()
