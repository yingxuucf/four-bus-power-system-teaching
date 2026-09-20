"""第3讲：变压器短路试验参数与恒 PQ 负荷。"""

from four_bus_system.data import CONFIG
from four_bus_system.per_unit import transformer_from_short_circuit_test
from ._common import heading


def main() -> None:
    heading(3, "变压器参数与负荷模型")
    for name, uk in (("T1", 10.01), ("T2", 12.01)):
        z = transformer_from_short_circuit_test(100.0, uk, 500.0)
        print(f"{name}: z={z.real:.5f}+j{z.imag:.5f} p.u.")
    for name in ("normal", "heavy"):
        load = CONFIG["loads"][name]
        current = complex(load["p_mw"], -load["q_mvar"]) / CONFIG["base"]["s_mva"]
        print(f"{name}: S={load['p_mw']:.0f}+j{load['q_mvar']:.0f} MVA，U=1 p.u.时 |I|={abs(current):.3f} p.u.")


if __name__ == "__main__":
    main()
