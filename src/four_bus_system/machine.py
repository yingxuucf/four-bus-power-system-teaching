"""Park 变换与同步发电机突然三相短路的教学模型。"""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

from .data import CONFIG
from .network import FREQUENCY_HZ


def park_matrix(theta_rad: float) -> np.ndarray:
    angles = theta_rad + np.array([0.0, -2.0 * np.pi / 3.0, 2.0 * np.pi / 3.0])
    return (2.0 / 3.0) * np.array(
        [np.cos(angles), -np.sin(angles), np.full(3, 0.5)], dtype=float
    )


def park_transform(abc: np.ndarray | list[float], theta_rad: float) -> np.ndarray:
    """幅值不变 Park 变换，返回 [d,q,0]。"""
    return park_matrix(theta_rad) @ np.asarray(abc, dtype=float)


def inverse_park_transform(dq0: np.ndarray | list[float], theta_rad: float) -> np.ndarray:
    return np.linalg.solve(park_matrix(theta_rad), np.asarray(dq0, dtype=float))


@dataclass(frozen=True)
class CurrentLevels:
    subtransient_rms_pu: float
    transient_rms_pu: float
    steady_rms_pu: float


def short_circuit_current_levels(source_voltage_pu: float = 1.04, external_x_pu: float = 0.0) -> CurrentLevels:
    g1 = CONFIG["generators"]["G1"]
    return CurrentLevels(
        subtransient_rms_pu=source_voltage_pu / (float(g1["xdpp"]) + external_x_pu),
        transient_rms_pu=source_voltage_pu / (float(g1["xdp"]) + external_x_pu),
        steady_rms_pu=source_voltage_pu / (float(g1["xd"]) + external_x_pu),
    )


def periodic_current_envelope(
    time_s: np.ndarray | float,
    source_voltage_pu: float = 1.04,
    external_x_pu: float = 0.0,
) -> np.ndarray:
    """用于课堂识别三个阶段的简化有效值包络。

    衰减常数采用工作簿给出的开路时间常数，仅用于定性演示；精确全过程应使用
    运行时间常数或完整 Park 微分方程。
    """
    time = np.asarray(time_s, dtype=float)
    g1 = CONFIG["generators"]["G1"]
    level = short_circuit_current_levels(source_voltage_pu, external_x_pu)
    return (
        level.steady_rms_pu
        + (level.transient_rms_pu - level.steady_rms_pu) * np.exp(-time / float(g1["tdop_s"]))
        + (level.subtransient_rms_pu - level.transient_rms_pu) * np.exp(-time / float(g1["tdopp_s"]))
    )


def stator_free_current_components(
    time_s: np.ndarray | float,
    theta0_rad: float,
    psi0_pu: float = 1.0,
    ta_s: float = 0.20,
    xdpp: float | None = None,
    xqpp: float | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """定子静止自由磁链逆 Park 后的非周期项、二倍频项及总和。"""
    g1 = CONFIG["generators"]["G1"]
    xdpp = float(g1["xdpp"] if xdpp is None else xdpp)
    xqpp = float(g1["xqpp"] if xqpp is None else xqpp)
    time = np.asarray(time_s, dtype=float)
    decay = np.exp(-time / ta_s)
    omega = 2.0 * math.pi * FREQUENCY_HZ
    nonperiodic = -0.5 * psi0_pu * decay * (1.0 / xdpp + 1.0 / xqpp) * math.cos(theta0_rad)
    double_frequency = (
        -0.5
        * psi0_pu
        * decay
        * (1.0 / xdpp - 1.0 / xqpp)
        * np.cos(2.0 * omega * time + theta0_rad)
    )
    return nonperiodic, double_frequency, nonperiodic + double_frequency
