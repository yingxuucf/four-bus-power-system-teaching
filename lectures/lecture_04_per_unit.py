"""第4讲：多电压等级统一标幺制。"""

from four_bus_system.per_unit import base_quantities, change_impedance_base
from ._common import heading


def main() -> None:
    heading(4, "电力系统标幺制")
    for voltage in (10.5, 220.0):
        base = base_quantities(voltage)
        print(f"{voltage:g} kV区：Ib={base.current_ka:.5f} kA，Zb={base.impedance_ohm:.3f} Ω，Yb={base.admittance_siemens:.6f} S")
    converted = change_impedance_base(0.10j, 100.0, 10.5, 50.0, 10.5)
    print(f"0.10 p.u.(100 MVA)换到50 MVA同电压基准：{converted.imag:.3f} p.u.")


if __name__ == "__main__":
    main()
