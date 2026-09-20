"""第20讲：等面积定则和全课程综合证据链。"""

import numpy as np
from four_bus_system.integrated import course_summary
from ._common import heading


def main() -> None:
    heading(20, "暂态稳定与综合案例")
    result = course_summary()
    for code, power_flow in result["power_flow"].items():
        print(f"{code}: |U4|={abs(power_flow.voltage[3]):.4f} p.u.，网损={power_flow.total_loss_mw():.3f} MW")
    print(f"H1恢复到0.95 p.u.所需补偿={result['required_compensation_mvar']:.2f} Mvar")
    print(f"F1频差={result['frequency'].delta_frequency_hz:.5f} Hz")
    print(f"B2三相短路 |I''|={abs(result['b2_three_phase_fault'].current_pu):.3f} p.u.")
    print(f"B4单相接地 |Ia|={abs(result['b4_slg_fault'].phase_current_pu[0]):.4f} p.u.")
    stability = result["stability"]
    print(f"临界切除角={np.degrees(stability.delta_critical_rad):.3f}°，临界切除时间={stability.critical_time_s:.4f} s")
    for time in (0.20, 0.32):
        print(f"切除时间 {time:.2f} s：{'稳定' if time < stability.critical_time_s else '失稳'}（等面积判据）")


if __name__ == "__main__":
    main()
