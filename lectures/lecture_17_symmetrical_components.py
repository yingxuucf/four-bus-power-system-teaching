"""第17讲：三相量与正、负、零序分量互换。"""

import numpy as np
from four_bus_system.fault import phase_to_sequence, sequence_to_phase
from ._common import heading, phasor


def main() -> None:
    heading(17, "对称分量法")
    phase = np.array([1.0 + 0.0j, -0.35 - 0.75j, -0.25 + 0.55j])
    sequence = phase_to_sequence(phase)
    names = ("零序", "正序", "负序")
    for name, value in zip(names, sequence):
        print(f"{name}: {phasor(value)}")
    restored = sequence_to_phase(sequence)
    print(f"分解—重构最大误差={np.max(np.abs(restored-phase)):.3e}")


if __name__ == "__main__":
    main()
