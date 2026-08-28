/** Усі нащадки тайла — від нього самого до рівня maxZ включно. */
export function* descendants(root: TileId, maxZ: number): Generator<TileId> {
  const stack: TileId[] = [root];
  while (stack.length > 0) {
    const cur = stack.pop()!;
    yield cur;
    if (cur.z >= maxZ) continue;
    const z = cur.z + 1, x = cur.x * 2, y = cur.y * 2;
    stack.push({ z, x, y }, { z, x: x + 1, y }, { z, x, y: y + 1 }, { z, x: x + 1, y: y + 1 });
  }
}

/** Скільки тайлів це буде. Викликати ПЕРЕД завантаженням. */
export function descendantCount(fromZ: number, toZ: number, seeds: number): number {
  if (toZ < fromZ) return 0;
  const d = toZ - fromZ;
  return seeds * ((4 ** (d + 1) - 1) / 3);       // 1 + 4 + … + 4ᵈ
}
