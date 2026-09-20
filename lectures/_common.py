from __future__ import annotations

import numpy as np


def heading(number: int, title: str) -> None:
    print(f"\n{'=' * 72}\n第{number:02d}讲  {title}\n{'=' * 72}")


def phasor(value: complex, digits: int = 4) -> str:
    return f"{abs(value):.{digits}f} ∠ {np.degrees(np.angle(value)):.2f}°"
