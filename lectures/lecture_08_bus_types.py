"""第8讲：控制方式决定 Slack、PV、PQ 节点。"""

from four_bus_system.data import CONFIG
from ._common import heading


def main() -> None:
    heading(8, "节点分类与潮流方程")
    known = {"Slack": "已知 |U|、δ；求 P、Q", "PV": "已知 P、|U|；求 Q、δ", "PQ": "已知 P、Q；求 |U|、δ"}
    for bus in CONFIG["buses"]:
        kind = bus["normal_type"]
        print(f"{bus['id']} {bus['name']}: {kind}；{known[kind]}")
    print("PF1 中 B3 由外部等值系统控制电压，因此作为 PV 节点。")


if __name__ == "__main__":
    main()
