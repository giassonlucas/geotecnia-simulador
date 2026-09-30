"""Stress calculations for the course geotechnics problem.

Units: kN, m, kPa and kN/m³. Depth is positive downward internally; user-facing
elevations are negative below the natural ground surface.
"""

from __future__ import annotations

import math
from typing import Any


PROFILE_LIMIT_M = 14.0
EXCAVATION_BASE_DEPTH_M = 1.0
GRID_X_MAX_M = 45.0
GRID_Y_MAX_M = 28.0


def _as_number(value: Any) -> float:
    """Parse finite numeric input, accepting either decimal comma or point."""
    if isinstance(value, str):
        value = value.strip().replace(" ", "")
        if "," in value and "." in value:
            raise ValueError("Use apenas um separador decimal: vírgula ou ponto.")
        value = value.replace(",", ".")
    return float(value)


DEFAULTS: dict[str, float] = {
    "group_elevation_m": -4.0,
    "water_table_elevation_m": -3.0,
    "gamma_water_kN_m3": 9.81,
    "gamma_sand_nat_kN_m3": 18.5,
    "gamma_sand_sat_kN_m3": 19.2,
    "gamma_soft_clay_sat_kN_m3": 15.4,
    "gamma_medium_clay_sat_kN_m3": 19.0,
    "tower_load_kN": 5000.0,
    "tower_x_m": 18.0,
    "tower_y_m": 22.0,
    "fill_height_m": 3.8,
    "fill_gamma_kN_m3": 16.5,
    "fill_x_min_m": 5.0,
    "fill_x_max_m": 15.0,
    "excavation_x_m": 25.0,
    "excavation_y_m": 17.0,
    "excavation_diameter_m": 7.0,
    "excavation_depth_m": 1.0,
    "ring_width_m": 1.0,
    "grid_step_m": 1.0,
    "contour_count": 12.0,
}


def validate_inputs(raw: dict[str, Any]) -> list[str]:
    """Return user-facing validation errors without changing the input values."""
    errors: list[str] = []
    required = tuple(DEFAULTS)
    values: dict[str, float] = {}
    for name in required:
        try:
            value = _as_number(raw[name])
        except (KeyError, TypeError, ValueError):
            errors.append(f"Campo ausente ou não numérico: {name}.")
            continue
        if not math.isfinite(value):
            errors.append(f"O campo {name} precisa ser um número finito.")
        else:
            values[name] = value
    if errors:
        return errors

    if values["group_elevation_m"] > -EXCAVATION_BASE_DEPTH_M:
        errors.append("A cota do plano precisa estar na base da escavação ou abaixo dela (cota ≤ −1 m).")
    if values["group_elevation_m"] < -PROFILE_LIMIT_M:
        errors.append("A cota do plano não pode ficar abaixo do limite do perfil, −14 m.")
    if not (-PROFILE_LIMIT_M <= values["water_table_elevation_m"] <= 0.0):
        errors.append("A cota do N.A. deve estar entre −14 m e 0 m.")
    for name in (
        "gamma_water_kN_m3", "gamma_sand_nat_kN_m3", "gamma_sand_sat_kN_m3",
        "gamma_soft_clay_sat_kN_m3", "gamma_medium_clay_sat_kN_m3",
        "tower_load_kN", "fill_height_m", "fill_gamma_kN_m3",
        "excavation_diameter_m", "excavation_depth_m", "ring_width_m",
    ):
        if values[name] <= 0:
            errors.append(f"{name} deve ser maior que zero.")
    if values["fill_x_max_m"] <= values["fill_x_min_m"]:
        errors.append("O limite x final do aterro deve ser maior que o limite inicial.")
    if values["excavation_depth_m"] >= abs(values["group_elevation_m"]):
        errors.append("O plano de cálculo precisa ficar estritamente abaixo da base da escavação (distância vertical positiva).")
    if not (0.25 <= values["grid_step_m"] <= 2.5):
        errors.append("O passo da malha deve estar entre 0,25 m e 2,5 m.")
    if int(values["contour_count"]) != values["contour_count"] or not (4 <= values["contour_count"] <= 30):
        errors.append("O número de níveis de contorno deve ser um inteiro entre 4 e 30.")
    return errors


def initial_stresses(depth_m: float, p: dict[str, Any]) -> dict[str, float]:
    """Layered vertical total, hydrostatic pore pressure and effective stress."""
    d = float(depth_m)
    if not (0.0 <= d <= PROFILE_LIMIT_M):
        raise ValueError("A profundidade precisa estar entre 0 m e 14 m.")
    water_depth = -float(p["water_table_elevation_m"])
    sand_bottom = min(d, 8.0)
    nat_sand_thickness = min(sand_bottom, water_depth)
    sat_sand_thickness = max(0.0, sand_bottom - max(0.0, water_depth))
    soft_clay_thickness = max(0.0, min(d, 12.0) - 8.0)
    medium_clay_thickness = max(0.0, min(d, 14.0) - 12.0)
    sigma_v = (
        nat_sand_thickness * float(p["gamma_sand_nat_kN_m3"])
        + sat_sand_thickness * float(p["gamma_sand_sat_kN_m3"])
        + soft_clay_thickness * float(p["gamma_soft_clay_sat_kN_m3"])
        + medium_clay_thickness * float(p["gamma_medium_clay_sat_kN_m3"])
    )
    u = max(0.0, d - water_depth) * float(p["gamma_water_kN_m3"])
    return {"sigma_v_kPa": sigma_v, "u_kPa": u, "sigma_eff_kPa": sigma_v - u}


def boussinesq_point(load_kN: float, horizontal_distance_m: float, vertical_distance_m: float) -> float:
    """Boussinesq vertical stress increment from a point load."""
    z = float(vertical_distance_m)
    if z <= 0:
        raise ValueError("A distância vertical à carga concentrada deve ser maior que zero.")
    r2 = float(horizontal_distance_m) ** 2
    return 3.0 * float(load_kN) * z**3 / (2.0 * math.pi * (r2 + z**2) ** 2.5)


def _strip_primitive(t: float) -> float:
    return math.atan(t) + t / (1.0 + t * t)


def strip_stress(q_kPa: float, x_m: float, z_m: float, x_min_m: float, x_max_m: float) -> float:
    """Stress beneath a uniformly loaded finite strip, infinite in the y direction.

    Integrates the Boussinesq point-load kernel over x in [x_min, x_max] and
    over the infinite y direction. This yields q/π times the primitive change.
    """
    if z_m <= 0:
        raise ValueError("A distância vertical até o aterro deve ser maior que zero.")
    if x_max_m <= x_min_m:
        raise ValueError("A faixa precisa ter largura positiva.")
    t2 = (x_max_m - x_m) / z_m
    t1 = (x_min_m - x_m) / z_m
    return float(q_kPa) / math.pi * (_strip_primitive(t2) - _strip_primitive(t1))


def _gauss_legendre(n: int) -> tuple[list[float], list[float]]:
    """Nodes and weights on [-1, 1], computed with Newton iteration."""
    nodes = [0.0] * n
    weights = [0.0] * n
    half = (n + 1) // 2
    for i in range(half):
        x = math.cos(math.pi * (i + 0.75) / (n + 0.5))
        for _ in range(40):
            p0, p1 = 1.0, x
            for k in range(2, n + 1):
                p0, p1 = p1, ((2.0 * k - 1.0) * x * p1 - (k - 1.0) * p0) / k
            pn = x if n == 1 else p1
            pnm1 = 1.0 if n == 1 else p0
            derivative = n * (x * pn - pnm1) / (x * x - 1.0)
            delta = pn / derivative
            x -= delta
            if abs(delta) < 2e-15:
                break
        p0, p1 = 1.0, x
        for k in range(2, n + 1):
            p0, p1 = p1, ((2.0 * k - 1.0) * x * p1 - (k - 1.0) * p0) / k
        pn = x if n == 1 else p1
        pnm1 = 1.0 if n == 1 else p0
        derivative = n * (x * pn - pnm1) / (x * x - 1.0)
        weight = 2.0 / ((1.0 - x * x) * derivative * derivative)
        nodes[i], nodes[n - 1 - i] = -x, x
        weights[i] = weights[n - 1 - i] = weight
    return nodes, weights


_RADIAL_NODES, _RADIAL_WEIGHTS = _gauss_legendre(18)
_THETA_COUNT = 64


def _polar_load_points(cx: float, cy: float, r_inner: float, r_outer: float) -> list[tuple[float, float, float]]:
    """Return source-point coordinates and area quadrature weights."""
    if r_inner < 0 or r_outer <= r_inner:
        raise ValueError("Os raios da área circular/anelar são inválidos.")
    rmid = (r_inner + r_outer) / 2.0
    rhalf = (r_outer - r_inner) / 2.0
    theta_weight = 2.0 * math.pi / _THETA_COUNT
    points: list[tuple[float, float, float]] = []
    for node, weight in zip(_RADIAL_NODES, _RADIAL_WEIGHTS):
        radius = rmid + rhalf * node
        radial_area_weight = weight * rhalf * radius * theta_weight
        for j in range(_THETA_COUNT):
            theta = theta_weight * j
            points.append((cx + radius * math.cos(theta), cy + radius * math.sin(theta), radial_area_weight))
    return points


def circular_area_stress(
    q_kPa: float, cx_m: float, cy_m: float, radius_m: float,
    x_m: float, y_m: float, z_m: float,
) -> float:
    """Integrate Boussinesq vertical stress over a uniformly loaded circular area."""
    return annular_area_stress(q_kPa, cx_m, cy_m, 0.0, radius_m, x_m, y_m, z_m)


def annular_area_stress(
    q_kPa: float, cx_m: float, cy_m: float, r_inner_m: float, r_outer_m: float,
    x_m: float, y_m: float, z_m: float,
) -> float:
    """Integrate Boussinesq vertical stress over a uniformly loaded annulus."""
    if z_m <= 0:
        raise ValueError("O plano precisa estar abaixo do plano de aplicação da carga distribuída.")
    points = _polar_load_points(cx_m, cy_m, r_inner_m, r_outer_m)
    kernel_factor = 3.0 * float(q_kPa) * z_m**3 / (2.0 * math.pi)
    total = 0.0
    z2 = z_m * z_m
    for sx, sy, area_weight in points:
        radius_sq = (x_m - sx) ** 2 + (y_m - sy) ** 2
        total += area_weight / (radius_sq + z2) ** 2.5
    return kernel_factor * total


def _axis(max_value: float, requested_step: float) -> tuple[list[float], float]:
    count = max(1, math.ceil(max_value / requested_step))
    actual_step = max_value / count
    return [i * actual_step for i in range(count + 1)], actual_step


def _profile_rows(p: dict[str, Any], count: int = 57) -> list[dict[str, float]]:
    depths = {i * PROFILE_LIMIT_M / count for i in range(count + 1)}
    depths.update({0.0, -float(p["water_table_elevation_m"]), 8.0, 12.0, PROFILE_LIMIT_M})
    result = []
    for depth in sorted(d for d in depths if 0.0 <= d <= PROFILE_LIMIT_M):
        row = {"depth_m": depth, "elevation_m": -depth}
        row.update(initial_stresses(depth, p))
        result.append(row)
    return result


def simulate(raw: dict[str, Any]) -> dict[str, Any]:
    """Validate the inputs and calculate the profile and plan-view stress maps."""
    errors = validate_inputs(raw)
    if errors:
        raise ValueError("\n".join(errors))
    p: dict[str, Any] = dict(DEFAULTS)
    p.update({key: _as_number(value) for key, value in raw.items() if key in DEFAULTS})
    p["contour_count"] = int(p["contour_count"])

    depth = -p["group_elevation_m"]
    initial = initial_stresses(depth, p)
    if initial["sigma_eff_kPa"] <= 0:
        raise ValueError("A tensão efetiva inicial na cota do grupo deve ser positiva para normalizar o acréscimo.")

    xs, dx = _axis(GRID_X_MAX_M, p["grid_step_m"])
    ys, dy = _axis(GRID_Y_MAX_M, p["grid_step_m"])
    q_fill = p["fill_height_m"] * p["fill_gamma_kN_m3"]
    excavation_radius = p["excavation_diameter_m"] / 2.0
    ring_inner = excavation_radius
    ring_outer = ring_inner + p["ring_width_m"]
    excavation_volume = math.pi * excavation_radius**2 * p["excavation_depth_m"]
    ring_area = math.pi * (ring_outer**2 - ring_inner**2)
    ring_height = excavation_volume / ring_area
    q_excavation = -p["gamma_sand_nat_kN_m3"] * p["excavation_depth_m"]
    q_ring = p["gamma_sand_nat_kN_m3"] * ring_height

    map_values: dict[str, list[list[float]]] = {
        "tower": [], "fill": [], "excavation": [], "ring": [], "total": [], "ratio": []
    }
    map_points: list[dict[str, float]] = []
    tower_z = depth
    excavation_z = depth - p["excavation_depth_m"]
    for y in ys:
        row_components = {name: [] for name in map_values}
        for x in xs:
            r_tower = math.hypot(x - p["tower_x_m"], y - p["tower_y_m"])
            s_tower = boussinesq_point(p["tower_load_kN"], r_tower, tower_z)
            s_fill = strip_stress(q_fill, x, depth, p["fill_x_min_m"], p["fill_x_max_m"])
            s_exc = circular_area_stress(
                q_excavation, p["excavation_x_m"], p["excavation_y_m"], excavation_radius,
                x, y, excavation_z,
            )
            s_ring = annular_area_stress(
                q_ring, p["excavation_x_m"], p["excavation_y_m"], ring_inner, ring_outer,
                x, y, depth,
            )
            total = s_tower + s_fill + s_exc + s_ring
            ratio = total / initial["sigma_eff_kPa"]
            for name, value in (("tower", s_tower), ("fill", s_fill), ("excavation", s_exc), ("ring", s_ring), ("total", total), ("ratio", ratio)):
                row_components[name].append(value)
            map_points.append({"x_m": x, "y_m": y, "tower_kPa": s_tower, "fill_kPa": s_fill,
                               "excavation_kPa": s_exc, "ring_kPa": s_ring, "total_kPa": total,
                               "ratio": ratio, "ratio_percent": 100.0 * ratio})
        for name in map_values:
            map_values[name].append(row_components[name])

    profile = _profile_rows(p)
    max_total = max(map_points, key=lambda point: point["total_kPa"])
    min_total = min(map_points, key=lambda point: point["total_kPa"])
    max_ratio = max(map_points, key=lambda point: point["ratio"])
    min_ratio = min(map_points, key=lambda point: point["ratio"])

    return {
        "inputs": p,
        "units": {"stress": "kPa", "length": "m", "load": "kN", "unit_weight": "kN/m³"},
        "initial_at_group_plane": initial,
        "geometry": {
            "fill_pressure_kPa": q_fill,
            "excavation_radius_m": excavation_radius,
            "excavation_volume_m3": excavation_volume,
            "ring_inner_radius_m": ring_inner,
            "ring_outer_radius_m": ring_outer,
            "ring_area_m2": ring_area,
            "ring_height_m": ring_height,
            "excavation_pressure_kPa": q_excavation,
            "ring_pressure_kPa": q_ring,
            "excavation_vertical_distance_m": excavation_z,
        },
        "grid": {"x_m": xs, "y_m": ys, "dx_m": dx, "dy_m": dy, "x_max_m": GRID_X_MAX_M, "y_max_m": GRID_Y_MAX_M},
        "maps": map_values,
        "map_points": map_points,
        "profile": profile,
        "summary": {
            "max_total": max_total, "min_total": min_total,
            "max_ratio": max_ratio, "min_ratio": min_ratio,
        },
        "assumptions": [
            "Estratos horizontais, peso específico constante por camada e tensão vertical inicial calculada antes dos carregamentos.",
            "Poropressão hidrostática abaixo do N.A.; γw = 9,81 kN/m³ é um valor adotado/editável, não especificado numericamente pelo professor.",
            "Aterro extenso interpretado como faixa infinita em y entre x=5 m e x=15 m, conforme as Figuras/capturas.",
            "A escavação atua como alívio uniforme na base (cota −1 m); o solo removido forma o anel por conservação de volume.",
            "Boussinesq e superposição assumem meio elástico, homogêneo, isotrópico e semi-infinito para os acréscimos de tensão.",
            "Não há critério fornecido para declarar ruptura, estabilidade ou aceitação de segurança.",
        ],
    }
