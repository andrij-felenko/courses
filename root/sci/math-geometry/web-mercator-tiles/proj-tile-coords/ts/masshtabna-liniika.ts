const EQUATOR = 2 * Math.PI * 6378137;          // 40 075 016.686 м

/** Метрів землі в одному пікселі екрана на цій широті й цьому рівні. */
export function resolution(latDeg: number, z: number): number {
  return (EQUATOR * Math.cos((latDeg * Math.PI) / 180)) / (TILE * 2 ** z);
}

export interface ScaleBar { metres: number; pixels: number; label: string; }

/** Найбільша «кругла» відстань (ряд 1-2-5), що вміщується в maxPx пікселів. */
export function scaleBar(latDeg: number, z: number, maxPx = 120): ScaleBar {
  const mPerPx = resolution(latDeg, z);
  const raw = mPerPx * maxPx;
  const pow = 10 ** Math.floor(Math.log10(raw));
  const nice = [5, 2, 1].find((c) => raw >= c * pow)! * pow;
  return {
    metres: nice,
    pixels: nice / mPerPx,
    label: nice >= 1000 ? `${nice / 1000} км` : `${nice} м`,
  };
}
