from __future__ import annotations

import unittest

import numpy as np

from four_bus_system.fault import build_fault_zbus, solve_b2_three_phase_fault
from four_bus_system.power_flow import solve_power_flow


class ReferenceResultTests(unittest.TestCase):
    def test_power_flow_reference_values(self) -> None:
        expected = {
            "N0": ([1.04, 1.00817756, 0.98614017, 0.94852434], 0.791249),
            "N1": ([1.04, 1.00108779, 0.95154878, 0.91220664], 1.245853),
            "H1": ([1.04, 0.97509765, 0.93381014, 0.86633722], 2.001004),
            "PF1": ([1.04, 1.02933119, 1.02, 0.98392309], 0.422606),
        }
        for code, (voltage, loss_mw) in expected.items():
            with self.subTest(code=code):
                result = solve_power_flow(code)
                self.assertTrue(result.converged)
                np.testing.assert_allclose(np.abs(result.voltage), voltage, atol=2e-7, rtol=0)
                self.assertAlmostEqual(result.total_loss_mw(), loss_mw, places=5)

    def test_fault_zbus_matches_slide_values(self) -> None:
        zbus = build_fault_zbus()
        expected = np.array(
            [
                [0.00192 + 0.12192j, 0.00093 + 0.08284j, -0.00144 + 0.05920j, -0.00144 + 0.05920j],
                [0.00093 + 0.08284j, 0.00346 + 0.12424j, -0.00068 + 0.08883j, -0.00068 + 0.08883j],
                [-0.00144 + 0.05920j, -0.00068 + 0.08883j, 0.00108 + 0.10648j, 0.00108 + 0.10648j],
                [-0.00144 + 0.05920j, -0.00068 + 0.08883j, 0.00108 + 0.10648j, 0.00608 + 0.22648j],
            ],
            dtype=complex,
        )
        rounded = np.round(zbus.real, 5) + 1j * np.round(zbus.imag, 5)
        np.testing.assert_array_equal(rounded, expected)

    def test_b2_three_phase_fault(self) -> None:
        result = solve_b2_three_phase_fault()
        self.assertEqual(result.z_thevenin_engineering_pu, 0.00346 + 0.12424j)
        self.assertAlmostEqual(result.current_pu.real, -0.078409, places=5)
        self.assertAlmostEqual(result.current_pu.imag, -8.281440, places=5)
        self.assertAlmostEqual(abs(result.current_pu), 8.281811, places=5)
        self.assertAlmostEqual(result.current_ka, 2.173412, places=5)
        self.assertAlmostEqual(result.short_circuit_mva, 828.181146, places=4)


if __name__ == "__main__":
    unittest.main()
