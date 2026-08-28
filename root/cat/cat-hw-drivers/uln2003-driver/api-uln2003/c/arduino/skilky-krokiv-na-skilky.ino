const long HALFSTEPS_PER_REV = 4076;   // півкроків на оберт вала (≈ 64 · 63.684)

// Зробити steps півкроків. dir = +1 вперед, -1 назад.
void moveSteps(long steps, int dir) {
  for (long i = 0; i < steps; i++) {
    if (dir > 0) idx = (idx + 1) % 8;
    else         idx = (idx + 7) % 8;
    applyStep(idx);
    delay(2);
  }
}

// Приклад: рівно один оберт вперед, тоді півоберту назад
void demo() {
  moveSteps(HALFSTEPS_PER_REV, +1);       // 360°
  moveSteps(HALFSTEPS_PER_REV / 2, -1);   // 180° назад
}
