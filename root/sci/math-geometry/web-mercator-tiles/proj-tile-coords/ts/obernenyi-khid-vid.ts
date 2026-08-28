export const MAX_LAT = 85.0511287798;   // широта зрізу: там висота карти = ширині
export const TILE = 256;                // сторона тайла в пікселях

export interface LatLon { lat: number; lon: number; }
export interface BBox { north: number; south: number; west: number; east: number; }

/** Дробові тайлові координати рівня z -> широта/довгота. */
export function tileToLatLon(fx: number, fy: number, z: number): LatLon {
  const n = 2 ** z;
  const lon = (fx / n) * 360 - 180;              // горизонталь лінійна
  const ym = (0.5 - fy / n) * 2 * Math.PI;       // назад у меркаторові одиниці
  return { lat: (Math.atan(Math.sinh(ym)) * 180) / Math.PI, lon };
}

/** Тайл (z,x,y) плюс піксель усередині нього -> градуси. */
export function pixelToLatLon(x: number, y: number, px: number, py: number, z: number): LatLon {
  return tileToLatLon(x + px / TILE, y + py / TILE, z);
}

/** Географічні межі тайла: NW-кут і SE-кут. */
export function tileBounds(x: number, y: number, z: number): BBox {
  const nw = tileToLatLon(x, y, z);
  const se = tileToLatLon(x + 1, y + 1, z);
  return { north: nw.lat, west: nw.lon, south: se.lat, east: se.lon };
}
