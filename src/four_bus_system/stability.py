"""功角特性、等面积定则和经典二阶转子运动方程。"""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

from .data import CONFIG
from .network import FREQUENCY_HZ


@dataclass(frozen=True)
class StabilitySummary:
    pmax_pre_pu: float
    pmax_post_pu: float
    delta0_rad: float
    delta_unstable_post_rad: float
    delta_critical_rad: float
    critical_time_s: float


def electrical_power(delta_rad: np.ndarray | float, transfer_x_pu: float) -> np.ndarray:
    data = CONFIG["stability"]
    coefficient = float(data["eprime_pu"]) * float(data["infinite_bus_voltage_pu"]) / transfer_x_pu
    return coefficient * np.sin(np.asarray(delta_rad, dtype=float))


def stability_summary() -> StabilitySummary:
    data = CONFIG["stability"]
    pm = float(data["pm_pu"])
    e = float(data["eprime_pu"])
    u = float(data["infinite_bus_voltage_pu"])
    xpre = float(data["x_pre_pu"])
    xpost = float(data["x_post_pu"])
    pmax_pre = e * u / xpre
    pmax_post = e * u / xpost
    delta0 = math.asin(pm / pmax_pre)
    delta_u = math.pi - math.asin(pm / pmax_post)
    argument = math.cos(delta_u) + (pm / pmax_post) * (delta_u - delta0)
    delta_c = math.acos(max(-1.0, min(1.0, argument)))
    h = float(CONFIG["generators"]["G1"]["h_s"])
    omega_s = 2.0 * math.pi * FREQUENCY_HZ
    critical_time = math.sqrt(4.0 * h * (delta_c - delta0) / (omega_s * pm))
    return StabilitySummary(pmax_pre, pmax_post, delta0, delta_u, delta_c, critical_time)


def equal_area_components() -> dict[str, float]:
    summary = stability_summary()
    data = CONFIG["stability"]
    pm = float(data["pm_pu"])
    accelerating = pm * (summary.delta_critical_rad - summary.delta0_rad)
    decelerating = (
        summary.pmax_post_pu
        * (math.cos(summary.delta_critical_rad) - math.cos(summary.delta_unstable_post_rad))
        - pm * (summary.delta_unstable_post_rad - summary.delta_critical_rad)
    )
    return {"accelerating": accelerating, "decelerating": decelerating}


def simulate_swing(
    clearing_time_s: float,
    end_time_s: float = 2.0,
    step_s: float = 0.001,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """用 RK4 积分经典模型；故障中 Pmax=0，切除后永久退出一回线。"""
    data = CONFIG["stability"]
    summary = stability_summary()
    pm = float(data["pm_pu"])
    h = float(CONFIG["generators"]["G1"]["h_s"])
    omega_s = 2.0 * math.pi * FREQUENCY_HZ
    damping = float(CONFIG["generators"]["G1"]["d_pu"])
    times = np.arange(0.0, end_time_s + step_s / 2.0, step_s)
    delta = np.empty_like(times)
    speed = np.empty_like(times)
    delta[0] = summary.delta0_rad
    speed[0] = 0.0

    def derivative(t: float, state: np.ndarray) -> np.ndarray:
        angle, deviation = state
        pmax = float(data["pmax_fault_pu"]) if t < clearing_time_s else summary.pmax_post_pu
        pe = pmax * math.sin(angle)
        return np.array([deviation, omega_s * (pm - pe - damping * deviation) / (2.0 * h)])

    for index in range(len(times) - 1):
        t = float(times[index])
        state = np.array([delta[index], speed[index]])
        k1 = derivative(t, state)
        k2 = derivative(t + step_s / 2.0, state + step_s * k1 / 2.0)
        k3 = derivative(t + step_s / 2.0, state + step_s * k2 / 2.0)
        k4 = derivative(t + step_s, state + step_s * k3)
        next_state = state + step_s * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
        delta[index + 1], speed[index + 1] = next_state
    return times, delta, speed


def is_first_swing_stable(clearing_time_s: float) -> bool:
    _, delta, _ = simulate_swing(clearing_time_s)
    return bool(np.max(delta) < math.pi)
