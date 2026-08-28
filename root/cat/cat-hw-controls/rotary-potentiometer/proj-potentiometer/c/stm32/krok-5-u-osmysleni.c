// Та сама пропорція, тільки написана руками: map() поза Arduino нема.
static int scale(int v, int inLo, int inHi, int outLo, int outHi) {
  return (v - inLo) * (outHi - outLo) / (inHi - inLo) + outLo;
}

int bright   = scale(raw, calMin, calMax, 0, 255);   // у регістр порівняння таймера (ARR = 255)
int tempC    = scale(raw, calMin, calMax, 20, 80);   // у температуру уставки 20..80 °C
int periodMs = scale(raw, calMin, calMax, 50, 2000); // у затримку миготіння 50..2000 мс
int inverted = scale(raw, calMin, calMax, 100, 0);   // ОБЕРНЕНО: вправо → менше значення

__HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, bright);         // CCR1 і є яскравість
