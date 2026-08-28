type Shape =
  | { kind: "circle"; r: number }
  | { kind: "rect"; w: number; h: number }
  | { kind: "triangle"; b: number; h: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle":   return 3.14159265 * s.r * s.r;
    case "rect":     return s.w * s.h;
    case "triangle": return 0.5 * s.b * s.h;
    default: {
      const _exhaustive: never = s;   // додав новий вид — тип «звузиться» не до never,
      return _exhaustive;             // і компілятор укаже саме цей switch
    }
  }
}
