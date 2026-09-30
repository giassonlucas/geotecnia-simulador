/* Independent browser calculation engine. Units: kN, m, kPa, kN/m³. */
(function (root) {
  'use strict';
  const D = {
    group_elevation_m:-4, water_table_elevation_m:-3, gamma_water_kN_m3:9.81,
    gamma_sand_nat_kN_m3:18.5, gamma_sand_sat_kN_m3:19.2,
    gamma_soft_clay_sat_kN_m3:15.4, gamma_medium_clay_sat_kN_m3:19,
    tower_load_kN:5000, tower_x_m:18, tower_y_m:22,
    fill_height_m:3.8, fill_gamma_kN_m3:16.5, fill_x_min_m:5, fill_x_max_m:15,
    excavation_x_m:25, excavation_y_m:17, excavation_diameter_m:7,
    excavation_depth_m:1, ring_width_m:1, grid_step_m:1, contour_count:12
  };
  const P_LIMIT=14, X_MAX=45, Y_MAX=28;
  function num(v){if(typeof v==='string'){v=v.trim().replace(/\s/g,'');if(v.includes(',')&&v.includes('.'))throw Error('Use vírgula ou ponto como separador decimal, não ambos.');v=v.replace(',','.');}return Number(v);}
  function validate(raw){const p={...D};for(const k of Object.keys(D)){if(raw[k]!==undefined){if(raw[k]===null||String(raw[k]).trim()==='')throw Error(`O campo ${k} é obrigatório.`);p[k]=num(raw[k]);}if(!Number.isFinite(p[k]))throw Error(`O campo ${k} precisa conter um número finito.`);}
    for(const k of ['gamma_water_kN_m3','gamma_sand_nat_kN_m3','gamma_sand_sat_kN_m3','gamma_soft_clay_sat_kN_m3','gamma_medium_clay_sat_kN_m3','tower_load_kN','fill_height_m','fill_gamma_kN_m3','excavation_diameter_m','excavation_depth_m','ring_width_m'])if(p[k]<=0)throw Error(`${k} deve ser maior que zero.`);
    if(p.group_elevation_m < -14 || p.group_elevation_m > -1)throw Error('A cota do plano deve estar entre −14 m e −1 m.');
    if(p.water_table_elevation_m < -14 || p.water_table_elevation_m > 0)throw Error('A cota do N.A. deve estar entre −14 m e 0 m.');
    if(p.fill_x_max_m<=p.fill_x_min_m)throw Error('O limite x final do aterro deve ser maior que o limite inicial.');
    if(p.excavation_depth_m>=Math.abs(p.group_elevation_m))throw Error('O plano de cálculo precisa ficar estritamente abaixo da base da escavação.');
    if(p.grid_step_m<.25||p.grid_step_m>2.5)throw Error('O passo da malha deve estar entre 0,25 m e 2,5 m.');
    if(!Number.isInteger(p.contour_count)||p.contour_count<4||p.contour_count>30)throw Error('O número de níveis de contorno deve ser inteiro entre 4 e 30.');return p;}
  function initial(d,p){const water=-p.water_table_elevation_m,sand=Math.min(d,8),nat=Math.min(sand,water),sat=Math.max(0,sand-Math.max(0,water)),soft=Math.max(0,Math.min(d,12)-8),medium=Math.max(0,Math.min(d,14)-12),sv=nat*p.gamma_sand_nat_kN_m3+sat*p.gamma_sand_sat_kN_m3+soft*p.gamma_soft_clay_sat_kN_m3+medium*p.gamma_medium_clay_sat_kN_m3,u=Math.max(0,d-water)*p.gamma_water_kN_m3;return {sigma_v_kPa:sv,u_kPa:u,sigma_eff_kPa:sv-u};}
  function point(Q,r,z){return 3*Q*z**3/(2*Math.PI*(r*r+z*z)**2.5);}
  function prim(t){return Math.atan(t)+t/(1+t*t);}
  function strip(q,x,z,x0,x1){const a=(x1-x)/z,b=(x0-x)/z;return q/Math.PI*(prim(a)-prim(b));}
  function gauss(n){const x=Array(n).fill(0),w=Array(n).fill(0),half=Math.floor((n+1)/2);for(let i=0;i<half;i++){let z=Math.cos(Math.PI*(i+.75)/(n+.5)),der=0;for(let it=0;it<40;it++){let p0=1,p1=z;for(let k=2;k<=n;k++){const t=((2*k-1)*z*p1-(k-1)*p0)/k;p0=p1;p1=t;}const pn=n===1?z:p1,pnm=n===1?1:p0;der=n*(z*pn-pnm)/(z*z-1);const dz=pn/der;z-=dz;if(Math.abs(dz)<2e-15)break;}let p0=1,p1=z;for(let k=2;k<=n;k++){const t=((2*k-1)*z*p1-(k-1)*p0)/k;p0=p1;p1=t;}const pn=n===1?z:p1,pnm=n===1?1:p0;der=n*(z*pn-pnm)/(z*z-1);const wt=2/((1-z*z)*der*der);x[i]=-z;x[n-1-i]=z;w[i]=wt;w[n-1-i]=wt;}return [x,w];}
  const [RN,RW]=gauss(18),NT=64;
  function polar(cx,cy,ri,ro){const pts=[],mid=(ri+ro)/2,half=(ro-ri)/2,tw=2*Math.PI/NT;for(let i=0;i<RN.length;i++){const r=mid+half*RN[i],aw=RW[i]*half*r*tw;for(let j=0;j<NT;j++){const t=tw*j;pts.push([cx+r*Math.cos(t),cy+r*Math.sin(t),aw]);}}return pts;}
  function area(q,pts,x,y,z){const fac=3*q*z**3/(2*Math.PI),z2=z*z;let s=0;for(const [sx,sy,a] of pts){const rr=(x-sx)**2+(y-sy)**2;s+=a/(rr+z2)**2.5;}return fac*s;}
  function axis(max,step){const n=Math.max(1,Math.ceil(max/step)),dx=max/n;return [Array.from({length:n+1},(_,i)=>i*dx),dx];}
  function profile(p){const ds=new Set(Array.from({length:58},(_,i)=>i*P_LIMIT/57));[0,-p.water_table_elevation_m,8,12,14].forEach(d=>{if(d>=0&&d<=14)ds.add(d);});return [...ds].sort((a,b)=>a-b).map(d=>({depth_m:d,elevation_m:-d,...initial(d,p)}));}
  function simulate(raw){const p=validate(raw),depth=-p.group_elevation_m,ini=initial(depth,p);if(ini.sigma_eff_kPa<=0)throw Error('A tensão efetiva inicial no plano precisa ser positiva.');const [xs,dx]=axis(X_MAX,p.grid_step_m),[ys,dy]=axis(Y_MAX,p.grid_step_m),qfill=p.fill_height_m*p.fill_gamma_kN_m3,rad=p.excavation_diameter_m/2,rout=rad+p.ring_width_m,vol=Math.PI*rad**2*p.excavation_depth_m,ringArea=Math.PI*(rout**2-rad**2),ringH=vol/ringArea,qexc=-p.gamma_sand_nat_kN_m3*p.excavation_depth_m,qring=p.gamma_sand_nat_kN_m3*ringH,zexc=depth-p.excavation_depth_m;
    const disk=polar(p.excavation_x_m,p.excavation_y_m,0,rad),ring=polar(p.excavation_x_m,p.excavation_y_m,rad,rout),names=['tower','fill','excavation','ring','total','ratio'],maps=Object.fromEntries(names.map(k=>[k,[]])),points=[];
    for(const y of ys){const rows=Object.fromEntries(names.map(k=>[k,[]]));for(const x of xs){const st=point(p.tower_load_kN,Math.hypot(x-p.tower_x_m,y-p.tower_y_m),depth),sf=strip(qfill,x,depth,p.fill_x_min_m,p.fill_x_max_m),se=area(qexc,disk,x,y,zexc),sr=area(qring,ring,x,y,depth),total=st+sf+se+sr,ratio=total/ini.sigma_eff_kPa;for(const [k,v] of [['tower',st],['fill',sf],['excavation',se],['ring',sr],['total',total],['ratio',ratio]])rows[k].push(v);points.push({x_m:x,y_m:y,tower_kPa:st,fill_kPa:sf,excavation_kPa:se,ring_kPa:sr,total_kPa:total,ratio,ratio_percent:100*ratio});}for(const k of names)maps[k].push(rows[k]);}
    const pick=k=>points.reduce((a,b)=>b[k]<a[k]?b:a),high=k=>points.reduce((a,b)=>b[k]>a[k]?b:a),ratioP=pt=>({...pt,ratio_percent:pt.ratio*100});
    return {inputs:p,units:{stress:'kPa',length:'m',load:'kN',unit_weight:'kN/m³'},initial_at_group_plane:ini,geometry:{fill_pressure_kPa:qfill,excavation_radius_m:rad,excavation_volume_m3:vol,ring_inner_radius_m:rad,ring_outer_radius_m:rout,ring_area_m2:ringArea,ring_height_m:ringH,excavation_pressure_kPa:qexc,ring_pressure_kPa:qring,excavation_vertical_distance_m:zexc},grid:{x_m:xs,y_m:ys,dx_m:dx,dy_m:dy,x_max_m:X_MAX,y_max_m:Y_MAX},maps,profile:profile(p),map_points:points,summary:{max_total:high('total_kPa'),min_total:pick('total_kPa'),max_ratio:ratioP(high('ratio')),min_ratio:ratioP(pick('ratio'))},assumptions:['Estratos horizontais, peso específico constante por camada e tensão vertical inicial calculada antes dos carregamentos.','Poropressão hidrostática abaixo do N.A.; γw = 9,81 kN/m³ é um valor adotado/editável, não especificado numericamente pelo professor.','Aterro extenso interpretado como faixa infinita em y entre x=5 m e x=15 m, conforme as Figuras/capturas.','A escavação atua como alívio uniforme na base (cota −1 m); o solo removido forma o anel por conservação de volume.','Boussinesq e superposição assumem meio elástico, homogêneo, isotrópico e semi-infinito para os acréscimos de tensão.','Não há critério fornecido para declarar ruptura, estabilidade ou aceitação de segurança.']};}
  root.GeotechCalculation={defaults:D,validate,simulate};
})(typeof self!=='undefined'?self:globalThis);
