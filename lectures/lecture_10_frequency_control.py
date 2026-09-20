"""第10讲：一次调频和功率分担。"""

from four_bus_system.control import primary_frequency_response
from ._common import heading


def main() -> None:
    heading(10, "有功平衡与频率调整")
    result = primary_frequency_response()
    print(f"负荷阶跃：+{result.delta_load_mw:.1f} MW，稳态频差：{result.delta_frequency_hz:.5f} Hz")
    for name, response in result.responses_mw.items():
        print(f"  {name}: ΔP={response:.4f} MW，K={result.unit_regulation_mw_per_hz[name]:.3f} MW/Hz")
    print(f"功率平衡校核：ΣΔP={result.balance_mw:.6f} MW")


if __name__ == "__main__":
    main()
