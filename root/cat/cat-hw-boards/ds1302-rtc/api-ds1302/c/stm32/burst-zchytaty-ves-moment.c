/* Той самий burst: один сеанс, вісім байтів, розкодування те саме. */
static void ds_read_burst(struct Clock *c) {
  HAL_GPIO_WritePin(RST_PORT, RST_PIN, GPIO_PIN_RESET);
  HAL_GPIO_WritePin(CLK_PORT, CLK_PIN, GPIO_PIN_RESET);
  dat_dir(GPIO_MODE_OUTPUT_PP);
  HAL_GPIO_WritePin(RST_PORT, RST_PIN, GPIO_PIN_SET);

  shift_out_byte(0xBF);                 /* clock-burst READ */
  dat_dir(GPIO_MODE_INPUT);             /* лінія за мікросхемою на всі 8 байтів */

  uint8_t raw[8];
  for (int i = 0; i < 8; i++) raw[i] = shift_in_byte();

  HAL_GPIO_WritePin(RST_PORT, RST_PIN, GPIO_PIN_RESET);

  c->sec   = bcd_to_dec(raw[0] & 0x7F); /* маскуємо CH (біт7) */
  c->min   = bcd_to_dec(raw[1] & 0x7F);
  c->hour  = bcd_to_dec(raw[2] & 0x3F); /* 24-год: біти 0..5 */
  c->date  = bcd_to_dec(raw[3] & 0x3F);
  c->month = bcd_to_dec(raw[4] & 0x1F);
  c->dow   = bcd_to_dec(raw[5] & 0x07);
  c->year  = bcd_to_dec(raw[6]);
}
