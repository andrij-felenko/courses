function gcd(a: number, b: number): number {
  a = Math.abs(a);
  b = Math.abs(b);
  while (b !== 0) {
    [a, b] = [b, a % b];
  }
  return a;
}

// Класика фронтенду — звести співвідношення сторін до нескоротного:
const g = gcd(1920, 1080);          // 120
const ratio = `${1920 / g}:${1080 / g}`;   // "16:9"
