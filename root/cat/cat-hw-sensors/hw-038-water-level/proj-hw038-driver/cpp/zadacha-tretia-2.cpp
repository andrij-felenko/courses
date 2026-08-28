int rawToLevel(int raw) {
  // нижче першої точки — вважаємо мінімальним рівнем
  if (raw <= calTable[0].raw)        return calTable[0].level;
  // вище останньої — максимальним
  if (raw >= calTable[CAL_N - 1].raw) return calTable[CAL_N - 1].level;

  // шукаємо відрізок [i, i+1], у який потрапив raw
  for (uint8_t i = 0; i < CAL_N - 1; i++) {
    int r0 = calTable[i].raw,     r1 = calTable[i + 1].raw;
    if (raw >= r0 && raw <= r1) {
      int l0 = calTable[i].level, l1 = calTable[i + 1].level;
      // лінійна інтерполяція ВСЕРЕДИНІ відрізка (множимо ПЕРШИМ!)
      return l0 + (long)(raw - r0) * (l1 - l0) / (r1 - r0);
    }
  }
  return calTable[CAL_N - 1].level;  // недосяжно, але хай компілятор спокійний
}
