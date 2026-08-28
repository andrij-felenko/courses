#define WIN 16                       // розмір вікна усереднення (степінь 2 — зручно)

static adc_oneshot_unit_handle_t adc1;   // блок ADC1, налаштований як вище
static int     buf[WIN];             // кільцевий буфер останніх відліків
static uint8_t idx = 0;              // куди писати наступний відлік
static long    sum = 0;              // поточна сума вмісту буфера

static int potSample(void) {         // єдине місце, що знає про платформу
  int v = 0;
  ESP_ERROR_CHECK(adc_oneshot_read(adc1, POT_CHAN, &v));
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
