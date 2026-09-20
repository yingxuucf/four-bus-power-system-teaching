from __future__ import annotations

from contextlib import redirect_stdout
from importlib import import_module
import io
import math
import unittest

import numpy as np

from four_bus_system.control import compensation_for_target_voltage, primary_frequency_response
from four_bus_system.fault import (
    peak_factor_iec,
    phase_to_sequence,
    sequence_to_phase,
    solve_b2_single_source_fault,
    solve_b4_single_line_ground_fault,
)
from four_bus_system.machine import inverse_park_transform, park_transform, stator_free_current_components
from four_bus_system.per_unit import base_quantities, line_parameters
from four_bus_system.stability import equal_area_components, stability_summary
from run_all import LECTURE_MODULES


class CoursePipelineTests(unittest.TestCase):
    def test_parameter_chain(self) -> None:
        base = base_quantities(220.0)
        self.assertAlmostEqual(base.impedance_ohm, 484.0, places=12)
        line = line_parameters("L1")
        self.assertAlmostEqual(line["r_ohm"], 7.26, places=10)
        self.assertAlmostEqual(line["x_ohm"], 58.08, places=10)

    def test_frequency_and_voltage_control(self) -> None:
        response = primary_frequency_response()
        self.assertAlmostEqual(response.delta_frequency_hz, -10.0 / 116.8, places=12)
        self.assertAlmostEqual(response.balance_mw, 10.0, places=10)
        compensation, result = compensation_for_target_voltage()
        self.assertGreater(compensation, 0.0)
        self.assertAlmostEqual(abs(result.voltage[3]), 0.95, places=9)

    def test_single_source_short_circuit_and_peak(self) -> None:
        result = solve_b2_single_source_fault()
        self.assertEqual(result.z_thevenin_engineering_pu, 0.005 + 0.30j)
        self.assertAlmostEqual(abs(result.current_pu), 3.360125215, places=8)
        self.assertAlmostEqual(peak_factor_iec(0.005, 0.30), 1.952204836, places=9)

    def test_park_round_trip_and_double_frequency_condition(self) -> None:
        abc = np.array([0.8, -0.1, -0.7])
        theta = 0.37
        np.testing.assert_allclose(inverse_park_transform(park_transform(abc, theta), theta), abc, atol=1e-12)
        _, double, _ = stator_free_current_components(np.linspace(0.0, 0.1, 20), 0.2)
        np.testing.assert_allclose(double, 0.0, atol=1e-12)

    def test_symmetrical_components_and_slg_reference(self) -> None:
        phase = np.array([1.0 + 0.2j, -0.4 - 0.8j, -0.3 + 0.7j])
        np.testing.assert_allclose(sequence_to_phase(phase_to_sequence(phase)), phase, atol=1e-12)
        result = solve_b4_single_line_ground_fault()
        self.assertAlmostEqual(abs(result.phase_current_pu[0]), 4.1604883925, places=9)
        self.assertLess(abs(result.phase_current_pu[1]), 1e-12)
        self.assertLess(abs(result.phase_current_pu[2]), 1e-12)

    def test_stability_reference(self) -> None:
        result = stability_summary()
        self.assertAlmostEqual(math.degrees(result.delta0_rad), 24.0638231417, places=8)
        self.assertAlmostEqual(math.degrees(result.delta_critical_rad), 83.2913211555, places=8)
        self.assertAlmostEqual(result.critical_time_s, 0.2810160091, places=9)
        areas = equal_area_components()
        self.assertAlmostEqual(areas["accelerating"], areas["decelerating"], places=10)

    def test_all_twenty_lecture_entry_points(self) -> None:
        self.assertEqual(len(LECTURE_MODULES), 20)
        output = io.StringIO()
        with redirect_stdout(output):
            for module_name in LECTURE_MODULES:
                import_module(f"lectures.{module_name}").main()
        self.assertIn("第20讲", output.getvalue())


if __name__ == "__main__":
    unittest.main()
