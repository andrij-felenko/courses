const uint8_t PIN_POT = A0;
const uint8_t SHIFT   = 4;           // α = 1/2^SHIFT = 1/16 ≈ 0.0625 (сильне згладжування)

long emaScaled;                      // оцінка, збережена в масштабі ×2^SHIFT

void emaBegin() {
  emaScaled = (long)analogRead(PIN_POT) << SHIFT;   // старт із першого відліку
}

int emaRead() {
  int  raw   = analogRead(PIN_POT);
  long delta = ((long)raw << SHIFT) - emaScaled;    // розбіжність у масштабі ×2^SHIFT
  emaScaled += (delta >> SHIFT);                    // крок α·delta, бо >>SHIFT = ділення на 2^SHIFT
  return (int)((emaScaled + (1 << (SHIFT - 1))) >> SHIFT);  // реальний масштаб, з округленням
}
