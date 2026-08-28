#define SHIFT 4                      // α = 1/2^SHIFT = 1/16 ≈ 0.0625 (сильне згладжування)

static adc_oneshot_unit_handle_t adc1;   // блок ADC1, налаштований як вище
static long emaScaled;               // оцінка, збережена в масштабі ×2^SHIFT

static int potSample(void) {
  int v = 0;
  ESP_ERROR_CHECK(adc_oneshot_read(adc1, POT_CHAN, &v));
  return v;
}

void ema_begin(void) {
  emaScaled = (long)potSample() << SHIFT;           // старт із першого відліку
}

int ema_read(void) {
  long delta = ((long)potSample() << SHIFT) - emaScaled;   // розбіжність у масштабі ×2^SHIFT
  emaScaled += (delta >> SHIFT);                    // крок α·delta, бо >>SHIFT = ділення на 2^SHIFT
  return (int)((emaScaled + (1 << (SHIFT - 1))) >> SHIFT); // реальний масштаб, з округленням
}
