"""四母线系统的统一网络对象、支路装配和序网络基础函数。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .data import CONFIG, bus_index


S_BASE_MVA = float(CONFIG["base"]["s_mva"])
FREQUENCY_HZ = float(CONFIG["base"]["frequency_hz"])
BUS_IDS = tuple(item["id"] for item in CONFIG["buses"])
BUS_NAMES = tuple(f"{item['id']} {item['name']}" for item in CONFIG["buses"])
V_BASE_KV = tuple(float(CONFIG["base"]["voltage_kv"][bus]) for bus in BUS_IDS)


@dataclass(frozen=True)
class Branch:
    name: str
    from_bus: int
    to_bus: int
    r_pu: float
    x_pu: float
    b_pu: float = 0.0
    rating_mva: float | None = None
    tap: complex = 1.0 + 0.0j

    @property
    def series_impedance(self) -> complex:
        return complex(self.r_pu, self.x_pu)

    @property
    def series_admittance(self) -> complex:
        return 1.0 / self.series_impedance


def make_branches(
    line_count: int = 2,
    include_line_shunt: bool = True,
    sequence: int = 1,
    t2_tap: float = 1.0,
) -> list[Branch]:
    """由统一数据文件建立正序/负序支路表。

    零序网络的变压器接线必须单独处理，见 :mod:`four_bus_system.fault`。
    """
    if line_count not in (1, 2):
        raise ValueError("line_count 只能取 1 或 2")
    if sequence not in (1, 2):
        raise ValueError("通用支路表只支持正序或负序")

    result: list[Branch] = []
    for record in CONFIG["branches"]:
        if record["id"] == "L2" and line_count == 1:
            continue
        suffix = str(sequence)
        b_pu = float(record.get("b1", 0.0)) if include_line_shunt and sequence == 1 else 0.0
        tap = complex(t2_tap) if record["id"] == "T2" else 1.0 + 0.0j
        result.append(
            Branch(
                name=record["id"],
                from_bus=bus_index(record["from"]),
                to_bus=bus_index(record["to"]),
                r_pu=float(record[f"r{suffix}"]),
                x_pu=float(record[f"x{suffix}"]),
                b_pu=b_pu,
                rating_mva=float(record["rating_mva"]),
                tap=tap,
            )
        )
    return result


def branch_admittance_terms(branch: Branch) -> tuple[complex, complex, complex, complex]:
    """返回支路对 Ybus 的四个元素 Yff、Yft、Ytf、Ytt。"""
    y = branch.series_admittance
    y_shunt = 1j * branch.b_pu / 2.0
    tap = branch.tap
    if abs(tap) == 0.0:
        raise ValueError(f"{branch.name} 的非标准变比不能为零")
    yff = (y + y_shunt) / (abs(tap) ** 2)
    yft = -y / np.conj(tap)
    ytf = -y / tap
    ytt = y + y_shunt
    return yff, yft, ytf, ytt


def build_ybus(branches: Iterable[Branch], bus_count: int = 4) -> np.ndarray:
    """按 π 型线路和非标准变比装配复数节点导纳矩阵。"""
    ybus = np.zeros((bus_count, bus_count), dtype=complex)
    for branch in branches:
        i, j = branch.from_bus, branch.to_bus
        yff, yft, ytf, ytt = branch_admittance_terms(branch)
        ybus[i, i] += yff
        ybus[i, j] += yft
        ybus[j, i] += ytf
        ybus[j, j] += ytt
    return ybus


def add_ground_impedance(ybus: np.ndarray, bus: int, impedance: complex) -> None:
    """把电压源置零后的内阻抗作为节点对地支路加入矩阵。"""
    if abs(impedance) == 0.0:
        raise ValueError("对地阻抗不能为零；理想接地应单独消元")
    ybus[bus, bus] += 1.0 / impedance


def driving_point_impedance(ybus: np.ndarray, bus: int) -> complex:
    return complex(np.linalg.inv(ybus)[bus, bus])


def network_topology() -> tuple[tuple[str, str, str], ...]:
    return tuple((item["id"], item["from"], item["to"]) for item in CONFIG["branches"])
