"""依次运行20讲课堂程序，用于交付前烟雾测试。"""

from __future__ import annotations

from importlib import import_module


LECTURE_MODULES = [
    "lecture_01_overview",
    "lecture_02_line_model",
    "lecture_03_transformer_load",
    "lecture_04_per_unit",
    "lecture_05_voltage_drop",
    "lecture_06_simple_power_flow",
    "lecture_07_ybus",
    "lecture_08_bus_types",
    "lecture_09_newton_power_flow",
    "lecture_10_frequency_control",
    "lecture_11_voltage_control",
    "lecture_12_initial_short_circuit",
    "lecture_13_park_transform",
    "lecture_14_machine_parameters",
    "lecture_15_sudden_short_circuit",
    "lecture_16_practical_fault",
    "lecture_17_symmetrical_components",
    "lecture_18_unbalanced_fault",
    "lecture_19_stability_fundamentals",
    "lecture_20_integrated_case",
]


def main() -> None:
    for module_name in LECTURE_MODULES:
        import_module(f"lectures.{module_name}").main()


if __name__ == "__main__":
    main()
