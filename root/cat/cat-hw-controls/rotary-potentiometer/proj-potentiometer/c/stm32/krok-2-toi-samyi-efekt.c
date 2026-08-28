#define SHIFT 4                      // α = 1/2^SHIFT = 1/16 ≈ 0.0625 (сильне згладжування)

extern ADC_HandleTypeDef hadc1;
static long emaScaled;               // оцінка, збережена в масштабі ×2^SHIFT

static int potSample(void) {
  HAL_ADC_Start(&hadc1);
  HAL_ADC_PollForConversion(&hadc1, 10);
  int v = (int)HAL_ADC_GetValue(&hadc1);
  HAL_ADC_Stop(&hadc1);
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
