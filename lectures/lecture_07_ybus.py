"""第7讲：由支路表形成复数 Ybus。"""

from four_bus_system.network import build_ybus, make_branches
from ._common import heading


def main() -> None:
    heading(7, "节点导纳矩阵与网络建模")
    ybus = build_ybus(make_branches(2, True))
    print("Ybus / p.u.")
    for row in ybus:
        print("  " + "  ".join(f"{x.real:+.4f}{x.imag:+.4f}j" for x in row))
    print(f"非零元素={int((abs(ybus)>1e-12).sum())}/{ybus.size}，矩阵对称={bool(abs(ybus-ybus.T).max()<1e-12)}")


if __name__ == "__main__":
    main()
