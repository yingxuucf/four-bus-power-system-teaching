"""第5讲：局部支路的电压降落和功率损耗。"""

from four_bus_system.steady_state import branch_drop_and_loss
from ._common import heading, phasor


def main() -> None:
    heading(5, "线路电压降落与功率损耗")
    sending, current, loss = branch_drop_and_loss(0.95 + 0j, 60 + 25j, 0.005 + 0.12j)
    print(f"受端电压 Ur=0.95∠0° p.u.，负荷=60+j25 MVA")
    print(f"支路电流 I={phasor(current)} p.u.")
    print(f"送端电压 Us={phasor(sending)} p.u.")
    print(f"支路损耗 ΔS={loss.real*100:.3f}+j{loss.imag*100:.3f} MVA")


if __name__ == "__main__":
    main()
