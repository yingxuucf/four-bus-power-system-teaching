"""第6讲：径向网前推回代与 N-1 对比。"""

from four_bus_system.steady_state import radial_backward_forward
from ._common import heading


def main() -> None:
    heading(6, "简单电力系统潮流计算")
    for lines in (2, 1):
        result = radial_backward_forward(line_count=lines)
        print(f"线路回数={lines}：收敛={result.converged}，|U4|={abs(result.voltage[3]):.4f} p.u.，ΔP={result.loss_pu.real*100:.3f} MW")
    print("本讲忽略线路并联电纳；第7—9讲在 Ybus/NR 模型中恢复。")


if __name__ == "__main__":
    main()
