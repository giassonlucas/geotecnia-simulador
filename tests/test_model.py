import math
import unittest

from calculation.model import (
    DEFAULTS, annular_area_stress, boussinesq_point, circular_area_stress,
    initial_stresses, simulate, strip_stress, validate_inputs,
)


class CalculationTests(unittest.TestCase):
    def test_initial_profile_at_minus_four(self):
        got = initial_stresses(4.0, DEFAULTS)
        self.assertAlmostEqual(got["sigma_v_kPa"], 74.7, places=10)
        self.assertAlmostEqual(got["u_kPa"], 9.81, places=10)
        self.assertAlmostEqual(got["sigma_eff_kPa"], 64.89, places=10)

    def test_point_load_on_axis(self):
        self.assertAlmostEqual(boussinesq_point(5000, 0, 4), 149.207759, places=6)

    def test_finite_strip_formula(self):
        self.assertAlmostEqual(strip_stress(62.7, 0, 4, 5, 15), 3.498569, places=6)

    def test_disk_center_numeric_quadrature(self):
        got = circular_area_stress(-18.5, 0, 0, 3.5, 0, 0, 3)
        self.assertAlmostEqual(got, -13.400858, places=5)

    def test_annulus_center_numeric_quadrature(self):
        ring_height = math.pi * 3.5**2 / (math.pi * (4.5**2 - 3.5**2))
        got = annular_area_stress(18.5 * ring_height, 0, 0, 3.5, 4.5, 0, 0, 4)
        exact = 28.328125 * 4**3 * ((4**2 + 3.5**2) ** -1.5 - (4**2 + 4.5**2) ** -1.5)
        self.assertAlmostEqual(got, exact, places=10)

    def test_defaults_simulate_and_superpose(self):
        result = simulate(DEFAULTS)
        self.assertEqual(len(result["map_points"]), len(result["grid"]["x_m"]) * len(result["grid"]["y_m"]))
        point = result["map_points"][0]
        self.assertAlmostEqual(point["total_kPa"], point["tower_kPa"] + point["fill_kPa"] + point["excavation_kPa"] + point["ring_kPa"], places=10)

    def test_rejects_out_of_domain_plane(self):
        bad = dict(DEFAULTS, group_elevation_m=-15)
        self.assertTrue(any("−14 m" in error for error in validate_inputs(bad)))

    def test_gamma_accepts_arbitrary_decimal_values(self):
        for value in (15.31, 15.32, 15.35, 15.40, 15.37):
            with self.subTest(value=value):
                self.assertEqual(validate_inputs(dict(DEFAULTS, gamma_soft_clay_sat_kN_m3=value)), [])

    def test_gamma_accepts_brazilian_decimal_comma(self):
        p = dict(DEFAULTS, gamma_soft_clay_sat_kN_m3="15,35")
        self.assertEqual(validate_inputs(p), [])
        self.assertAlmostEqual(simulate(p)["inputs"]["gamma_soft_clay_sat_kN_m3"], 15.35)

    def test_locale_decimal_comma_for_geometry_and_coordinates(self):
        p = dict(DEFAULTS, tower_x_m="18,25", fill_height_m="3,85", ring_width_m="1,05")
        self.assertEqual(validate_inputs(p), [])
        out = simulate(p)
        self.assertEqual(out["inputs"]["tower_x_m"], 18.25)
        self.assertEqual(out["inputs"]["fill_height_m"], 3.85)
        self.assertEqual(out["inputs"]["ring_width_m"], 1.05)

    def test_gamma_rejects_nonpositive_or_non_numeric(self):
        for value in (0, -0.01, "abc"):
            with self.subTest(value=value):
                self.assertTrue(validate_inputs(dict(DEFAULTS, gamma_soft_clay_sat_kN_m3=value)))

    def test_all_numeric_parameters_accept_fractional_values(self):
        for name, original in DEFAULTS.items():
            if name == "contour_count":
                continue
            candidate = dict(DEFAULTS, **{name: original + 0.013})
            with self.subTest(field=name):
                self.assertEqual(validate_inputs(candidate), [])

    def test_small_positive_values_are_not_arbitrarily_rounded_to_hundredths(self):
        self.assertEqual(validate_inputs(dict(DEFAULTS, gamma_soft_clay_sat_kN_m3=0.001)), [])

    def test_small_but_positive_engineering_inputs_complete_simulation(self):
        p = dict(DEFAULTS, gamma_soft_clay_sat_kN_m3=0.001, tower_load_kN=0.001,
                 fill_height_m=0.001, fill_gamma_kN_m3=0.001,
                 excavation_diameter_m=0.01, excavation_depth_m=0.001,
                 ring_width_m=0.001, grid_step_m=2.5)
        result = simulate(p)
        self.assertTrue(math.isfinite(result["summary"]["max_total"]["total_kPa"]))

    def test_changed_parameters_update_dependent_outputs(self):
        from calculation.model import initial_stresses
        low = dict(DEFAULTS, gamma_soft_clay_sat_kN_m3=15.3)
        high = dict(DEFAULTS, gamma_soft_clay_sat_kN_m3=15.5)
        self.assertNotEqual(initial_stresses(10, low)["sigma_eff_kPa"], initial_stresses(10, high)["sigma_eff_kPa"])
        # This soil layer is below the group's −4 m plane, so its weight must
        # not alter the −4 m map or normalization.
        self.assertEqual(simulate(low)["initial_at_group_plane"], simulate(high)["initial_at_group_plane"])
        base = simulate(DEFAULTS)
        heavier_tower = simulate(dict(DEFAULTS, tower_load_kN=5500))
        self.assertNotEqual(base["summary"]["max_total"]["total_kPa"], heavier_tower["summary"]["max_total"]["total_kPa"])

    def test_documented_ranges_and_integer_field_still_enforced(self):
        self.assertTrue(validate_inputs(dict(DEFAULTS, group_elevation_m=-14.01)))
        self.assertTrue(validate_inputs(dict(DEFAULTS, water_table_elevation_m=0.01)))
        self.assertTrue(validate_inputs(dict(DEFAULTS, grid_step_m=0.249)))
        self.assertTrue(validate_inputs(dict(DEFAULTS, contour_count=12.5)))
        self.assertTrue(validate_inputs(dict(DEFAULTS, group_elevation_m=-1.0)))


if __name__ == "__main__":
    unittest.main()
