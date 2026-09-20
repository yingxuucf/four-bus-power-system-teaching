"""一次调频、无功补偿与分接头调压教学计算。"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .data import CONFIG
from .power_flow import SCENARIOS, PowerFlowResult, solve_power_flow


@dataclass(frozen=True)
class FrequencyResponse:
    delta_load_mw: float
    unit_regulation_mw_per_hz: dict[str, float]
    delta_frequency_hz: float
    responses_mw: dict[str, float]

    @property
    def balance_mw(self) -> float:
        return float(sum(self.responses_mw.values()))


def primary_frequency_response(delta_load_mw: float | None = None) -> FrequencyResponse:
    settings = CONFIG["frequency_control"]
    delta_load = float(settings["load_step_mw"] if delta_load_mw is None else delta_load_mw)
    frequency = float(CONFIG["base"]["frequency_hz"])
    g1 = float(settings["g1_rated_mw"]) / (float(settings["g1_r"]) * frequency)
    g2 = float(settings["g2_rated_mw"]) / (float(settings["g2_r"]) * frequency)
    load_p = float(CONFIG["loads"]["normal"]["p_mw"])
    load = float(CONFIG["loads"]["frequency_d"]) * load_p / frequency
    regulation = {"G1": g1, "G2": g2, "负荷频率特性": load}
    delta_f = -delta_load / sum(regulation.values())
    responses = {name: -value * delta_f for name, value in regulation.items()}
    return FrequencyResponse(delta_load, regulation, delta_f, responses)


def voltage_control_case(
    base_scenario: str = "H1",
    compensation_mvar: float = 0.0,
    t2_tap: float = 1.0,
) -> PowerFlowResult:
    scenario = replace(
        SCENARIOS[base_scenario],
        code=f"{base_scenario}-Q{compensation_mvar:g}-tap{t2_tap:g}",
        q_comp_mvar=float(compensation_mvar),
        t2_tap=float(t2_tap),
    )
    return solve_power_flow(scenario)


def compensation_for_target_voltage(
    target_voltage_pu: float = 0.95,
    base_scenario: str = "H1",
    upper_mvar: float = 100.0,
) -> tuple[float, PowerFlowResult]:
    """二分搜索使 B4 电压达到目标值所需的最小并联无功。"""
    low, high = 0.0, float(upper_mvar)
    high_result = voltage_control_case(base_scenario, high)
    if abs(high_result.voltage[3]) < target_voltage_pu:
        raise ValueError("给定无功搜索上限不足以达到目标电压")
    for _ in range(50):
        middle = (low + high) / 2.0
        result = voltage_control_case(base_scenario, middle)
        if abs(result.voltage[3]) >= target_voltage_pu:
            high = middle
            high_result = result
        else:
            low = middle
    return high, high_result
