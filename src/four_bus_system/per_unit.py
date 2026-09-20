"""基准量、标幺换算以及线路和变压器参数计算。"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .data import CONFIG, branch_record


@dataclass(frozen=True)
class BaseQuantities:
    voltage_kv: float
    power_mva: float
    current_ka: float
    impedance_ohm: float
    admittance_siemens: float


def base_quantities(voltage_kv: float, power_mva: float | None = None) -> BaseQuantities:
    power_mva = float(power_mva or CONFIG["base"]["s_mva"])
    z_base = voltage_kv**2 / power_mva
    return BaseQuantities(
        voltage_kv=voltage_kv,
        power_mva=power_mva,
        current_ka=power_mva / (math.sqrt(3.0) * voltage_kv),
        impedance_ohm=z_base,
        admittance_siemens=1.0 / z_base,
    )


def change_impedance_base(
    z_pu_old: complex,
    s_old_mva: float,
    v_old_kv: float,
    s_new_mva: float,
    v_new_kv: float,
) -> complex:
    return z_pu_old * (s_new_mva / s_old_mva) * (v_old_kv / v_new_kv) ** 2


def transformer_from_short_circuit_test(
    rating_mva: float, uk_percent: float, copper_loss_kw: float
) -> complex:
    """由短路电压百分数和额定铜耗求自身容量基准下的标幺阻抗。"""
    z = uk_percent / 100.0
    r = (copper_loss_kw / 1000.0) / rating_mva
    if r > z:
        raise ValueError("铜耗对应的标幺电阻不能大于短路阻抗")
    return complex(r, math.sqrt(z * z - r * r))


def line_parameters(line_id: str = "L1") -> dict[str, float]:
    record = branch_record(line_id)
    length = float(record["length_km"])
    base = base_quantities(220.0)
    r_ohm = float(record["r1"]) * base.impedance_ohm
    x_ohm = float(record["x1"]) * base.impedance_ohm
    b_siemens = float(record["b1"]) * base.admittance_siemens
    return {
        "length_km": length,
        "r_ohm": r_ohm,
        "x_ohm": x_ohm,
        "b_siemens": b_siemens,
        "r_ohm_per_km": r_ohm / length,
        "x_ohm_per_km": x_ohm / length,
        "b_siemens_per_km": b_siemens / length,
        "r_pu": float(record["r1"]),
        "x_pu": float(record["x1"]),
        "b_pu": float(record["b1"]),
    }
