#define WIN 16                       // розмір вікна усереднення (степінь 2 — зручно)

extern ADC_HandleTypeDef hadc1;
static int      buf[WIN];            // кільцевий буфер останніх відліків
static uint8_t  idx = 0;             // куди писати наступний відлік
static long     sum = 0;             // поточна сума вмісту буфера

static int potSample(void) {         // єдине місце, що знає про платформу
  HAL_ADC_Start(&hadc1);
  HAL_ADC_PollForConversion(&hadc1, 10);
  int v = (int)HAL_ADC_GetValue(&hadc1);
  HAL_ADC_Stop(&hadc1);
  return v;
}

void pot_begin(void) {
  int first = potSample();
  for (int i = 0; i < WIN; i++) { buf[i] = first; sum += first; }  // старт без «розгону»
}

int pot_read_averaged(void) {
  sum -= buf[idx];                   // прибрати найстаріший відлік із суми
  int fresh = potSample();
  buf[idx] = fresh;                  // записати найновіший на його місце
  sum += fresh;                      // додати до суми
  idx = (idx + 1) % WIN;             // індекс по колу
  return (int)(sum / WIN);           // середнє = сума / кількість
}
