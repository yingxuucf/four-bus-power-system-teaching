"""综合案例：把稳态、调控、故障和稳定指标组织成一条证据链。"""

from __future__ import annotations

from .control import compensation_for_target_voltage, primary_frequency_response
from .fault import solve_b2_three_phase_fault, solve_b4_single_line_ground_fault
from .power_flow import SCENARIOS, solve_power_flow
from .stability import stability_summary


def course_summary() -> dict[str, object]:
    power_flow = {code: solve_power_flow(code) for code in SCENARIOS}
    compensation, controlled = compensation_for_target_voltage()
    frequency = primary_frequency_response()
    three_phase = solve_b2_three_phase_fault()
    slg = solve_b4_single_line_ground_fault()
    stability = stability_summary()
    return {
        "power_flow": power_flow,
        "required_compensation_mvar": compensation,
        "controlled_b4_voltage_pu": abs(controlled.voltage[3]),
        "frequency": frequency,
        "b2_three_phase_fault": three_phase,
        "b4_slg_fault": slg,
        "stability": stability,
    }
