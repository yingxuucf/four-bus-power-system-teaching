"""第1讲：从系统全貌识别后续计算问题。"""

from four_bus_system.data import CONFIG
from four_bus_system.network import network_topology
from ._common import heading


def main() -> None:
    heading(1, "电力系统及其基本运行问题")
    print(f"统一基准：{CONFIG['base']['s_mva']:.0f} MVA，{CONFIG['base']['frequency_hz']:.0f} Hz")
    print("母体系统：")
    for device, start, end in network_topology():
        print(f"  {start} --{device}-- {end}")
    print("课程问题链：元件建模 → 潮流与调控 → 故障 → 稳定")


if __name__ == "__main__":
    main()
