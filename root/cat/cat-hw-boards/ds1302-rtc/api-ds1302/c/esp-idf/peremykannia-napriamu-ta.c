// DAT сконфігуровано один раз (gpio_config), а напрям міняємо просто на льоту.

// ── Один регістр: запис ──
static void ds_write(uint8_t cmd, uint8_t data) {
  gpio_set_level(PIN_RST, 0);
  gpio_set_level(PIN_CLK, 0);
  gpio_set_direction(PIN_DAT, GPIO_MODE_OUTPUT);
  gpio_set_level(PIN_RST, 1);                    // почали сеанс

  shift_out_byte(cmd);                           // командний байт (біт0 = 0, запис)
  shift_out_byte(data);                          // байт даних

  gpio_set_level(PIN_RST, 0);                    // завершили — дані зафіксовано
}

// ── Один регістр: читання ──
static uint8_t ds_read(uint8_t cmd) {
  gpio_set_level(PIN_RST, 0);
  gpio_set_level(PIN_CLK, 0);
  gpio_set_direction(PIN_DAT, GPIO_MODE_OUTPUT);
  gpio_set_level(PIN_RST, 1);                    // почали сеанс

  shift_out_byte(cmd | 0x01);                    // командний байт із бітом ЧИТАННЯ
  gpio_set_direction(PIN_DAT, GPIO_MODE_INPUT);  // ← віддаємо лінію мікросхемі
  uint8_t data = shift_in_byte();                // забрали байт

  gpio_set_level(PIN_RST, 0);                    // завершили сеанс
  return data;
}
