"""前置课程使用的支路压降、损耗与径向网前推回代。"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .network import S_BASE_MVA


@dataclass(frozen=True)
class RadialResult:
    converged: bool
    iterations: int
    voltage: np.ndarray
    current_pu: complex
    source_power_pu: complex
    loss_pu: complex


def branch_drop_and_loss(
    receiving_voltage_pu: complex, load_mva: complex, impedance_pu: complex
) -> tuple[complex, complex, complex]:
    load_pu = load_mva / S_BASE_MVA
    current = np.conj(load_pu / receiving_voltage_pu)
    sending_voltage = receiving_voltage_pu + impedance_pu * current
    loss = abs(current) ** 2 * impedance_pu
    return sending_voltage, current, loss


def radial_backward_forward(
    load_mva: complex = 60.0 + 25.0j,
    line_count: int = 2,
    source_voltage_pu: complex = 1.04 + 0.0j,
    tolerance: float = 1e-10,
    max_iterations: int = 100,
) -> RadialResult:
    """忽略并联电纳，对 B1—B4 径向网进行恒 PQ 前推回代。"""
    if line_count not in (1, 2):
        raise ValueError("line_count 只能取 1 或 2")
    impedances = np.array(
        [0.005 + 0.10j, (0.015 + 0.12j) / line_count, 0.005 + 0.12j],
        dtype=complex,
    )
    load_pu = load_mva / S_BASE_MVA
    voltage = np.ones(4, dtype=complex)
    voltage[0] = source_voltage_pu
    current = 0.0j
    converged = False
    for iteration in range(1, max_iterations + 1):
        old = voltage.copy()
        current = np.conj(load_pu / voltage[3])
        for index, impedance in enumerate(impedances, start=1):
            voltage[index] = voltage[index - 1] - impedance * current
        if np.max(np.abs(voltage - old)) < tolerance:
            converged = True
            break
    loss = abs(current) ** 2 * impedances.sum()
    source_power = load_pu + loss
    return RadialResult(converged, iteration, voltage, current, source_power, loss)
