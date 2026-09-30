const test = require('node:test');
const assert = require('node:assert/strict');
require('../static/calculation.js');
const model = globalThis.GeotechCalculation;

test('valores padrão e balanço de tensões na cota −4 m', () => {
  const result = model.simulate({});
  assert.equal(result.initial_at_group_plane.sigma_v_kPa, 74.7);
  assert.equal(result.initial_at_group_plane.u_kPa, 9.81);
  assert.equal(result.initial_at_group_plane.sigma_eff_kPa, 64.89);
  assert.ok(Math.abs(result.initial_at_group_plane.sigma_eff_kPa - (result.initial_at_group_plane.sigma_v_kPa - result.initial_at_group_plane.u_kPa)) < 1e-12);
});

test('perfil local finito inclui nível d’água e interfaces estratigráficas', () => {
  const result = model.simulate({});
  assert.equal(result.profile.length, 61);
  for (const elevation of [0, -3, -8, -12, -14]) assert.ok(result.profile.some(row => row.elevation_m === elevation));
  for (const row of result.profile) for (const key of ['sigma_v_kPa', 'u_kPa', 'sigma_eff_kPa']) assert.ok(Number.isFinite(row[key]));
});

test('γsat da argila mole só influencia o perfil a partir da interface −8 m', () => {
  const base = model.simulate({});
  const changed = model.simulate({ gamma_soft_clay_sat_kN_m3: '15,32' });
  const shallow = base.profile.findIndex(row => row.elevation_m === -8);
  assert.equal(base.initial_at_group_plane.sigma_eff_kPa, changed.initial_at_group_plane.sigma_eff_kPa);
  assert.notEqual(base.profile.at(-1).sigma_v_kPa, changed.profile.at(-1).sigma_v_kPa);
  assert.equal(base.profile[shallow].sigma_v_kPa, changed.profile[shallow].sigma_v_kPa);
});

test('nível d’água altera poropressão e tensão efetiva', () => {
  const base = model.simulate({});
  const changed = model.simulate({ water_table_elevation_m: -2 });
  assert.notEqual(base.initial_at_group_plane.u_kPa, changed.initial_at_group_plane.u_kPa);
  assert.notEqual(base.initial_at_group_plane.sigma_eff_kPa, changed.initial_at_group_plane.sigma_eff_kPa);
});

test('carga da torre altera mapa de carregamentos sem alterar perfil geostático', () => {
  const base = model.simulate({});
  const changed = model.simulate({ tower_load_kN: 5500 });
  assert.equal(base.profile[30].sigma_v_kPa, changed.profile[30].sigma_v_kPa);
  assert.notEqual(base.maps.total[0][0], changed.maps.total[0][0]);
});

test('geometria do carregamento modifica o mapa e os dados exportáveis', () => {
  const base = model.simulate({});
  const changed = model.simulate({ fill_x_max_m: 17 });
  assert.notEqual(base.maps.fill[0][0], changed.maps.fill[0][0]);
  assert.ok(base.map_points.length > 0);
  assert.ok(base.summary.max_total.total_kPa > 0);
});

test('cotas negativas decimais e vírgula decimal são aceitas', () => {
  const result = model.simulate({ group_elevation_m: '-4', water_table_elevation_m: '-3', gamma_soft_clay_sat_kN_m3: '15,32' });
  assert.equal(result.inputs.group_elevation_m, -4);
  assert.equal(result.inputs.gamma_soft_clay_sat_kN_m3, 15.32);
});
