"""第9讲：极坐标牛顿—拉夫逊潮流与结果校核。"""

from four_bus_system.power_flow import print_result, solve_power_flow
from ._common import heading


def main() -> None:
    heading(9, "计算机潮流程序与结果校核")
    for code in ("N0", "N1", "H1", "PF1"):
        print_result(solve_power_flow(code))


if __name__ == "__main__":
    main()
