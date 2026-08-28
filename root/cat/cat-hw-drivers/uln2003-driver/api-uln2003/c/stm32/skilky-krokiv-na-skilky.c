#define HALFSTEPS_PER_REV 4076   // півкроків на оберт вала (≈ 64 · 63.684)

// Зробити steps півкроків. dir = +1 вперед, -1 назад.
static void move_steps(int32_t steps, int8_t dir) {
  for (int32_t i = 0; i < steps; i++) {
    if (dir > 0) idx = (idx + 1) % 8;
    else         idx = (idx + 7) % 8;
    apply_step(idx);
    HAL_Delay(2);
  }
}

// Приклад: рівно один оберт вперед, тоді півоберту назад
static void demo(void) {
  move_steps(HALFSTEPS_PER_REV, +1);       // 360°
  move_steps(HALFSTEPS_PER_REV / 2, -1);   // 180° назад
}
