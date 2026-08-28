#define SPEED 300.0   // півкроків/с; напрям задає dir

static void spin_task(void *arg) {
  const uint32_t period_us = (uint32_t)(1e6 / SPEED);
  for (;;) {
    idx = (idx + dir + 8) % 8;
    apply_step(idx);
    esp_rom_delay_us(period_us);   // рівний темп, БЕЗ розгону/гальмування
  }
}
