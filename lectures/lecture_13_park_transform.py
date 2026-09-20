"""第13讲：abc 与 dq0 的角度关系和 Park 变换。"""

import numpy as np
from four_bus_system.machine import inverse_park_transform, park_transform
from ._common import heading


def main() -> None:
    heading(13, "同步发电机模型与 Park 变换")
    theta = np.deg2rad(25.0)
    abc = np.array([1.0, -0.5, -0.5])
    dq0 = park_transform(abc, theta)
    restored = inverse_park_transform(dq0, theta)
    print(f"转子d轴相对a轴电角度 θ=25°")
    print(f"abc={np.round(abc,6)} → dq0={np.round(dq0,6)}")
    print(f"逆变换误差={np.max(np.abs(restored-abc)):.3e}")
    print("同步正序基频量在随转子同步旋转的 dq 轴上表现为直流量。")


if __name__ == "__main__":
    main()
