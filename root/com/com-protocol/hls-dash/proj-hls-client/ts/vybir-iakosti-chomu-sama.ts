const SAFETY = 0.8;        // беремо копію, що просить не більше 80% від виміряного
const UP_BUFFER = 20;      // угору — лише коли в буфері вже стільки секунд
const DOWN_BUFFER = 8;     // нижче цього падаємо негайно, хай яка гарна швидкість

function choose(vars: Variant[], level: number, mbps: number, buffered: number): number {
  const bps = mbps * 1e6;

  // Униз — без умов і одразу на скільки треба: порожній буфер це вже зупинка показу.
  if (buffered < DOWN_BUFFER || vars[level].bandwidth > bps) {
    let i = level;
    while (i > 0 && vars[i].bandwidth > bps * SAFETY) i--;
    return i;
  }

  // Угору — на один щабель і з подвійним дозволом: і швидкість із запасом, і буфер.
  const up = level + 1;
  if (up < vars.length && buffered >= UP_BUFFER && vars[up].bandwidth <= bps * SAFETY)
    return up;

  return level;
}
