"""四母线系统的极坐标牛顿—拉夫逊潮流程序。"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import numpy as np

from .data import CONFIG
from .network import (
    BUS_NAMES,
    S_BASE_MVA,
    Branch,
    branch_admittance_terms,
    build_ybus,
    make_branches,
)


V_MIN_PU = 0.95
V_MAX_PU = 1.05


@dataclass(frozen=True)
class Scenario:
    code: str
    description: str
    load_p_mw: float
    load_q_mvar: float
    line_count: int
    use_g2_pv: bool
    g2_p_mw: float = 20.0
    g2_v_pu: float = 1.02
    q_comp_mvar: float = 0.0
    t2_tap: float = 1.0


@dataclass
class PowerFlowResult:
    scenario: Scenario
    converged: bool
    iterations: int
    voltage: np.ndarray
    injection: np.ndarray
    branches: list[Branch]
    branch_flows: list[tuple[complex, complex, complex]]
    max_mismatch: float

    def total_loss_mw(self) -> float:
        return float(sum(flow[2].real for flow in self.branch_flows) * S_BASE_MVA)


def _scenario(code: str) -> Scenario:
    item = CONFIG["scenarios"][code]
    load = CONFIG["loads"][item["load"]]
    return Scenario(
        code=code,
        description=item["description"],
        load_p_mw=float(load["p_mw"]),
        load_q_mvar=float(load["q_mvar"]),
        line_count=int(item["line_count"]),
        use_g2_pv=item["g2_mode"] == "pv",
        g2_p_mw=float(CONFIG["generators"]["G2eq"]["p_mw"]),
        g2_v_pu=float(CONFIG["generators"]["G2eq"]["v_pu"]),
    )


SCENARIOS = {code: _scenario(code) for code in ("N0", "N1", "H1", "PF1")}


def specified_injections(scenario: Scenario) -> tuple[np.ndarray, np.ndarray]:
    p_spec = np.zeros(4)
    q_spec = np.zeros(4)
    p_spec[3] = -scenario.load_p_mw / S_BASE_MVA
    q_spec[3] = (-scenario.load_q_mvar + scenario.q_comp_mvar) / S_BASE_MVA
    if scenario.use_g2_pv:
        p_spec[2] = scenario.g2_p_mw / S_BASE_MVA
    return p_spec, q_spec


def calculate_injections(ybus: np.ndarray, voltage: np.ndarray) -> np.ndarray:
    return voltage * np.conj(ybus @ voltage)


def build_jacobian(
    ybus: np.ndarray,
    voltage: np.ndarray,
    injection: np.ndarray,
    angle_buses: np.ndarray,
    pq_buses: np.ndarray,
) -> np.ndarray:
    g, b = ybus.real, ybus.imag
    vm, va = np.abs(voltage), np.angle(voltage)
    p, q = injection.real, injection.imag
    n_ang, n_pq = len(angle_buses), len(pq_buses)
    jacobian = np.zeros((n_ang + n_pq, n_ang + n_pq))

    for row, i in enumerate(angle_buses):
        for col, k in enumerate(angle_buses):
            if i == k:
                jacobian[row, col] = -q[i] - b[i, i] * vm[i] ** 2
            else:
                theta = va[i] - va[k]
                jacobian[row, col] = vm[i] * vm[k] * (
                    g[i, k] * np.sin(theta) - b[i, k] * np.cos(theta)
                )
        for col, k in enumerate(pq_buses):
            if i == k:
                jacobian[row, n_ang + col] = p[i] / vm[i] + g[i, i] * vm[i]
            else:
                theta = va[i] - va[k]
                jacobian[row, n_ang + col] = vm[i] * (
                    g[i, k] * np.cos(theta) + b[i, k] * np.sin(theta)
                )

    for row, i in enumerate(pq_buses):
        out_row = n_ang + row
        for col, k in enumerate(angle_buses):
            if i == k:
                jacobian[out_row, col] = p[i] - g[i, i] * vm[i] ** 2
            else:
                theta = va[i] - va[k]
                jacobian[out_row, col] = -vm[i] * vm[k] * (
                    g[i, k] * np.cos(theta) + b[i, k] * np.sin(theta)
                )
        for col, k in enumerate(pq_buses):
            if i == k:
                jacobian[out_row, n_ang + col] = q[i] / vm[i] - b[i, i] * vm[i]
            else:
                theta = va[i] - va[k]
                jacobian[out_row, n_ang + col] = vm[i] * (
                    g[i, k] * np.sin(theta) - b[i, k] * np.cos(theta)
                )
    return jacobian


def calculate_branch_flow(branch: Branch, voltage: np.ndarray) -> tuple[complex, complex, complex]:
    i, j = branch.from_bus, branch.to_bus
    vi, vj = voltage[i], voltage[j]
    yff, yft, ytf, ytt = branch_admittance_terms(branch)
    current_ij = yff * vi + yft * vj
    current_ji = ytf * vi + ytt * vj
    s_ij = vi * np.conj(current_ij)
    s_ji = vj * np.conj(current_ji)
    return s_ij, s_ji, s_ij + s_ji


def solve_power_flow(
    scenario: str | Scenario = "N0",
    tolerance: float = 1e-10,
    max_iterations: int = 30,
) -> PowerFlowResult:
    if isinstance(scenario, str):
        scenario = SCENARIOS[scenario]

    branches = make_branches(
        scenario.line_count,
        include_line_shunt=True,
        sequence=1,
        t2_tap=scenario.t2_tap,
    )
    ybus = build_ybus(branches)
    p_spec, q_spec = specified_injections(scenario)

    slack = 0
    pq_buses = np.array([1, 3], dtype=int) if scenario.use_g2_pv else np.array([1, 2, 3], dtype=int)
    angle_buses = np.array([i for i in range(4) if i != slack], dtype=int)

    vm = np.ones(4)
    va = np.zeros(4)
    vm[slack] = 1.04
    if scenario.use_g2_pv:
        vm[2] = scenario.g2_v_pu

    converged = False
    max_mismatch = float("inf")
    iteration = 0
    for iteration in range(1, max_iterations + 1):
        voltage = vm * np.exp(1j * va)
        injection = calculate_injections(ybus, voltage)
        mismatch = np.concatenate(
            (
                p_spec[angle_buses] - injection.real[angle_buses],
                q_spec[pq_buses] - injection.imag[pq_buses],
            )
        )
        max_mismatch = float(np.max(np.abs(mismatch)))
        if max_mismatch < tolerance:
            converged = True
            break

        jacobian = build_jacobian(ybus, voltage, injection, angle_buses, pq_buses)
        correction = np.linalg.solve(jacobian, mismatch)
        va[angle_buses] += correction[: len(angle_buses)]
        vm[pq_buses] += correction[len(angle_buses) :]
        if np.any(vm[pq_buses] <= 0.0):
            raise RuntimeError("迭代出现非正电压，初值或工况可能不可行")

    voltage = vm * np.exp(1j * va)
    injection = calculate_injections(ybus, voltage)
    branch_flows = [calculate_branch_flow(branch, voltage) for branch in branches]
    return PowerFlowResult(
        scenario=scenario,
        converged=converged,
        iterations=iteration,
        voltage=voltage,
        injection=injection,
        branches=branches,
        branch_flows=branch_flows,
        max_mismatch=max_mismatch,
    )


def print_result(result: PowerFlowResult) -> None:
    print(f"\n场景 {result.scenario.code}：{result.scenario.description}")
    print(
        f"收敛={result.converged}，迭代次数={result.iterations}，"
        f"最大失配={result.max_mismatch:.3e} p.u."
    )
    print("母线                U/p.u.    δ/deg       P/MW      Q/Mvar")
    for index, name in enumerate(BUS_NAMES):
        voltage = result.voltage[index]
        injection = result.injection[index] * S_BASE_MVA
        print(
            f"{name:<18} {abs(voltage):8.5f} {np.degrees(np.angle(voltage)):9.4f}"
            f" {injection.real:10.3f} {injection.imag:10.3f}"
        )
    print(f"系统有功损耗：{result.total_loss_mw():.4f} MW")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=SCENARIOS, default="N0")
    parser.add_argument("--all", action="store_true", help="依次计算全部工况")
    args = parser.parse_args()

    codes = list(SCENARIOS) if args.all else [args.scenario]
    for code in codes:
        result = solve_power_flow(code)
        print_result(result)
        if not result.converged:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
