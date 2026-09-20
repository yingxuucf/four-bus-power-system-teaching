"""第11讲：重载低电压、无功补偿和分接头调压。"""

from four_bus_system.control import compensation_for_target_voltage, voltage_control_case
from ._common import heading


def main() -> None:
    heading(11, "无功平衡与电压控制")
    base = voltage_control_case("H1")
    compensation, compensated = compensation_for_target_voltage(0.95, "H1")
    print(f"H1未调节：|U4|={abs(base.voltage[3]):.4f} p.u.")
    print(f"达到0.95 p.u.所需并联补偿约 {compensation:.2f} Mvar；校核 |U4|={abs(compensated.voltage[3]):.4f}")
    for tap in (0.975, 1.0, 1.025):
        result = voltage_control_case("H1", 0.0, tap)
        print(f"T2非标准变比={tap:.3f}：|U4|={abs(result.voltage[3]):.4f} p.u.")


if __name__ == "__main__":
    main()
