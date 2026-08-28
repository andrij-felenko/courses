const N = 10_000;                 // параметр квантування
const L_LAT = 111229.064;         // м на градус широти  @50°
const L_LON = 71695.754;          // м на градус довготи @50°

const pts: [number, number][] = [
  [30.523400, 50.450100], [30.524150, 50.450620], [30.525900, 50.451080],
  [30.527310, 50.450940], [30.528000, 50.452250],
];
const [x0, x1, y0, y1] = [30.2, 30.8, 50.2, 50.6];   // обмежувальний прямокутник

const kx = (N - 1) / (x1 - x0), ky = (N - 1) / (y1 - y0);
const transform = { scale: [1 / kx, 1 / ky], translate: [x0, y0] };
const [qx, qy] = transform.scale;
console.log(`q_x = ${qx.toFixed(10)}° = ${(qx * L_LON).toFixed(4)} м   ` +
            `q_y = ${qy.toFixed(10)}° = ${(qy * L_LAT).toFixed(4)} м`);

// 1. на цілочислову сітку
const idx = pts.map(([x, y]) => [Math.round((x - x0) * kx), Math.round((y - y0) * ky)]);

// 2. різниці — цілі
const deltas = idx.map((p, k) => k === 0 ? p : [p[0] - idx[k-1][0], p[1] - idx[k-1][1]]);

// 3. відновлення — часткові суми
const sgn = (v: number, d = 0) => (v >= 0 ? "+" : "") + v.toFixed(d);
let ax = 0, ay = 0, mx = 0, my = 0;
deltas.forEach(([dx, dy], k) => {
  ax += dx; ay += dy;
  const ex = (ax * qx + x0 - pts[k][0]) * L_LON;
  const ey = (ay * qy + y0 - pts[k][1]) * L_LAT;
  mx = Math.max(mx, Math.abs(ex)); my = Math.max(my, Math.abs(ey));
  console.log(`  k=${k}  Δ=(${sgn(dx)},${sgn(dy)})  індекс=(${ax},${ay})  ` +
              `похибка=(${sgn(ex, 3)}, ${sgn(ey, 3)}) м`);
});
console.log(`макс |Δx| = ${mx.toFixed(3)} м (межа ${(qx*L_LON/2).toFixed(3)})   ` +
            `макс |Δy| = ${my.toFixed(3)} м (межа ${(qy*L_LAT/2).toFixed(3)})`);
