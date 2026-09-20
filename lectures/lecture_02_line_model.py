"""第2讲：线路有名值、标幺值与 π 型模型。"""

from four_bus_system.per_unit import line_parameters
from ._common import heading


def main() -> None:
    heading(2, "输电线路参数与等值电路")
    p = line_parameters("L1")
    print(f"L1长度={p['length_km']:.0f} km")
    print(f"R={p['r_ohm']:.2f} Ω，X={p['x_ohm']:.2f} Ω，B={p['b_siemens'] * 1e6:.2f} μS")
    print(f"每回标幺值：z={p['r_pu']:.3f}+j{p['x_pu']:.3f}，b={p['b_pu']:.3f}")
    print(f"双回串联等值：z={p['r_pu']/2:.4f}+j{p['x_pu']/2:.4f} p.u.")


if __name__ == "__main__":
    main()
