export interface TileId { z: number; x: number; y: number; }

/** Довгота -> дробова тайлова X. НЕ обрізається: значення може вийти за [0,n). */
function lonToX(lonDeg: number, z: number): number {
  return ((lonDeg + 180) / 360) * 2 ** z;
}

/** Широта -> дробова тайлова Y. Зріз до ±MAX_LAT ОБОВ'ЯЗКОВИЙ перед asinh/log. */
function latToY(latDeg: number, z: number): number {
  const lat = Math.min(MAX_LAT, Math.max(-MAX_LAT, latDeg));
  const ym = Math.asinh(Math.tan((lat * Math.PI) / 180));   // = ln tan(π/4 + φ/2)
  return (0.5 - ym / (2 * Math.PI)) * 2 ** z;
}

/** Усі тайли рівня z, що накривають прямокутник. Коректно через 180-й меридіан. */
export function tilesForBBox(b: BBox, z: number): TileId[] {
  const n = 2 ** z;

  // y: обрізаємо — полюсів на карті немає, склеювати нема чого
  const yTop = Math.max(0, Math.floor(latToY(b.north, z)));
  const yBot = Math.min(n - 1, Math.floor(latToY(b.south, z)));

  // x: ширину рахуємо в ДРОБОВИХ координатах, до floor
  const fLeft = lonToX(b.west, z);
  let fRight = lonToX(b.east, z);
  if (fRight < fLeft) fRight += n;                 // прямокутник перетнув шов
  const xLeft = Math.floor(fLeft);
  const spanX = Math.min(n, Math.floor(fRight) - xLeft + 1);

  const out: TileId[] = [];
  for (let y = yTop; y <= yBot; y++) {
    for (let i = 0; i < spanX; i++) {
      out.push({ z, x: (((xLeft + i) % n) + n) % n, y });   // циклічність по x
    }
  }
  return out;
}
