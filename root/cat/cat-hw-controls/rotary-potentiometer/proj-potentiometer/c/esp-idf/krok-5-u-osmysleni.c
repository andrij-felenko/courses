// Та сама пропорція, тільки написана руками: map() поза Arduino нема.
static int scale(int v, int inLo, int inHi, int outLo, int outHi) {
  return (v - inLo) * (outHi - outLo) / (inHi - inLo) + outLo;
}

int bright   = scale(raw, calMin, calMax, 0, 255);   // у заповнення LEDC 0..255 (8 біт)
int tempC    = scale(raw, calMin, calMax, 20, 80);   // у температуру уставки 20..80 °C
int periodMs = scale(raw, calMin, calMax, 50, 2000); // у затримку миготіння 50..2000 мс
int inverted = scale(raw, calMin, calMax, 100, 0);   // ОБЕРНЕНО: вправо → менше значення

ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, bright);   // віддати яскравість у ШІМ
ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
