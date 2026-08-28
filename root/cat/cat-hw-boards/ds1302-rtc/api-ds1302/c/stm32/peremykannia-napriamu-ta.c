/* На STM32 напрям ніжки міняється переініціалізацією: та сама структура,
   інше поле Mode. Це дорожче за один регістровий запис, але чесно й наочно. */
static void dat_dir(uint32_t mode) {      /* GPIO_MODE_OUTPUT_PP або GPIO_MODE_INPUT */
  GPIO_InitTypeDef g = {0};
  g.Pin   = DAT_PIN;
  g.Mode  = mode;
  g.Pull  = GPIO_NOPULL;
  g.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(DAT_PORT, &g);
}

/* ── Один регістр: запис ── */
static void ds_write(uint8_t cmd, uint8_t data) {
  HAL_GPIO_WritePin(RST_PORT, RST_PIN, GPIO_PIN_RESET);
  HAL_GPIO_WritePin(CLK_PORT, CLK_PIN, GPIO_PIN_RESET);
  dat_dir(GPIO_MODE_OUTPUT_PP);
  HAL_GPIO_WritePin(RST_PORT, RST_PIN, GPIO_PIN_SET);   /* почали сеанс */

  shift_out_byte(cmd);                                  /* біт0 = 0, запис */
  shift_out_byte(data);

  HAL_GPIO_WritePin(RST_PORT, RST_PIN, GPIO_PIN_RESET); /* дані зафіксовано */
}

/* ── Один регістр: читання ── */
static uint8_t ds_read(uint8_t cmd) {
  HAL_GPIO_WritePin(RST_PORT, RST_PIN, GPIO_PIN_RESET);
  HAL_GPIO_WritePin(CLK_PORT, CLK_PIN, GPIO_PIN_RESET);
  dat_dir(GPIO_MODE_OUTPUT_PP);
  HAL_GPIO_WritePin(RST_PORT, RST_PIN, GPIO_PIN_SET);

  shift_out_byte(cmd | 0x01);                           /* біт0 = 1, читання */
  dat_dir(GPIO_MODE_INPUT);                             /* ← лінія за мікросхемою */
  uint8_t data = shift_in_byte();

  HAL_GPIO_WritePin(RST_PORT, RST_PIN, GPIO_PIN_RESET);
  return data;
}
