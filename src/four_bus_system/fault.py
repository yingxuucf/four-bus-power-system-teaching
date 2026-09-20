"""三相短路、对称分量、序网络和不对称故障。"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .data import CONFIG, bus_index
from .network import (
    BUS_IDS,
    FREQUENCY_HZ,
    S_BASE_MVA,
    V_BASE_KV,
    add_ground_impedance,
    build_ybus,
    make_branches,
)
from .power_flow import solve_power_flow


A_OPERATOR = np.exp(1j * 2.0 * np.pi / 3.0)
SEQUENCE_TO_PHASE = np.array(
    [[1, 1, 1], [1, A_OPERATOR**2, A_OPERATOR], [1, A_OPERATOR, A_OPERATOR**2]],
    dtype=complex,
)
PHASE_TO_SEQUENCE = np.linalg.inv(SEQUENCE_TO_PHASE)


@dataclass(frozen=True)
class ThreePhaseFaultResult:
    bus: str
    prefault_voltage: np.ndarray
    zbus: np.ndarray
    z_thevenin_exact_pu: complex
    z_thevenin_engineering_pu: complex
    current_pu: complex
    current_ka: float
    short_circuit_mva: float
    postfault_voltage: np.ndarray


@dataclass(frozen=True)
class UnbalancedFaultResult:
    kind: str
    bus: str
    z1_pu: complex
    z2_pu: complex
    z0_pu: complex
    sequence_current_pu: np.ndarray
    phase_current_pu: np.ndarray


def phase_to_sequence(phase: np.ndarray | list[complex]) -> np.ndarray:
    return PHASE_TO_SEQUENCE @ np.asarray(phase, dtype=complex)


def sequence_to_phase(sequence: np.ndarray | list[complex]) -> np.ndarray:
    return SEQUENCE_TO_PHASE @ np.asarray(sequence, dtype=complex)


def build_fault_ybus(line_count: int = 2, include_line_shunt: bool = True) -> np.ndarray:
    """构造双电源三相短路的正序故障分量网络。"""
    ybus = build_ybus(make_branches(line_count, include_line_shunt, sequence=1))
    g1 = CONFIG["generators"]["G1"]
    g2 = CONFIG["generators"]["G2eq"]
    add_ground_impedance(ybus, bus_index("B1"), 1j * float(g1["xdpp"]))
    add_ground_impedance(ybus, bus_index("B3"), 1j * float(g2["x1"]))
    return ybus


def build_fault_zbus(line_count: int = 2, include_line_shunt: bool = True) -> np.ndarray:
    return np.linalg.inv(build_fault_ybus(line_count, include_line_shunt))


def solve_three_phase_fault(
    fault_bus: str = "B2",
    line_count: int = 2,
    prefault_scenario: str = "PF1",
    fault_impedance_pu: complex = 0.0j,
    include_line_shunt: bool = True,
) -> ThreePhaseFaultResult:
    power_flow = solve_power_flow(prefault_scenario)
    if not power_flow.converged:
        raise RuntimeError(f"{prefault_scenario} 潮流未收敛")
    k = bus_index(fault_bus)
    zbus = build_fault_zbus(line_count, include_line_shunt)
    z_exact = complex(zbus[k, k])
    z_engineering = complex(round(z_exact.real, 5), round(z_exact.imag, 5))
    current = power_flow.voltage[k] / (z_engineering + fault_impedance_pu)
    postfault_voltage = power_flow.voltage - zbus[:, k] * current
    base_current_ka = S_BASE_MVA / (math.sqrt(3.0) * V_BASE_KV[k])
    return ThreePhaseFaultResult(
        bus=fault_bus,
        prefault_voltage=power_flow.voltage,
        zbus=zbus,
        z_thevenin_exact_pu=z_exact,
        z_thevenin_engineering_pu=z_engineering,
        current_pu=current,
        current_ka=abs(current) * base_current_ka,
        short_circuit_mva=abs(current) * S_BASE_MVA,
        postfault_voltage=postfault_voltage,
    )


def solve_b2_three_phase_fault() -> ThreePhaseFaultResult:
    return solve_three_phase_fault("B2", 2, "PF1", 0.0j, True)


def solve_b2_single_source_fault(
    fault_impedance_pu: complex = 0.0j,
) -> ThreePhaseFaultResult:
    """第12讲：仅保留 G1 和 T1，不引入 B3 等值电源。"""
    n0 = solve_power_flow("N0")
    prefault = n0.voltage
    g1 = CONFIG["generators"]["G1"]
    t1 = next(item for item in CONFIG["branches"] if item["id"] == "T1")
    z = complex(float(t1["r1"]), float(t1["x1"]) + float(g1["xdpp"]))
    z_engineering = complex(round(z.real, 5), round(z.imag, 5))
    current = prefault[1] / (z_engineering + fault_impedance_pu)
    base_current_ka = S_BASE_MVA / (math.sqrt(3.0) * V_BASE_KV[1])
    zbus = np.zeros((4, 4), dtype=complex)
    zbus[1, 1] = z
    return ThreePhaseFaultResult(
        bus="B2",
        prefault_voltage=prefault,
        zbus=zbus,
        z_thevenin_exact_pu=z,
        z_thevenin_engineering_pu=z_engineering,
        current_pu=current,
        current_ka=abs(current) * base_current_ka,
        short_circuit_mva=abs(current) * S_BASE_MVA,
        postfault_voltage=np.full(4, np.nan + 0.0j),
    )


def peak_factor_iec(r_pu: float, x_pu: float) -> float:
    """IEC 常用近似：κ=1.02+0.98 exp(-3R/X)。"""
    if x_pu <= 0.0:
        raise ValueError("X 必须为正")
    return 1.02 + 0.98 * math.exp(-3.0 * r_pu / x_pu)


def aperiodic_time_constant(r_pu: float, x_pu: float) -> float:
    if r_pu <= 0.0:
        return math.inf
    return x_pu / (2.0 * math.pi * FREQUENCY_HZ * r_pu)


def peak_short_circuit_current(i_initial_rms: float, kappa: float) -> float:
    return math.sqrt(2.0) * kappa * i_initial_rms


def _sequence_ybus(sequence: int, line_count: int = 2) -> np.ndarray:
    if sequence in (1, 2):
        ybus = build_ybus(make_branches(line_count, False, sequence=sequence))
        g1 = CONFIG["generators"]["G1"]
        g2 = CONFIG["generators"]["G2eq"]
        z_g1 = complex(float(g1["r1"]), float(g1["xdpp"] if sequence == 1 else g1["x2"]))
        z_g2 = 1j * float(g2["x1"] if sequence == 1 else g2["x2"])
        add_ground_impedance(ybus, bus_index("B1"), z_g1)
        add_ground_impedance(ybus, bus_index("B3"), z_g2)
        return ybus

    if sequence != 0:
        raise ValueError("sequence 只能取 0、1、2")

    # 零序：T1 的 Δ 侧把 B1 与高压网隔离；高压 YN 侧仍为 B2 提供接地通道。
    ybus = np.zeros((3, 3), dtype=complex)  # 顺序为 B2、B3、B4

    def add_branch(i: int, j: int, impedance: complex) -> None:
        y = 1.0 / impedance
        ybus[i, i] += y
        ybus[j, j] += y
        ybus[i, j] -= y
        ybus[j, i] -= y

    def add_shunt(i: int, impedance: complex) -> None:
        ybus[i, i] += 1.0 / impedance

    line = next(item for item in CONFIG["branches"] if item["id"] == "L1")
    t1 = next(item for item in CONFIG["branches"] if item["id"] == "T1")
    t2 = next(item for item in CONFIG["branches"] if item["id"] == "T2")
    for _ in range(line_count):
        add_branch(0, 1, complex(float(line["r0"]), float(line["x0"])))
    add_branch(1, 2, complex(float(t2["r0"]), float(t2["x0"])))
    add_shunt(0, complex(float(t1["r0"]), float(t1["x0"])))
    add_shunt(1, 1j * float(CONFIG["generators"]["G2eq"]["x0"]))
    return ybus


def sequence_driving_point_impedance(
    fault_bus: str = "B4", sequence: int = 1, line_count: int = 2
) -> complex:
    ybus = _sequence_ybus(sequence, line_count)
    if sequence == 0:
        reduced_index = {"B2": 0, "B3": 1, "B4": 2}
        if fault_bus not in reduced_index:
            raise ValueError("该零序教学网络只定义 B2、B3、B4")
        return complex(np.linalg.inv(ybus)[reduced_index[fault_bus], reduced_index[fault_bus]])
    return complex(np.linalg.inv(ybus)[bus_index(fault_bus), bus_index(fault_bus)])


def solve_b4_single_line_ground_fault(
    prefault_voltage_pu: complex = 1.0 + 0.0j,
    fault_impedance_pu: complex = 0.0j,
) -> UnbalancedFaultResult:
    z1 = sequence_driving_point_impedance("B4", 1)
    z2 = sequence_driving_point_impedance("B4", 2)
    z0 = sequence_driving_point_impedance("B4", 0)
    i1 = prefault_voltage_pu / (z1 + z2 + z0 + 3.0 * fault_impedance_pu)
    sequence_current = np.array([i1, i1, i1], dtype=complex)  # [I0,I1,I2]
    phase_current = sequence_to_phase(sequence_current)
    return UnbalancedFaultResult(
        "single-line-to-ground", "B4", z1, z2, z0, sequence_current, phase_current
    )


def solve_b4_line_to_line_fault(
    prefault_voltage_pu: complex = 1.0 + 0.0j,
    fault_impedance_pu: complex = 0.0j,
) -> UnbalancedFaultResult:
    z1 = sequence_driving_point_impedance("B4", 1)
    z2 = sequence_driving_point_impedance("B4", 2)
    z0 = sequence_driving_point_impedance("B4", 0)
    i1 = prefault_voltage_pu / (z1 + z2 + fault_impedance_pu)
    sequence_current = np.array([0.0j, i1, -i1], dtype=complex)
    phase_current = sequence_to_phase(sequence_current)
    return UnbalancedFaultResult("line-to-line", "B4", z1, z2, z0, sequence_current, phase_current)


def format_complex(value: complex, digits: int = 5) -> str:
    return f"{value.real:.{digits}f}{value.imag:+.{digits}f}j"


def main() -> None:
    result = solve_b2_three_phase_fault()
    print("B2 三相金属性短路（双电源、完整复数网络）")
    print(f"Z22={format_complex(result.z_thevenin_engineering_pu)} p.u.")
    print(f"Ik''={format_complex(result.current_pu, 4)} p.u.，|Ik''|={abs(result.current_pu):.3f} p.u.")
    print(f"Ik''={result.current_ka:.3f} kA，Sk''={result.short_circuit_mva:.1f} MVA")


if __name__ == "__main__":
    main()
