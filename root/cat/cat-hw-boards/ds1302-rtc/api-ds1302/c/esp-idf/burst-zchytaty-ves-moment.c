// Той самий burst: один сеанс, вісім байтів, розкодування те саме.
static void ds_read_burst(struct Clock *c) {
  gpio_set_level(PIN_RST, 0);
  gpio_set_level(PIN_CLK, 0);
  gpio_set_direction(PIN_DAT, GPIO_MODE_OUTPUT);
  gpio_set_level(PIN_RST, 1);

  shift_out_byte(0xBF);                          // clock-burst READ
  gpio_set_direction(PIN_DAT, GPIO_MODE_INPUT);  // лінія за мікросхемою на всі 8 байтів

  uint8_t raw[8];
  for (int i = 0; i < 8; i++) raw[i] = shift_in_byte();

  gpio_set_level(PIN_RST, 0);

  c->sec   = bcd_to_dec(raw[0] & 0x7F);          // маскуємо CH (біт7)
  c->min   = bcd_to_dec(raw[1] & 0x7F);
  c->hour  = bcd_to_dec(raw[2] & 0x3F);          // 24-год: біти 0..5
  c->date  = bcd_to_dec(raw[3] & 0x3F);
  c->month = bcd_to_dec(raw[4] & 0x1F);
  c->dow   = bcd_to_dec(raw[5] & 0x07);
  c->year  = bcd_to_dec(raw[6]);
}
