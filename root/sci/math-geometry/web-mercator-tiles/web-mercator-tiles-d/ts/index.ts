const MAX_LAT = 85.0511287798;   // широта зрізу: там висота карти = ширині
const TILE = 256;                // сторона тайла в пікселях

interface TilePos { x: number; y: number; px: number; py: number; }

/** Географічні координати -> тайл рівня z і піксель усередині нього. */
function latLonToTile(latDeg: number, lonDeg: number, z: number): TilePos {
  const lat = Math.max(-MAX_LAT, Math.min(MAX_LAT, latDeg));  // зріз полярних шапок
  const phi = (lat * Math.PI) / 180;

  const xn = (lonDeg + 180) / 360;                            // довгота лінійна
  const ym = Math.log(Math.tan(Math.PI / 4 + phi / 2));       // інтеграл секанса
  const yn = 0.5 - ym / (2 * Math.PI);                        // мінус: північ угорі

  const n = 2 ** z;
  const fx = xn * n;
  const fy = yn * n;
  return {
    x: Math.floor(fx),
    y: Math.floor(fy),
    px: (fx - Math.floor(fx)) * TILE,
    py: (fy - Math.floor(fy)) * TILE,
  };
}

/** Скільки метрів землі в пікселі на цій широті й цьому рівні. */
function resolution(latDeg: number, z: number): number {
  const EQUATOR = 2 * Math.PI * 6378137;                      // 40 075 016.686 м
  return (EQUATOR * Math.cos((latDeg * Math.PI) / 180)) / (TILE * 2 ** z);
}
